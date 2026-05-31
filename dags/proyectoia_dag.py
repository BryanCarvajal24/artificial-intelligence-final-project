from datetime import datetime, timedelta

import sys

sys.path.append("/opt/airflow/src")
sys.path.append("/opt/airflow/spark")


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


from bronze.extract_s3_data import extract_s3_data
from bronze.load_postgres_bronze import load_postgres_bronze


from silver_customers import run_silver_customers
from silver_accounts import run_silver_accounts
from silver_transactions import run_silver_transactions
from silver_loans import run_silver_loans


default_args = {
    "owner": "qversity",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    "qversity_fintech_pipeline",
    default_args=default_args,
    description="Fintech ELT Pipeline",
    schedule_interval=None,
    catchup=False,
    tags=["bronze", "silver", "gold"],
)


# BRONZE PIPELINE

def bronze_pipeline():

    data = extract_s3_data()

    load_postgres_bronze(data)


# SILVER PYSPARK PIPELINE

def silver_pyspark_staging():

    spark, bronze_df2, jdbc_url, properties = run_silver_customers()

    run_silver_accounts(
        bronze_df2,
        jdbc_url,
        properties
    )

    run_silver_transactions(
        bronze_df2,
        jdbc_url,
        properties
    )

    run_silver_loans(
        bronze_df2,
        jdbc_url,
        properties
    )

    spark.stop()

    print("Spark session stopped.")


# TASKS

bronze_task = PythonOperator(
    task_id="bronze_ingestion",
    python_callable=bronze_pipeline,
    dag=dag,
)


silver_pyspark_task = PythonOperator(
    task_id="silver_pyspark_staging",
    python_callable=silver_pyspark_staging,
    dag=dag,
)


silver_dbt_task = BashOperator(
    task_id="silver_dbt_cleaning_modeling",
    bash_command="""
    cd /opt/airflow/dbt &&
    export DBT_PROFILES_DIR=/opt/airflow/dbt &&
    dbt run --select silver &&
    dbt test --select silver
    """,
    dag=dag,
)


gold_dbt_task = BashOperator(
    task_id="gold_business_analytics",
    bash_command="""
    cd /opt/airflow/dbt &&
    export DBT_PROFILES_DIR=/opt/airflow/dbt &&
    dbt run --select gold &&
    dbt test --select gold
    """,
    dag=dag,
)


# PIPELINE ORDER

bronze_task >> silver_pyspark_task >> silver_dbt_task >> gold_dbt_task
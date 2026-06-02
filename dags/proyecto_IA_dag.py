from datetime import datetime, timedelta

import sys

sys.path.append("/opt/airflow/src")

from airflow import DAG
from airflow.operators.python import PythonOperator

from extract_api_data_purpleair import (
    extract_purpleair_history
)

from extract_api_data_ambient_weather import (
    extract_api_data,
    save_raw_data,
    load_to_bronze
)

from transform_api_data import (
    transform_api_data
)

from merge_pm10_api_data import (
    merge_pm10_data
)

from load_historical_data import (
    read_historical_data,
    load_to_silver
)

from train_pm25_model import (
    train_pm25_model
)

from predict_pm25 import (
    predict_pm25
)


default_args = {
    "owner": "TEAM",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    "proyecto_ia_pipeline",
    default_args=default_args,
    description="PM2.5 Prediction Pipeline",
    schedule_interval=None,
    catchup=False,
    tags=["bronze", "silver", "gold", "ml"]
)


def purpleair_pipeline():

    extract_purpleair_history()


def api_bronze_pipeline():

    df = extract_api_data()

    save_raw_data(df)

    load_to_bronze(df)


def api_silver_pipeline():

    transform_api_data()


def merge_pm10_pipeline():

    merge_pm10_data()


def historical_compartir_station_pipeline():

    df = read_historical_data()

    load_to_silver(df)


def pm25_training_pipeline():

    train_pm25_model()


def predict_pm25_pipeline():

    predict_pm25()


extract_api_data_purpleair_task = PythonOperator(
    task_id="extract_api_data_purpleair",
    python_callable=purpleair_pipeline,
    dag=dag,
)


extract_api_data_ambient_weather_task = PythonOperator(
    task_id="extract_api_data_ambient_weather",
    python_callable=api_bronze_pipeline,
    dag=dag,
)


transform_and_load_api_data_task = PythonOperator(
    task_id="transform_and_load_api_data",
    python_callable=api_silver_pipeline,
    dag=dag,
)


merge_pm10_api_data_task = PythonOperator(
    task_id="merge_pm10_api_data",
    python_callable=merge_pm10_pipeline,
    dag=dag,
)


load_historical_compartir_station_task = PythonOperator(
    task_id="load_historical_compartir_station_data",
    python_callable=historical_compartir_station_pipeline,
    dag=dag,
)


train_pm25_model_task = PythonOperator(
    task_id="train_pm2.5_model",
    python_callable=pm25_training_pipeline,
    dag=dag,
)


predict_pm25_task = PythonOperator(
    task_id="predict_pm2.5",
    python_callable=predict_pm25_pipeline,
    dag=dag,
)


extract_api_data_purpleair_task >> \
extract_api_data_ambient_weather_task >> \
transform_and_load_api_data_task >> \
merge_pm10_api_data_task >> \
load_historical_compartir_station_task >> \
train_pm25_model_task >> \
predict_pm25_task
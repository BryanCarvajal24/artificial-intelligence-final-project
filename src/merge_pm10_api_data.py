import pandas as pd

from sqlalchemy import (
    create_engine,
    text
)


def merge_pm10_data():

    print(
        "=== STARTING PM10 MERGE ==="
    )

    engine = create_engine(
        "postgresql+psycopg2://"
        "ai_admin:ai_admin"
        "@postgres:5432/ai_project"
    )

    # =====================================
    # LEER DATOS AMBIENTALES
    # =====================================

    environmental_df = pd.read_sql(
        """
        SELECT *
        FROM silver.stg_environmental_api_data
        """,
        con=engine
    )

    print(
        f"Environmental records: "
        f"{len(environmental_df)}"
    )

    # =====================================
    # LEER PM10
    # =====================================

    pm10_df = pd.read_sql(
        """
        SELECT *
        FROM bronze."PM10_station_api_data"
        """,
        con=engine
    )

    print(
        f"PM10 records: "
        f"{len(pm10_df)}"
    )

    # =====================================
    # DATETIME
    # =====================================

    environmental_df["Fecha & Hora"] = pd.to_datetime(
        environmental_df["Fecha & Hora"]
    )

    pm10_df["Fecha & Hora"] = pd.to_datetime(
        pm10_df["Fecha & Hora"]
    )

    print(
        f"Environmental dtype: "
        f"{environmental_df['Fecha & Hora'].dtype}"
    )

    print(
        f"PM10 dtype: "
        f"{pm10_df['Fecha & Hora'].dtype}"
    )

    # =====================================
    # MERGE POR FECHA Y HORA EXACTA
    # SOLO CONSERVAR FECHAS EXISTENTES
    # EN AMBAS TABLAS
    # =====================================

    merged_df = environmental_df.merge(
        pm10_df,
        how="inner",
        on="Fecha & Hora"
    )

    print(
        f"Records after merge: "
        f"{len(merged_df)}"
    )

    # =====================================
    # PM10 DESPUÉS DE FECHA
    # =====================================

    ordered_columns = [
        "Fecha & Hora",
        "PM10 (ug/m3)"
    ]

    for column in merged_df.columns:

        if column not in ordered_columns:

            ordered_columns.append(
                column
            )

    merged_df = merged_df[
        ordered_columns
    ]

    # =====================================
    # ORDENAR POR FECHA
    # =====================================

    merged_df = merged_df.sort_values(
        by="Fecha & Hora"
    )

    merged_df = merged_df.reset_index(
        drop=True
    )

    # =====================================
    # CREAR SCHEMA
    # =====================================

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS silver
                """
            )
        )

    # =====================================
    # SOBRESCRIBIR TABLA ORIGINAL
    # =====================================

    merged_df.to_sql(
        name="stg_environmental_api_data",
        schema="silver",
        con=engine,
        if_exists="replace",
        index=False
    )

    print(
        "=== PM10 MERGE COMPLETED ==="
    )

    print(
        "Schema: silver"
    )

    print(
        "Table: stg_environmental_api_data"
    )

    print(
        f"Records loaded: "
        f"{len(merged_df)}"
    )

    print(
        "=== FINAL COLUMNS ==="
    )

    for column in merged_df.columns:

        print(column)

    return merged_df


if __name__ == "__main__":

    merge_pm10_data()
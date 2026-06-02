import os
from io import StringIO
from datetime import datetime

import pandas as pd
import requests

from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    text
)


load_dotenv()


API_KEY = os.getenv(
    "PURPLEAIR_API_KEY"
)

SENSOR_ID = os.getenv(
    "PURPLEAIR_SENSOR_ID"
)


def extract_purpleair_history():

    print(
        "=== EXTRACTING PURPLEAIR HISTORY ==="
    )

    print(
        f"Sensor ID: {SENSOR_ID}"
    )

    end_timestamp = (
        datetime.utcnow()
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    url = (
        f"https://api.purpleair.com/v1/sensors/"
        f"{SENSOR_ID}/history/csv"
    )

    headers = {
        "X-API-Key": API_KEY
    }

    params = {

        # 26/05/2026 10:00 AM Colombia
        # = 15:00 UTC

        "start_timestamp":
            "2026-05-26T15:00:00Z",

        "end_timestamp":
            end_timestamp,

        "average":
            60,

        "fields":
            "pm10.0_atm"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    print(
        f"Status Code: {response.status_code}"
    )

    if response.status_code != 200:

        raise Exception(
            response.text
        )

    df = pd.read_csv(
        StringIO(
            response.text
        )
    )

    print(
        f"Records downloaded: {len(df)}"
    )

    print(
        f"Columns downloaded: "
        f"{len(df.columns)}"
    )

    # =====================================
    # COLUMNAS NECESARIAS
    # =====================================

    df = df[
        [
            "time_stamp",
            "pm10.0_atm"
        ]
    ]

    # =====================================
    # UTC -> COLOMBIA
    # =====================================

    df["Fecha & Hora"] = (
        pd.to_datetime(
            df["time_stamp"],
            utc=True
        )
        .dt.tz_convert(
            "America/Bogota"
        )
        .dt.tz_localize(None)
    )

    df = df.drop(
        columns=[
            "time_stamp"
        ]
    )

    # =====================================
    # RENOMBRAR PM10
    # =====================================

    df = df.rename(
        columns={
            "pm10.0_atm":
                "PM10 (ug/m3)"
        }
    )

    # =====================================
    # ORDENAR
    # =====================================

    df = df.sort_values(
        by="Fecha & Hora",
        ascending=True
    )

    df = df.reset_index(
        drop=True
    )

    # =====================================
    # ORDEN FINAL COLUMNAS
    # =====================================

    df = df[
        [
            "Fecha & Hora",
            "PM10 (ug/m3)"
        ]
    ]

    print(
        "=== DATA PREPARED ==="
    )

    print(
        f"Oldest record: "
        f"{df['Fecha & Hora'].min()}"
    )

    print(
        f"Most recent record: "
        f"{df['Fecha & Hora'].max()}"
    )

    # =====================================
    # GUARDAR CSV RAW
    # =====================================

    os.makedirs(
        "/opt/airflow/data/raw",
        exist_ok=True
    )

    csv_path = (
        "/opt/airflow/data/raw/"
        "PM10_station_api_data.csv"
    )

    df.to_csv(
        csv_path,
        index=False
    )

    print(
        "=== RAW CSV SAVED ==="
    )

    print(
        f"Path: {csv_path}"
    )

    # =====================================
    # POSTGRES
    # =====================================

    engine = create_engine(
        "postgresql+psycopg2://"
        "ai_admin:ai_admin"
        "@postgres:5432/ai_project"
    )

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS bronze
                """
            )
        )

    # =====================================
    # CARGAR A BRONZE
    # =====================================

    df.to_sql(
        name="PM10_station_api_data",
        schema="bronze",
        con=engine,
        if_exists="replace",
        index=False
    )

    print(
        "=== BRONZE LOAD COMPLETED ==="
    )

    print(
        "Schema: bronze"
    )

    print(
        "Table: PM10_station_api_data"
    )

    print(
        f"Records inserted: {len(df)}"
    )

    return df


if __name__ == "__main__":

    extract_purpleair_history()
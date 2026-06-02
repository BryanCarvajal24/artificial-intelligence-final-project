import os
import time

import pandas as pd
import requests

from dotenv import load_dotenv

from sqlalchemy import create_engine, text


load_dotenv()


RAW_FILE = "data/raw/weather_station_api_data.csv"


def extract_api_data():

    api_key = os.getenv("API_KEY")
    app_key = os.getenv("APP_KEY")

    mac = "48:E7:29:7C:A0:44"

    base_url = (
        f"https://api.ambientweather.net/v1/devices/{mac}"
    )

    limit = 288

    all_data = []
    seen_dates = set()

    end_date = None

    print("=== DOWNLOADING API DATA ===")

    while True:

        params = {
            "apiKey": api_key,
            "applicationKey": app_key,
            "limit": limit
        }

        if end_date is not None:

            params["endDate"] = end_date

        response = requests.get(
            base_url,
            params=params
        )

        if response.status_code != 200:

            raise Exception(
                f"API Error: {response.status_code} - {response.text}"
            )

        data = response.json()

        if not data:

            print("No more API records available.")
            break

        new_rows = []

        for row in data:

            timestamp = row["dateutc"]

            if timestamp not in seen_dates:

                seen_dates.add(timestamp)
                new_rows.append(row)

        if len(new_rows) == 0:

            print("API download completed.")
            break

        all_data.extend(new_rows)

        oldest_timestamp = min(
            row["dateutc"]
            for row in new_rows
        )

        end_date = oldest_timestamp - 1

        time.sleep(1)

    df = pd.DataFrame(all_data)

    df["datetime"] = (
        pd.to_datetime(
            df["dateutc"],
            unit="ms",
            utc=True
        )
        .dt.tz_convert("America/Bogota")
        .dt.tz_localize(None)
    )

    df = df.sort_values(
        by="datetime"
    )

    print("=== API CONNECTION SUCCESSFUL ===")
    print(f"Total records downloaded: {len(df)}")

    print("Oldest record:")
    print(df["datetime"].min())

    print("Most recent record:")
    print(df["datetime"].max())

    return df


def save_raw_data(df):

    os.makedirs(
        "data/raw",
        exist_ok=True
    )

    df.to_csv(
        RAW_FILE,
        index=False
    )

    print("=== RAW FILE CREATED ===")
    print(f"File: {RAW_FILE}")
    print(f"Records saved: {len(df)}")


def load_to_bronze(df):

    engine = create_engine(
        "postgresql+psycopg2://ai_admin:ai_admin@postgres:5432/ai_project"
    )

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS bronze
                """
            )
        )

    df.to_sql(
        name="weather_station_api_data",
        schema="bronze",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("=== BRONZE LOAD COMPLETED ===")
    print("Schema: bronze")
    print("Table: weather_station_api_data")
    print(f"Records inserted: {len(df)}")


if __name__ == "__main__":

    dataframe = extract_api_data()

    save_raw_data(dataframe)

    load_to_bronze(dataframe)

    print("Process completed successfully.")
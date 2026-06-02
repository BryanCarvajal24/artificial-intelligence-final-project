import numpy as np
import pandas as pd

from sqlalchemy import create_engine, text


def transform_api_data():

    print("=== STARTING API DATA TRANSFORMATION ===")

    engine = create_engine(
        "postgresql+psycopg2://ai_admin:ai_admin@postgres:5432/ai_project"
    )

    df = pd.read_sql(
        """
        SELECT *
        FROM bronze.weather_station_api_data
        """,
        con=engine
    )

    columns_to_drop = [
        "dateutc",
        "windgustmph",
        "maxdailygust",
        "uv",
        "eventrainin",
        "dailyrainin",
        "weeklyrainin",
        "monthlyrainin",
        "yearlyrainin",
        "totalrainin",
        "battout",
        "tempinf",
        "humidityin",
        "baromrelin",
        "baromabsin",
        "feelsLike",
        "dewPoint",
        "feelsLikein",
        "dewPointin",
        "lastRain",
        "date",
        "passkey",
        "time",
        "loc"
    ]

    original_columns = len(df.columns)

    df = df.drop(
        columns=columns_to_drop,
        errors="ignore"
    )

    print("=== COLUMN REMOVAL ===")
    print(f"Columns removed: {len(columns_to_drop)}")

    # =====================================
    # VALIDACIONES
    # =====================================

    records_before_validation = len(df)

    df = df[
        (df["humidity"] >= 0) &
        (df["humidity"] <= 100)
    ]

    records_after_validation = len(df)

    print("=== HUMIDITY VALIDATION ===")
    print("Rule: Humidity (%) must be between 0 and 100")
    print(
        f"Records removed: "
        f"{records_before_validation - records_after_validation}"
    )

    # =====================================
    # CONVERSIONES
    # =====================================

    transformed_df = pd.DataFrame()

    transformed_df["Temperatura (°C)"] = (
        (df["tempf"] - 32) * 5 / 9
    ).round(1)

    print("=== TEMPERATURE ===")
    print("Converted tempf (°F) -> Temperatura (°C)")
    print(f"Records transformed: {len(df)}")

    transformed_df["Vel Viento (m/s)"] = (
        df["windspeedmph"] * 0.44704
    ).round(1)

    print("=== WIND SPEED ===")
    print("Converted windspeedmph (mph) -> Vel Viento (m/s)")
    print(f"Records transformed: {len(df)}")

    transformed_df["Dir Viento (grados)"] = (
        df["winddir"].astype(float)
    ).round(1)

    print("=== WIND DIRECTION ===")
    print("Mapped winddir -> Dir Viento (grados)")
    print(f"Records transformed: {len(df)}")

    transformed_df["Humedad (%)"] = (
        df["humidity"].astype(float)
    ).round(1)

    print("=== HUMIDITY ===")
    print("Mapped humidity -> Humedad (%)")
    print(f"Records transformed: {len(df)}")

    transformed_df["Radiacion Solar (W/m2)"] = (
        df["solarradiation"]
    ).round(1)

    print("=== SOLAR RADIATION ===")
    print("Mapped solarradiation -> Radiacion Solar (W/m2)")
    print(f"Records transformed: {len(df)}")

    transformed_df["Lluvia (mm)"] = (
        df["hourlyrainin"] * 25.4
    ).round(1)

    print("=== RAINFALL ===")
    print("Converted hourlyrainin (in) -> Lluvia (mm)")
    print(f"Records transformed: {len(df)}")

    transformed_df["Fecha & Hora"] = (
        df["datetime"]
    )

    print("=== DATETIME ===")
    print("Mapped datetime -> Fecha & Hora")
    print(f"Records transformed: {len(df)}")

    transformed_df = transformed_df.sort_values(
        by="Fecha & Hora"
    )

    # =====================================
    # AGRUPAMIENTO HORARIO
    # =====================================

    print("=== HOURLY AGGREGATION ===")

    records_before_grouping = len(
        transformed_df
    )

    transformed_df["Fecha & Hora"] = pd.to_datetime(
        transformed_df["Fecha & Hora"]
    )

    transformed_df = (
        transformed_df
        .set_index("Fecha & Hora")
        .resample("1h")
        .agg({
            "Temperatura (°C)": "mean",
            "Vel Viento (m/s)": "mean",
            "Dir Viento (grados)": "median",
            "Humedad (%)": "mean",
            "Radiacion Solar (W/m2)": "mean",
            "Lluvia (mm)": "max"
        })
        .reset_index()
    )

    numeric_columns = [
        "Temperatura (°C)",
        "Vel Viento (m/s)",
        "Dir Viento (grados)",
        "Humedad (%)",
        "Radiacion Solar (W/m2)",
        "Lluvia (mm)"
    ]

    transformed_df[numeric_columns] = (
        transformed_df[numeric_columns]
        .round(1)
    )

    print(
        f"Records before grouping: "
        f"{records_before_grouping}"
    )

    print(
        f"Records after grouping: "
        f"{len(transformed_df)}"
    )

    # =====================================
    # FEATURE ENGINEERING (WIND)
    # =====================================

    print("=== WIND FEATURE ENGINEERING ===")

    wind_direction_rad = (
        transformed_df["Dir Viento (grados)"]
        * np.pi
        / 180
    )

    transformed_df["Wx"] = (
        transformed_df["Vel Viento (m/s)"]
        * np.cos(wind_direction_rad)
    )

    transformed_df["Wy"] = (
        transformed_df["Vel Viento (m/s)"]
        * np.sin(wind_direction_rad)
    )

    print(
        "Created Wx and Wy from "
        "Vel Viento (m/s) and Dir Viento (grados)"
    )

    print(
        f"Records transformed: "
        f"{len(transformed_df)}"
    )

    transformed_df = transformed_df.drop(
        columns=[
            "Vel Viento (m/s)",
            "Dir Viento (grados)"
        ]
    )


    # =====================================
    # FEATURE ENGINEERING (TIME)
    # =====================================

    print("=== TIME FEATURE ENGINEERING ===")

    tiempo_s = pd.to_datetime(
        transformed_df["Fecha & Hora"]
    ).map(
        pd.Timestamp.timestamp
    )

    dia = 24 * 60 * 60

    transformed_df["dia_sin"] = np.sin(
        tiempo_s * (
            2 * np.pi / dia
        )
    )

    transformed_df["dia_cos"] = np.cos(
        tiempo_s * (
            2 * np.pi / dia
        )
    )

    print(
        "Created dia_sin and dia_cos "
        "from Fecha & Hora"
    )

    print(
        f"Records transformed: "
        f"{len(transformed_df)}"
    )

    # =====================================
    # EXTRAER COMPONENTES DE FECHA
    # =====================================

    transformed_df["Año"] = (
        transformed_df["Fecha & Hora"].dt.year
    )

    transformed_df["Mes"] = (
        transformed_df["Fecha & Hora"].dt.month
    )

    transformed_df["Día"] = (
        transformed_df["Fecha & Hora"].dt.day
    )

    transformed_df["Hora"] = (
        transformed_df["Fecha & Hora"].dt.hour
    )

    print(
        "Created Año, Mes, Día and Hora"
    )

    print(
        f"Records transformed: "
        f"{len(transformed_df)}"
    )

    # =====================================
    # ELIMINAR FECHA ORIGINAL
    # =====================================

    #transformed_df = transformed_df.drop(
    #    columns=[
    #    "Fecha & Hora"
    #    ]
    #)

    #print(
    #    "Removed column: Fecha & Hora"
    #)













    remaining_columns = len(
        transformed_df.columns
    )

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS silver
                """
            )
        )

    transformed_df.to_sql(
        name="stg_environmental_api_data",
        schema="silver",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("=== API DATA TRANSFORMATION COMPLETED ===")
    print(f"Original columns: {original_columns}")
    print(f"Remaining columns: {remaining_columns}")
    print(f"Records loaded: {len(transformed_df)}")

    print("=== FINAL COLUMNS ===")

    for column in transformed_df.columns:
        print(column)

    print("=== PROCESS COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":

    transform_api_data()
    
    
    












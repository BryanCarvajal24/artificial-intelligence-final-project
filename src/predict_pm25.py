import os
import joblib

import pandas as pd

from sqlalchemy import (
    create_engine,
    text
)


def predict_pm25():

    print(
        "=== STARTING PM2.5 PREDICTION ==="
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
    # CARGAR FEATURES
    # =====================================

    features = joblib.load(
        "/opt/airflow/models/pm25_features.pkl"
    )

    print(
        "=== FEATURES LOADED ==="
    )

    print(
        features
    )

    # =====================================
    # CARGAR MODELO
    # =====================================

    model = joblib.load(
        "/opt/airflow/models/pm25_xgboost_model.pkl"
    )

    print(
        "=== MODEL LOADED ==="
    )

    # =====================================
    # CREAR MATRIZ X
    # =====================================

    X = environmental_df[
        features
    ].copy()

    print(
        f"Prediction records: "
        f"{len(X)}"
    )

    print(
        f"Prediction features: "
        f"{X.shape[1]}"
    )

    # =====================================
    # PREDECIR PM2.5
    # =====================================

    predictions = model.predict(
        X
    )

    environmental_df[
        "PM2.5 Predicho (ug/m3)"
    ] = predictions

    print(
        "=== PREDICTIONS COMPLETED ==="
    )

    # =====================================
    # CREAR SCHEMA GOLD
    # =====================================

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS gold
                """
            )
        )

    # =====================================
    # ORDENAR COLUMNAS
    # =====================================

    ordered_columns = [
        "Fecha & Hora",
        "PM10 (ug/m3)",
        "Temperatura (°C)",
        "Humedad (%)",
        "Radiacion Solar (W/m2)",
        "Lluvia (mm)",
        "Wx",
        "Wy",
        "dia_sin",
        "dia_cos",
        "PM2.5 Estimado (ug/m3)"
    ]

    prediction_df = environmental_df[
        ordered_columns
    ]

    # =====================================
    # GUARDAR EN GOLD
    # =====================================

    prediction_df.to_sql(
        name="pm25_predictions",
        schema="gold",
        con=engine,
        if_exists="replace",
        index=False
    )

    print(
        "=== GOLD LOAD COMPLETED ==="
    )

    print(
        "Schema: gold"
    )

    print(
        "Table: pm25_predictions"
    )

    print(
        f"Records loaded: "
        f"{len(prediction_df)}"
    )

    print(
        "=== FINAL COLUMNS ==="
    )

    for column in prediction_df.columns:

        print(column)

    return prediction_df


if __name__ == "__main__":

    predict_pm25()
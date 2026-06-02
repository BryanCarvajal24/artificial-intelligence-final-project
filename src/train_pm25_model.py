import os
import joblib

import numpy as np
import pandas as pd

from sqlalchemy import (
    create_engine,
    text
)

from xgboost import XGBRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


def train_pm25_model():

    engine = create_engine(
        "postgresql+psycopg2://ai_admin:ai_admin@postgres:5432/ai_project"
    )

    # =====================================
    # CREAR TRAINING DATASET
    # =====================================

    print(
        "=== CREATING TRAINING DATASET ==="
    )

    with engine.connect() as conn:

        result = conn.execute(
            text(
                """
                SELECT
                    "PM2.5 (ug/m3)",
                    "PM10 (ug/m3)",
                    "Temperatura (°C)",
                    "Humedad (%)",
                    "Radiacion Solar (W/m2)",
                    "Lluvia (mm)",
                    "Wx",
                    "Wy",
                    "dia_sin",
                    "dia_cos"
                FROM silver.stg_historical_compartir_station
                """
            )
        )

        training_df = pd.DataFrame(
            result.fetchall(),
            columns=result.keys()
        )

    print(
        f"Historical records loaded: "
        f"{len(training_df)}"
    )

    training_df = training_df.dropna()

    print(
        f"Records after dropna: "
        f"{len(training_df)}"
    )

    training_df.to_sql(
        name="stg_pm25_training_dataset",
        schema="silver",
        con=engine,
        if_exists="replace",
        index=False
    )

    print(
        "Training dataset created successfully"
    )

    # =====================================
    # LEER TRAINING DATASET
    # =====================================

    print(
        "=== LOADING TRAINING DATASET ==="
    )

    with engine.connect() as conn:

        result = conn.execute(
            text(
                """
                SELECT *
                FROM silver.stg_pm25_training_dataset
                """
            )
        )

        df = pd.DataFrame(
            result.fetchall(),
            columns=result.keys()
        )

    print(
        f"Records loaded: {len(df)}"
    )

    print(
        f"Columns loaded: {len(df.columns)}"
    )

    print(
        df.columns.tolist()
    )

    # =====================================
    # FEATURES / TARGET
    # =====================================

    X = df.drop(
        columns=["PM2.5 (ug/m3)"]
    )

    y = df["PM2.5 (ug/m3)"]

    print(
        "=== FEATURES AND TARGET CREATED ==="
    )

    print(
        f"Features: {X.shape[1]}"
    )

    # =====================================
    # TRAIN / TEST SPLIT
    # =====================================

    N = len(df)

    train_size = int(
        N * 0.80
    )

    X_train = X.iloc[:train_size]

    X_test = X.iloc[
        train_size:
    ]

    y_train = y.iloc[:train_size]

    y_test = y.iloc[
        train_size:
    ]

    print(
        "=== TRAIN / TEST SPLIT ==="
    )

    print(
        f"Train: {X_train.shape}"
    )

    print(
        f"Test: {X_test.shape}"
    )

    # =====================================
    # XGBOOST MODEL
    # =====================================

    print(
        "=== TRAINING XGBOOST MODEL ==="
    )

    xgb_model = XGBRegressor(

        n_estimators=500,

        max_depth=6,

        learning_rate=0.03,

        subsample=0.7,

        colsample_bytree=0.7,

        reg_alpha=0.5,

        reg_lambda=1.5,

        random_state=42,

        n_jobs=-1
    )

    xgb_model.fit(
        X_train,
        y_train
    )

    print(
        "Model trained successfully"
    )

    # =====================================
    # GUARDAR MODELO
    # =====================================

    MODEL_DIR = "/opt/airflow/models"

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        xgb_model,
        f"{MODEL_DIR}/pm25_xgboost_model.pkl"
    )

    joblib.dump(
        X.columns.tolist(),
        f"{MODEL_DIR}/pm25_features.pkl"
    )

    print(
        "=== MODEL SAVED ==="
    )

    print(
        f"Model: {MODEL_DIR}/pm25_xgboost_model.pkl"
    )

    print(
        f"Features: {MODEL_DIR}/pm25_features.pkl"
    )

    # =====================================
    # TRAIN PREDICTIONS
    # =====================================

    y_pred_train = (
        xgb_model.predict(
            X_train
        )
    )

    # =====================================
    # TEST PREDICTIONS
    # =====================================

    y_pred_test = (
        xgb_model.predict(
            X_test
        )
    )

    print(
        "=== SAMPLE PREDICTIONS ==="
    )

    print(
        "Predictions:"
    )

    print(
        y_pred_test[:10]
    )

    print(
        "Real values:"
    )

    print(
        y_test.values[:10]
    )

    # =====================================
    # TRAIN METRICS
    # =====================================

    mae_train = mean_absolute_error(
        y_train,
        y_pred_train
    )

    mse_train = mean_squared_error(
        y_train,
        y_pred_train
    )

    rmse_train = np.sqrt(
        mse_train
    )

    r2_train = r2_score(
        y_train,
        y_pred_train
    )

    print(
        "=== TRAIN METRICS ==="
    )

    print(
        "MAE TRAIN:",
        mae_train
    )

    print(
        "MSE TRAIN:",
        mse_train
    )

    print(
        "RMSE TRAIN:",
        rmse_train
    )

    print(
        "R2 TRAIN:",
        r2_train
    )

    # =====================================
    # TEST METRICS
    # =====================================

    mae_test = mean_absolute_error(
        y_test,
        y_pred_test
    )

    mse_test = mean_squared_error(
        y_test,
        y_pred_test
    )

    rmse_test = np.sqrt(
        mse_test
    )

    r2_test = r2_score(
        y_test,
        y_pred_test
    )

    print(
        "=== TEST METRICS ==="
    )

    print(
        "MAE TEST:",
        mae_test
    )

    print(
        "MSE TEST:",
        mse_test
    )

    print(
        "RMSE TEST:",
        rmse_test
    )

    print(
        "R2 TEST:",
        r2_test
    )

    print(
        "=== PM2.5 MODEL TRAINING COMPLETED ==="
    )


if __name__ == "__main__":

    train_pm25_model()
import pandas as pd
from sqlalchemy import create_engine, text


EXCEL_FILE = "data/clean/df_estación_compartir_clean2 (3).xlsx"


def read_historical_data():
    """
    Leer dataset histórico limpio.
    """

    df = pd.read_excel(EXCEL_FILE)

    print("\n=== LECTURA DEL DATASET HISTÓRICO ===")
    print(f"Filas leídas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")
    print(f"Nombres de columnas: {list(df.columns)}")

    return df


def load_to_silver(df):
    """
    Cargar DataFrame en PostgreSQL.
    """

    engine = create_engine(
        "postgresql+psycopg2://ai_admin:ai_admin@postgres:5432/ai_project"
    )

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS silver
                """
            )
        )

    df.to_sql(
        name="stg_historical_compartir_station",
        schema="silver",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("\n=== CARGA EN POSTGRESQL ===")
    print("Esquema: silver")
    print("Tabla: stg_historical_compartir_station")
    print(f"Registros insertados: {len(df)}")
    print(f"Total columnas: {len(df.columns)}")


if __name__ == "__main__":

    dataframe = read_historical_data()

    load_to_silver(dataframe)

    print("\nProceso finalizado correctamente.")
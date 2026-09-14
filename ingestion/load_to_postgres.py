import os

from sqlalchemy import create_engine, text

from ingestion.extract import TABLE_LOAD_ORDER


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/korusafe",
)


def create_postgres_engine(database_url=DATABASE_URL):
    return create_engine(database_url)


def truncate_tables(engine, table_names=TABLE_LOAD_ORDER):
    table_list = ", ".join(table_names)

    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))


def load_dataframe(engine, table_name, df):
    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(df)} rows into {table_name}")


def load_all(dataframes, database_url=DATABASE_URL, truncate=True):
    engine = create_postgres_engine(database_url)

    if truncate:
        truncate_tables(engine)

    for table_name in TABLE_LOAD_ORDER:
        load_dataframe(engine, table_name, dataframes[table_name])

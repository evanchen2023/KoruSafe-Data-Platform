import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data_generator" / "data" / "generated"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/korusafe",
)

TABLE_LOAD_ORDER = [
    ("organisations", "organisations.csv"),
    ("employees", "employees.csv"),
    ("incidents", "incidents.csv"),
    ("injuries", "injuries.csv"),
    ("claims", "claims.csv"),
]


def load_csv_to_table(engine, table_name, csv_name):
    csv_path = DATA_DIR / csv_name

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(df)} rows into {table_name}")


def main():
    engine = create_engine(DATABASE_URL)
    table_names = ", ".join(table_name for table_name, _ in TABLE_LOAD_ORDER)

    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))

    for table_name, csv_name in TABLE_LOAD_ORDER:
        load_csv_to_table(engine, table_name, csv_name)


if __name__ == "__main__":
    main()

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

TABLE_LOAD_ORDER = [
    "organisations",
    "employees",
    "incidents",
    "injuries",
    "claims",
]


def extract_csv(table_name, data_dir=RAW_DATA_DIR):
    csv_path = data_dir / f"{table_name}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Source CSV file not found: {csv_path}")

    return pd.read_csv(csv_path, encoding="utf-8-sig")


def extract_all(data_dir=RAW_DATA_DIR):
    return {
        table_name: extract_csv(table_name, data_dir)
        for table_name in TABLE_LOAD_ORDER
    }

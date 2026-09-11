import pandas as pd
import pytest


@pytest.mark.parametrize(
    "table_name",
    ["organisations", "employees", "incidents", "injuries", "claims"],
)
def test_generated_csv_exists(generated_data_dir, table_name):
    """Every generated CSV should exist before ingestion runs."""

    file_path = generated_data_dir / f"{table_name}.csv"

    assert file_path.exists()


@pytest.mark.parametrize(
    "table_name",
    ["organisations", "employees", "incidents", "injuries", "claims"],
)
def test_generated_csv_can_be_read(generated_data_dir, table_name):
    """Every generated CSV should be readable by pandas."""

    file_path = generated_data_dir / f"{table_name}.csv"

    df = pd.read_csv(file_path)

    assert len(df) > 0


@pytest.mark.parametrize(
    "table_name",
    ["organisations", "employees", "incidents", "injuries", "claims"],
)
def test_generated_csv_has_expected_columns(loaded_csvs, csv_schemas, table_name):
    """Every generated CSV should match the expected table schema."""

    df = loaded_csvs[table_name]

    assert list(df.columns) == csv_schemas[table_name]

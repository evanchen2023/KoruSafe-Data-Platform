import pandas as pd
import pytest

from ingestion.extract import extract_all, extract_csv


def test_raw_data_directory_exists(raw_data_dir):
    """The pipeline should have a raw source data directory."""

    assert raw_data_dir.exists()


def test_table_load_order_matches_foreign_key_dependencies(table_load_order):
    """Parent tables must be loaded before child tables."""

    assert table_load_order == [
        "organisations",
        "employees",
        "incidents",
        "injuries",
        "claims",
    ]


@pytest.mark.parametrize(
    "table_name",
    ["organisations", "employees", "incidents", "injuries", "claims"],
)
def test_raw_csv_exists(raw_data_dir, table_name):
    """Every expected raw CSV should exist."""

    file_path = raw_data_dir / f"{table_name}.csv"

    assert file_path.exists()


@pytest.mark.parametrize(
    "table_name",
    ["organisations", "employees", "incidents", "injuries", "claims"],
)
def test_extract_csv_returns_dataframe(table_name):
    """extract_csv should read one source file into a DataFrame."""

    df = extract_csv(table_name)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_extract_all_returns_every_table(table_load_order):
    """extract_all should return all source tables in the pipeline."""

    dataframes = extract_all()

    assert list(dataframes.keys()) == table_load_order


@pytest.mark.parametrize(
    "table_name",
    ["organisations", "employees", "incidents", "injuries", "claims"],
)
def test_raw_csv_has_expected_columns(raw_csvs, csv_schemas, table_name):
    """Every raw source CSV should match the expected table schema."""

    df = raw_csvs[table_name]

    assert list(df.columns) == csv_schemas[table_name]

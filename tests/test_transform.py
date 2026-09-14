import pandas as pd

from ingestion.transform import transform_all, transform_table


def test_transform_table_strips_column_names_and_text_values():
    """Transform should clean whitespace from headers and text fields."""

    df = pd.DataFrame(
        {
            "organisation_id ": ["1"],
            "organisation_name": [" Koru Construction "],
            "industry": [" Construction "],
            "employee_count": ["120"],
            "region": [" Auckland "],
            "created_date": ["2024-01-10"],
        }
    )

    transformed = transform_table("organisations", df)

    assert list(transformed.columns) == [
        "organisation_id",
        "organisation_name",
        "industry",
        "employee_count",
        "region",
        "created_date",
    ]
    assert transformed.loc[0, "organisation_name"] == "Koru Construction"
    assert transformed.loc[0, "region"] == "Auckland"


def test_transform_table_converts_integer_columns():
    """ID, count and amount fields should become integer columns."""

    transformed = transform_table(
        "claims",
        pd.DataFrame(
            {
                "claim_id": ["1"],
                "injury_id": ["10"],
                "employee_id": ["100"],
                "claim_date": ["2024-04-10"],
                "claim_type": ["Medical"],
                "claim_amount": ["1800"],
                "claim_status": ["Approved"],
            }
        ),
    )

    assert transformed["claim_id"].dtype == "int64"
    assert transformed["injury_id"].dtype == "int64"
    assert transformed["employee_id"].dtype == "int64"
    assert transformed["claim_amount"].dtype == "int64"


def test_transform_table_converts_date_columns():
    """Date-like strings should be converted to Python date values."""

    transformed = transform_table(
        "incidents",
        pd.DataFrame(
            {
                "incident_id": [1],
                "organisation_id": [1],
                "employee_id": [10],
                "incident_date": ["2024-04-01"],
                "incident_type": ["Fall"],
                "severity": ["Medium"],
                "location": ["Warehouse"],
                "description": ["Slip near loading bay"],
            }
        ),
    )

    assert transformed.loc[0, "incident_date"].isoformat() == "2024-04-01"


def test_transform_all_returns_same_tables(valid_raw_dataframes, table_load_order):
    """transform_all should preserve the table set used by the pipeline."""

    transformed = transform_all(valid_raw_dataframes)

    assert list(transformed.keys()) == table_load_order

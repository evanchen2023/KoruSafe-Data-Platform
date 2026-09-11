import pandas as pd
import pytest


PRIMARY_KEYS = [
    ("organisations", "organisation_id"),
    ("employees", "employee_id"),
    ("incidents", "incident_id"),
    ("injuries", "injury_id"),
    ("claims", "claim_id"),
]


@pytest.mark.parametrize("table_name,primary_key", PRIMARY_KEYS)
def test_primary_keys_are_unique_and_not_null(loaded_csvs, table_name, primary_key):
    df = loaded_csvs[table_name]

    assert df[primary_key].notna().all()
    assert df[primary_key].is_unique


def test_employee_count_is_positive(loaded_csvs):
    organisations = loaded_csvs["organisations"]

    assert (organisations["employee_count"] > 0).all()


def test_cost_and_day_values_are_not_negative(loaded_csvs):
    injuries = loaded_csvs["injuries"]
    claims = loaded_csvs["claims"]

    assert (injuries["medical_cost"] >= 0).all()
    assert (injuries["days_off_work"] >= 0).all()
    assert (claims["claim_amount"] >= 0).all()


@pytest.mark.parametrize(
    "table_name,date_column",
    [
        ("organisations", "created_date"),
        ("employees", "start_date"),
        ("incidents", "incident_date"),
        ("claims", "claim_date"),
    ],
)
def test_date_columns_are_valid_dates(loaded_csvs, table_name, date_column):
    parsed_dates = pd.to_datetime(loaded_csvs[table_name][date_column], errors="coerce")

    assert parsed_dates.notna().all()


def test_employees_reference_existing_organisations(loaded_csvs):
    organisations = loaded_csvs["organisations"]
    employees = loaded_csvs["employees"]

    assert employees["organisation_id"].isin(organisations["organisation_id"]).all()


def test_incidents_reference_existing_organisations_and_employees(loaded_csvs):
    organisations = loaded_csvs["organisations"]
    employees = loaded_csvs["employees"]
    incidents = loaded_csvs["incidents"]

    assert incidents["organisation_id"].isin(organisations["organisation_id"]).all()
    assert incidents["employee_id"].isin(employees["employee_id"]).all()


def test_injuries_reference_existing_incidents_and_employees(loaded_csvs):
    employees = loaded_csvs["employees"]
    incidents = loaded_csvs["incidents"]
    injuries = loaded_csvs["injuries"]

    assert injuries["incident_id"].isin(incidents["incident_id"]).all()
    assert injuries["employee_id"].isin(employees["employee_id"]).all()


def test_claims_reference_existing_injuries_and_employees(loaded_csvs):
    employees = loaded_csvs["employees"]
    injuries = loaded_csvs["injuries"]
    claims = loaded_csvs["claims"]

    assert claims["injury_id"].isin(injuries["injury_id"]).all()
    assert claims["employee_id"].isin(employees["employee_id"]).all()

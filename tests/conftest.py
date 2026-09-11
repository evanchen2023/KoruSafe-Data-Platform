from pathlib import Path

import pandas as pd
import pytest


CSV_SCHEMAS = {
    "organisations": [
        "organisation_id",
        "organisation_name",
        "industry",
        "employee_count",
        "region",
        "created_date",
    ],
    "employees": [
        "employee_id",
        "organisation_id",
        "job_role",
        "department",
        "employment_type",
        "region",
        "start_date",
    ],
    "incidents": [
        "incident_id",
        "organisation_id",
        "employee_id",
        "incident_date",
        "incident_type",
        "severity",
        "location",
        "description",
    ],
    "injuries": [
        "injury_id",
        "incident_id",
        "employee_id",
        "injury_type",
        "body_part",
        "severity",
        "medical_cost",
        "days_off_work",
    ],
    "claims": [
        "claim_id",
        "injury_id",
        "employee_id",
        "claim_date",
        "claim_type",
        "claim_amount",
        "claim_status",
    ],
}


@pytest.fixture(scope="session")
def generated_data_dir():
    return Path("data_generator/data/generated")


@pytest.fixture(scope="session")
def csv_schemas():
    return CSV_SCHEMAS


@pytest.fixture(scope="session")
def loaded_csvs(generated_data_dir):
    return {
        table_name: pd.read_csv(generated_data_dir / f"{table_name}.csv")
        for table_name in CSV_SCHEMAS
    }

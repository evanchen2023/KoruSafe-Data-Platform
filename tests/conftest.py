import pandas as pd
import pytest

from ingestion.extract import RAW_DATA_DIR, TABLE_LOAD_ORDER
from ingestion.validate import CSV_SCHEMAS


@pytest.fixture(scope="session")
def raw_data_dir():
    return RAW_DATA_DIR


@pytest.fixture(scope="session")
def table_load_order():
    return TABLE_LOAD_ORDER


@pytest.fixture(scope="session")
def csv_schemas():
    return CSV_SCHEMAS


@pytest.fixture(scope="session")
def raw_csvs(raw_data_dir, table_load_order):
    return {
        table_name: pd.read_csv(raw_data_dir / f"{table_name}.csv", encoding="utf-8-sig")
        for table_name in table_load_order
    }


@pytest.fixture
def valid_raw_dataframes():
    return {
        "organisations": pd.DataFrame(
            {
                "organisation_id": [1, 2],
                "organisation_name": ["Koru Construction", "Harbour Logistics"],
                "industry": ["Construction", "Transport"],
                "employee_count": [120, 85],
                "region": ["Auckland", "Wellington"],
                "created_date": ["2024-01-10", "2024-02-15"],
            }
        ),
        "employees": pd.DataFrame(
            {
                "employee_id": [10, 20],
                "organisation_id": [1, 2],
                "job_role": ["Engineer", "Driver"],
                "department": ["Operations", "Logistics"],
                "employment_type": ["Full time", "Contractor"],
                "region": ["Auckland", "Wellington"],
                "start_date": ["2024-03-01", "2024-03-15"],
            }
        ),
        "incidents": pd.DataFrame(
            {
                "incident_id": [100, 200],
                "organisation_id": [1, 2],
                "employee_id": [10, 20],
                "incident_date": ["2024-04-01", "2024-04-20"],
                "incident_type": ["Fall", "Vehicle accident"],
                "severity": ["Medium", "High"],
                "location": ["Warehouse", "Road"],
                "description": ["Slip near loading bay", "Minor collision"],
            }
        ),
        "injuries": pd.DataFrame(
            {
                "injury_id": [1000, 2000],
                "incident_id": [100, 200],
                "employee_id": [10, 20],
                "injury_type": ["Sprain", "Fracture"],
                "body_part": ["Ankle", "Arm"],
                "severity": ["Medium", "High"],
                "medical_cost": [1500, 12000],
                "days_off_work": [5, 30],
            }
        ),
        "claims": pd.DataFrame(
            {
                "claim_id": [10000, 20000],
                "injury_id": [1000, 2000],
                "employee_id": [10, 20],
                "claim_date": ["2024-04-10", "2024-05-01"],
                "claim_type": ["Medical", "Compensation"],
                "claim_amount": [1800, 15000],
                "claim_status": ["Approved", "Review"],
            }
        ),
    }

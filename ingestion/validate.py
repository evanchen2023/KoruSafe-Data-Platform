import pandas as pd


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

PRIMARY_KEYS = {
    "organisations": "organisation_id",
    "employees": "employee_id",
    "incidents": "incident_id",
    "injuries": "injury_id",
    "claims": "claim_id",
}

DATE_COLUMNS = {
    "organisations": ["created_date"],
    "employees": ["start_date"],
    "incidents": ["incident_date"],
    "injuries": [],
    "claims": ["claim_date"],
}


class DataValidationError(ValueError):
    """Raised when source data fails ingestion validation."""


def _require(condition, message, errors):
    if not condition:
        errors.append(message)


def validate_schema(table_name, df, errors):
    expected_columns = CSV_SCHEMAS[table_name]

    _require(
        list(df.columns) == expected_columns,
        f"{table_name}: expected columns {expected_columns}, got {list(df.columns)}",
        errors,
    )


def validate_primary_key(table_name, df, errors):
    primary_key = PRIMARY_KEYS[table_name]

    _require(
        df[primary_key].notna().all(),
        f"{table_name}: primary key {primary_key} contains null values",
        errors,
    )
    _require(
        df[primary_key].is_unique,
        f"{table_name}: primary key {primary_key} contains duplicate values",
        errors,
    )


def validate_dates(table_name, df, errors):
    for date_column in DATE_COLUMNS[table_name]:
        parsed_dates = pd.to_datetime(
            df[date_column],
            errors="coerce",
            format="%Y-%m-%d",
        )
        _require(
            parsed_dates.notna().all(),
            f"{table_name}: {date_column} contains invalid dates",
            errors,
        )


def validate_business_rules(dataframes, errors):
    organisations = dataframes["organisations"]
    injuries = dataframes["injuries"]
    claims = dataframes["claims"]

    _require(
        (organisations["employee_count"] > 0).all(),
        "organisations: employee_count must be greater than zero",
        errors,
    )
    _require(
        (injuries["medical_cost"] >= 0).all(),
        "injuries: medical_cost cannot be negative",
        errors,
    )
    _require(
        (injuries["days_off_work"] >= 0).all(),
        "injuries: days_off_work cannot be negative",
        errors,
    )
    _require(
        (claims["claim_amount"] >= 0).all(),
        "claims: claim_amount cannot be negative",
        errors,
    )


def validate_relationships(dataframes, errors):
    organisations = dataframes["organisations"]
    employees = dataframes["employees"]
    incidents = dataframes["incidents"]
    injuries = dataframes["injuries"]
    claims = dataframes["claims"]

    _require(
        employees["organisation_id"].isin(organisations["organisation_id"]).all(),
        "employees: organisation_id must reference organisations.organisation_id",
        errors,
    )
    _require(
        incidents["organisation_id"].isin(organisations["organisation_id"]).all(),
        "incidents: organisation_id must reference organisations.organisation_id",
        errors,
    )
    _require(
        incidents["employee_id"].isin(employees["employee_id"]).all(),
        "incidents: employee_id must reference employees.employee_id",
        errors,
    )
    _require(
        injuries["incident_id"].isin(incidents["incident_id"]).all(),
        "injuries: incident_id must reference incidents.incident_id",
        errors,
    )
    _require(
        injuries["employee_id"].isin(employees["employee_id"]).all(),
        "injuries: employee_id must reference employees.employee_id",
        errors,
    )
    _require(
        claims["injury_id"].isin(injuries["injury_id"]).all(),
        "claims: injury_id must reference injuries.injury_id",
        errors,
    )
    _require(
        claims["employee_id"].isin(employees["employee_id"]).all(),
        "claims: employee_id must reference employees.employee_id",
        errors,
    )


def validate_all(dataframes):
    errors = []

    for table_name, df in dataframes.items():
        validate_schema(table_name, df, errors)
        validate_primary_key(table_name, df, errors)
        validate_dates(table_name, df, errors)

    validate_business_rules(dataframes, errors)
    validate_relationships(dataframes, errors)

    if errors:
        raise DataValidationError("\n".join(errors))

    return True

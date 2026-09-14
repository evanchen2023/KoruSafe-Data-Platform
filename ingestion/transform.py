import pandas as pd


INTEGER_COLUMNS = {
    "organisations": ["organisation_id", "employee_count"],
    "employees": ["employee_id", "organisation_id"],
    "incidents": ["incident_id", "organisation_id", "employee_id"],
    "injuries": [
        "injury_id",
        "incident_id",
        "employee_id",
        "medical_cost",
        "days_off_work",
    ],
    "claims": ["claim_id", "injury_id", "employee_id", "claim_amount"],
}

DATE_COLUMNS = {
    "organisations": ["created_date"],
    "employees": ["start_date"],
    "incidents": ["incident_date"],
    "injuries": [],
    "claims": ["claim_date"],
}


def transform_table(table_name, df):
    transformed = df.copy()
    transformed.columns = transformed.columns.str.strip()

    text_columns = transformed.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        transformed[column] = transformed[column].astype("string").str.strip()

    for column in INTEGER_COLUMNS[table_name]:
        transformed[column] = pd.to_numeric(transformed[column], errors="raise").astype("int64")

    for column in DATE_COLUMNS[table_name]:
        transformed[column] = pd.to_datetime(
            transformed[column],
            errors="raise",
            format="%Y-%m-%d",
        ).dt.date

    return transformed


def transform_all(dataframes):
    return {
        table_name: transform_table(table_name, df)
        for table_name, df in dataframes.items()
    }

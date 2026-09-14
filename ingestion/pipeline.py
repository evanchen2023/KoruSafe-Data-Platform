from ingestion.extract import extract_all
from ingestion.load_to_postgres import load_all
from ingestion.transform import transform_all
from ingestion.validate import validate_all


def run_pipeline():
    print("Extracting raw source data...")
    raw_dataframes = extract_all()

    print("Validating raw source data...")
    validate_all(raw_dataframes)

    print("Transforming data...")
    transformed_dataframes = transform_all(raw_dataframes)

    print("Loading data into PostgreSQL...")
    load_all(transformed_dataframes)

    print("Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()

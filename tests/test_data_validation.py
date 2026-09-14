import pytest

from ingestion.validate import DataValidationError, validate_all


def test_valid_raw_dataframes_pass_validation(valid_raw_dataframes):
    """A complete, valid source dataset should pass pipeline validation."""

    assert validate_all(valid_raw_dataframes) is True


def test_real_raw_csvs_pass_validation(raw_csvs):
    """Current raw files should pass the same validation used by the pipeline."""

    assert validate_all(raw_csvs) is True


def test_duplicate_primary_key_fails_validation(valid_raw_dataframes):
    """Primary keys must be unique before data is loaded to PostgreSQL."""

    valid_raw_dataframes["organisations"].loc[1, "organisation_id"] = 1

    with pytest.raises(DataValidationError, match="duplicate"):
        validate_all(valid_raw_dataframes)


def test_invalid_date_fails_validation(valid_raw_dataframes):
    """Date fields must be parseable before ingestion continues."""

    valid_raw_dataframes["claims"].loc[0, "claim_date"] = "not-a-date"

    with pytest.raises(DataValidationError, match="claim_date contains invalid dates"):
        validate_all(valid_raw_dataframes)


def test_negative_business_value_fails_validation(valid_raw_dataframes):
    """Counts, costs, days and amounts should not contain invalid negative values."""

    valid_raw_dataframes["injuries"].loc[0, "medical_cost"] = -1

    with pytest.raises(DataValidationError, match="medical_cost cannot be negative"):
        validate_all(valid_raw_dataframes)


def test_broken_foreign_key_fails_validation(valid_raw_dataframes):
    """Child tables must only reference keys that exist in parent tables."""

    valid_raw_dataframes["claims"].loc[0, "injury_id"] = 999999

    with pytest.raises(DataValidationError, match="claims: injury_id"):
        validate_all(valid_raw_dataframes)


def test_wrong_schema_fails_validation(valid_raw_dataframes):
    """Unexpected or missing columns should stop the pipeline early."""

    valid_raw_dataframes["employees"] = valid_raw_dataframes["employees"].drop(
        columns=["department"]
    )

    with pytest.raises(DataValidationError, match="employees: expected columns"):
        validate_all(valid_raw_dataframes)

from ingestion.pipeline import run_pipeline


def test_run_pipeline_calls_steps_in_order(monkeypatch, valid_raw_dataframes):
    """The pipeline should orchestrate extract, validate, transform and load in order."""

    calls = []

    def fake_extract_all():
        calls.append("extract")
        return valid_raw_dataframes

    def fake_validate_all(dataframes):
        calls.append("validate")
        assert dataframes is valid_raw_dataframes
        return True

    def fake_transform_all(dataframes):
        calls.append("transform")
        assert dataframes is valid_raw_dataframes
        return dataframes

    def fake_load_all(dataframes):
        calls.append("load")
        assert dataframes is valid_raw_dataframes

    monkeypatch.setattr("ingestion.pipeline.extract_all", fake_extract_all)
    monkeypatch.setattr("ingestion.pipeline.validate_all", fake_validate_all)
    monkeypatch.setattr("ingestion.pipeline.transform_all", fake_transform_all)
    monkeypatch.setattr("ingestion.pipeline.load_all", fake_load_all)

    run_pipeline()

    assert calls == ["extract", "validate", "transform", "load"]

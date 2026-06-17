from traceleak.model_output_contract import MODEL_OUTPUT_FORMAT, model_output_record


def test_model_output_format() -> None:
    assert MODEL_OUTPUT_FORMAT == "traceleak.model_output.v1"


def test_model_output_builder_is_callable() -> None:
    assert callable(model_output_record)


def test_model_output_record_has_output_id() -> None:
    record = model_output_record(
        sample_id="sample_000001",
        model_id="model_000001",
        consumer_mode="sequence",
        prediction={"class": "metadata_even"},
        confidence=0.75,
        output_id="output_000001",
    )
    assert record["output_id"] == "output_000001"

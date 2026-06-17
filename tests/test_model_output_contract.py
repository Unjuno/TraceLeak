from traceleak.model_output_contract import MODEL_OUTPUT_FORMAT, model_output_record


def test_model_output_format() -> None:
    assert MODEL_OUTPUT_FORMAT == "traceleak.model_output.v1"


def test_model_output_builder_is_callable() -> None:
    assert callable(model_output_record)

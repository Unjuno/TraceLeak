from traceleak.model_output_contract import MODEL_OUTPUT_FORMAT


def test_model_output_format() -> None:
    assert MODEL_OUTPUT_FORMAT == "traceleak.model_output.v1"

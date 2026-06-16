import json

from traceleak.level25_index import (
    DEFAULT_LEVEL24_OUTPUT_PATHS,
    EXPECTED_LEVEL25_COMMANDS,
    LEVEL25_INDEX_FORMAT,
    build_level25_index,
    validate_level25_index,
    write_level25_index,
)


def test_level25_index_default_paths() -> None:
    index = build_level25_index()

    assert index["format"] == LEVEL25_INDEX_FORMAT
    assert index["phase"] == "P198"
    assert index["status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL24_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL24_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL25_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level25_index(index)


def test_level25_index_writer(tmp_path) -> None:
    index = build_level25_index()
    path = tmp_path / "level25-index.json"

    write_level25_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL25_INDEX_FORMAT

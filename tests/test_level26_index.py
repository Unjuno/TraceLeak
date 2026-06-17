import json

from traceleak.level26_index import (
    DEFAULT_LEVEL25_OUTPUT_PATHS,
    EXPECTED_LEVEL26_COMMANDS,
    LEVEL26_INDEX_FORMAT,
    build_level26_index,
    validate_level26_index,
    write_level26_index,
)


def test_level26_index_default_paths() -> None:
    index = build_level26_index()

    assert index["format"] == LEVEL26_INDEX_FORMAT
    assert index["phase"] == "P203"
    assert index["status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL25_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL25_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL26_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level26_index(index)


def test_level26_index_writer(tmp_path) -> None:
    index = build_level26_index()
    path = tmp_path / "level26-index.json"

    write_level26_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL26_INDEX_FORMAT

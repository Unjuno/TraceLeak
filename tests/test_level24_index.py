import json

from traceleak.level24_index import (
    DEFAULT_LEVEL23_OUTPUT_PATHS,
    EXPECTED_LEVEL24_COMMANDS,
    LEVEL24_INDEX_FORMAT,
    build_level24_index,
    validate_level24_index,
    write_level24_index,
)


def test_level24_index_default_paths() -> None:
    index = build_level24_index()

    assert index["format"] == LEVEL24_INDEX_FORMAT
    assert index["phase"] == "P193"
    assert index["status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL23_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL23_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL24_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level24_index(index)


def test_level24_index_writer(tmp_path) -> None:
    index = build_level24_index()
    path = tmp_path / "level24-index.json"

    write_level24_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL24_INDEX_FORMAT

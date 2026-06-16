import json

from traceleak.level23_index import (
    DEFAULT_LEVEL22_OUTPUT_PATHS,
    EXPECTED_LEVEL23_COMMANDS,
    LEVEL23_INDEX_FORMAT,
    build_level23_index,
    validate_level23_index,
    write_level23_index,
)


def test_level23_index_default_paths() -> None:
    index = build_level23_index()

    assert index["format"] == LEVEL23_INDEX_FORMAT
    assert index["phase"] == "P188"
    assert index["status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL22_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL22_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL23_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level23_index(index)


def test_level23_index_writer(tmp_path) -> None:
    index = build_level23_index()
    path = tmp_path / "level23-index.json"

    write_level23_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL23_INDEX_FORMAT

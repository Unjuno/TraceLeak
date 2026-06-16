import json

import pytest

from traceleak.level22_index import (
    DEFAULT_LEVEL21_OUTPUT_PATHS,
    EXPECTED_LEVEL22_COMMANDS,
    LEVEL22_INDEX_FORMAT,
    Level22IndexError,
    build_level22_index,
    validate_level22_index,
    write_level22_index,
)


def test_level22_index_default_paths() -> None:
    index = build_level22_index()

    assert index["format"] == LEVEL22_INDEX_FORMAT
    assert index["phase"] == "P183"
    assert index["status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL21_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL21_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL22_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level22_index(index)


def test_level22_index_rejects_absolute_path() -> None:
    with pytest.raises(Level22IndexError, match="relative"):
        build_level22_index(output_paths=["/reports/local/bad.json"])


def test_level22_index_rejects_parent_directory_path() -> None:
    with pytest.raises(Level22IndexError, match="parent-directory"):
        build_level22_index(output_paths=["reports/local/../bad.json"])


def test_level22_index_rejects_content_read_enabled() -> None:
    index = build_level22_index()
    index["flags"]["content_read"] = True

    with pytest.raises(Level22IndexError, match="content_read"):
        validate_level22_index(index)


def test_level22_index_rejects_command_executed_enabled() -> None:
    index = build_level22_index()
    index["flags"]["command_executed"] = True

    with pytest.raises(Level22IndexError, match="command_executed"):
        validate_level22_index(index)


def test_level22_index_writer(tmp_path) -> None:
    index = build_level22_index()
    path = tmp_path / "level22-index.json"

    write_level22_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL22_INDEX_FORMAT

import json

import pytest

from traceleak.level21_status_index import (
    DEFAULT_LEVEL20_OUTPUT_PATHS,
    EXPECTED_LEVEL21_COMMANDS,
    LEVEL21_STATUS_INDEX_FORMAT,
    Level21StatusIndexError,
    build_level21_status_index,
    validate_level21_status_index,
    write_level21_status_index,
)


def test_status_index_default_paths() -> None:
    index = build_level21_status_index()

    assert index["format"] == LEVEL21_STATUS_INDEX_FORMAT
    assert index["phase"] == "P178"
    assert index["status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL20_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL20_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL21_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level21_status_index(index)


def test_status_index_rejects_absolute_path() -> None:
    with pytest.raises(Level21StatusIndexError, match="relative"):
        build_level21_status_index(output_paths=["/reports/local/bad.json"])


def test_status_index_rejects_parent_directory_path() -> None:
    with pytest.raises(Level21StatusIndexError, match="parent-directory"):
        build_level21_status_index(output_paths=["reports/local/../bad.json"])


def test_status_index_rejects_content_read_enabled() -> None:
    index = build_level21_status_index()
    index["flags"]["content_read"] = True

    with pytest.raises(Level21StatusIndexError, match="content_read"):
        validate_level21_status_index(index)


def test_status_index_rejects_command_executed_enabled() -> None:
    index = build_level21_status_index()
    index["flags"]["command_executed"] = True

    with pytest.raises(Level21StatusIndexError, match="command_executed"):
        validate_level21_status_index(index)


def test_status_index_writer(tmp_path) -> None:
    index = build_level21_status_index()
    path = tmp_path / "level21-status-index.json"

    write_level21_status_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL21_STATUS_INDEX_FORMAT

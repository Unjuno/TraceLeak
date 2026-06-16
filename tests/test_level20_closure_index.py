import json

import pytest

from traceleak.level20_closure_index import (
    DEFAULT_LEVEL19_OUTPUT_PATHS,
    EXPECTED_LEVEL20_COMMANDS,
    LEVEL20_CLOSURE_INDEX_FORMAT,
    Level20ClosureIndexError,
    build_level20_closure_index,
    validate_level20_closure_index,
    write_level20_closure_index,
)


def test_closure_index_default_paths() -> None:
    index = build_level20_closure_index()

    assert index["format"] == LEVEL20_CLOSURE_INDEX_FORMAT
    assert index["phase"] == "P173"
    assert index["closure_status"] == "pending_local_validation"
    assert index["output_paths"] == DEFAULT_LEVEL19_OUTPUT_PATHS
    assert index["path_count"] == len(DEFAULT_LEVEL19_OUTPUT_PATHS)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL20_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level20_closure_index(index)


def test_closure_index_rejects_absolute_path() -> None:
    with pytest.raises(Level20ClosureIndexError, match="relative"):
        build_level20_closure_index(output_paths=["/reports/local/bad.json"])


def test_closure_index_rejects_parent_directory_path() -> None:
    with pytest.raises(Level20ClosureIndexError, match="parent-directory"):
        build_level20_closure_index(output_paths=["reports/local/../bad.json"])


def test_closure_index_rejects_content_read_enabled() -> None:
    index = build_level20_closure_index()
    index["flags"]["content_read"] = True

    with pytest.raises(Level20ClosureIndexError, match="content_read"):
        validate_level20_closure_index(index)


def test_closure_index_rejects_command_executed_enabled() -> None:
    index = build_level20_closure_index()
    index["flags"]["command_executed"] = True

    with pytest.raises(Level20ClosureIndexError, match="command_executed"):
        validate_level20_closure_index(index)


def test_closure_index_writer(tmp_path) -> None:
    index = build_level20_closure_index()
    path = tmp_path / "level20-closure-index.json"

    write_level20_closure_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL20_CLOSURE_INDEX_FORMAT

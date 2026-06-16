import json

import pytest

from traceleak.level18_archive_index import (
    DEFAULT_ARCHIVE_FAMILIES,
    EXPECTED_LEVEL18_COMMANDS,
    LEVEL18_ARCHIVE_INDEX_FORMAT,
    Level18ArchiveIndexError,
    build_level18_archive_index,
    validate_level18_archive_index,
    write_level18_archive_index,
)


def test_archive_index_default_families() -> None:
    index = build_level18_archive_index()

    assert index["format"] == LEVEL18_ARCHIVE_INDEX_FORMAT
    assert index["phase"] == "P163"
    assert index["archive_status"] == "pending_local_validation"
    assert index["family_count"] == len(DEFAULT_ARCHIVE_FAMILIES)
    assert index["path_count"] == sum(len(family["paths"]) for family in DEFAULT_ARCHIVE_FAMILIES)
    assert index["expected_validation_commands"] == EXPECTED_LEVEL18_COMMANDS
    assert index["flags"]["review_only"] is True
    assert index["flags"]["path_only"] is True
    assert index["flags"]["content_read"] is False
    assert index["flags"]["command_executed"] is False
    assert index["flags"]["claim_generated"] is False
    validate_level18_archive_index(index)


def test_archive_index_rejects_absolute_path() -> None:
    families = [{"family": "bad", "paths": ["/reports/local/bad.json"]}]

    with pytest.raises(Level18ArchiveIndexError, match="relative"):
        build_level18_archive_index(families=families)


def test_archive_index_rejects_parent_directory_path() -> None:
    families = [{"family": "bad", "paths": ["reports/local/../bad.json"]}]

    with pytest.raises(Level18ArchiveIndexError, match="parent-directory"):
        build_level18_archive_index(families=families)


def test_archive_index_rejects_content_read_enabled() -> None:
    index = build_level18_archive_index()
    index["flags"]["content_read"] = True

    with pytest.raises(Level18ArchiveIndexError, match="content_read"):
        validate_level18_archive_index(index)


def test_archive_index_rejects_command_executed_enabled() -> None:
    index = build_level18_archive_index()
    index["flags"]["command_executed"] = True

    with pytest.raises(Level18ArchiveIndexError, match="command_executed"):
        validate_level18_archive_index(index)


def test_archive_index_writer(tmp_path) -> None:
    index = build_level18_archive_index()
    path = tmp_path / "level18-archive-index.json"

    write_level18_archive_index(path, index)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL18_ARCHIVE_INDEX_FORMAT

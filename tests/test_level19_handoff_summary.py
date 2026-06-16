import json

import pytest

from traceleak.level18_archive_index import build_level18_archive_index
from traceleak.level19_summary import (
    EXPECTED_LEVEL19_COMMANDS,
    LEVEL19_SUMMARY_FORMAT,
    Level19SummaryError,
    build_level19_summary,
    validate_level19_summary,
    write_level19_summary,
)


def test_level19_summary_from_archive_index() -> None:
    summary = build_level19_summary(archive_index=build_level18_archive_index())

    assert summary["format"] == LEVEL19_SUMMARY_FORMAT
    assert summary["phase"] == "P168"
    assert summary["source_index_format"] == "traceleak.level18_archive_index.v1"
    assert summary["summary_status"] == "pending_local_validation"
    assert summary["reviewed_levels"] == [
        "level13",
        "level14",
        "level15",
        "level16",
        "level17",
        "level18",
    ]
    assert summary["expected_validation_commands"] == EXPECTED_LEVEL19_COMMANDS
    assert summary["flags"]["review_only"] is True
    assert summary["flags"]["path_only"] is True
    assert summary["flags"]["content_read"] is False
    assert summary["flags"]["command_executed"] is False
    assert summary["flags"]["claim_generated"] is False
    validate_level19_summary(summary)


def test_level19_summary_rejects_content_read_enabled() -> None:
    summary = build_level19_summary(archive_index=build_level18_archive_index())
    summary["flags"]["content_read"] = True

    with pytest.raises(Level19SummaryError, match="content_read"):
        validate_level19_summary(summary)


def test_level19_summary_rejects_command_executed_enabled() -> None:
    summary = build_level19_summary(archive_index=build_level18_archive_index())
    summary["flags"]["command_executed"] = True

    with pytest.raises(Level19SummaryError, match="command_executed"):
        validate_level19_summary(summary)


def test_level19_summary_writer(tmp_path) -> None:
    summary = build_level19_summary(archive_index=build_level18_archive_index())
    path = tmp_path / "level19-summary.json"

    write_level19_summary(path, summary)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL19_SUMMARY_FORMAT

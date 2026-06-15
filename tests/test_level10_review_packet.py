import json

import pytest

from traceleak.level10_review_packet import (
    LEVEL10_REVIEW_PACKET_FORMAT,
    Level10ReviewPacketError,
    build_level10_review_packet,
    render_level10_review_packet_report,
    validate_level10_review_packet,
    validate_level10_review_packet_report,
    write_level10_review_packet,
    write_level10_review_packet_report,
)
from traceleak.level9_readiness_audit import LEVEL9_READINESS_AUDIT_FORMAT


def audit(*, status: str = "ready"):
    missing = []
    if status == "incomplete":
        missing = [
            {
                "key": "missing",
                "artifact_class": "summary_json",
                "relative_path": "reports/local/missing.json",
                "role": "missing summary",
            }
        ]
    return {
        "format": LEVEL9_READINESS_AUDIT_FORMAT,
        "phase": "P121",
        "source_index_format": "traceleak.level8_artifact_intake_index.v1",
        "source_index_phase": "P116",
        "entry_count": 2,
        "present_count": 1 if missing else 2,
        "missing_count": len(missing),
        "readiness_ratio": 0.5 if missing else 1.0,
        "status": status,
        "missing_artifacts": missing,
        "flags": {"path_only": True, "payload_read": False, "claim_generated": False},
    }


def test_review_packet_marks_ready_for_complete_audit() -> None:
    packet = build_level10_review_packet(readiness_audit=audit())

    assert packet["format"] == LEVEL10_REVIEW_PACKET_FORMAT
    assert packet["phase"] == "P125"
    assert packet["readiness"]["status"] == "ready"
    assert packet["review_items"]["ready_for_next_todo"] is True
    assert packet["allowances"]["review_packet_only"] is True
    assert packet["allowances"]["direct_action_enabled"] is False
    assert packet["allowances"]["content_read_enabled"] is False
    assert packet["allowances"]["claim_enabled"] is False
    validate_level10_review_packet(packet)


def test_review_packet_marks_not_ready_for_incomplete_audit() -> None:
    packet = build_level10_review_packet(readiness_audit=audit(status="incomplete"))

    assert packet["readiness"]["status"] == "incomplete"
    assert packet["review_items"]["ready_for_next_todo"] is False
    assert packet["missing_artifacts"][0]["key"] == "missing"


def test_review_packet_rejects_content_read_enabled() -> None:
    packet = build_level10_review_packet(readiness_audit=audit())
    packet["allowances"]["content_read_enabled"] = True

    with pytest.raises(Level10ReviewPacketError, match="content_read_enabled"):
        validate_level10_review_packet(packet)


def test_review_packet_report_renders_required_sections() -> None:
    packet = build_level10_review_packet(readiness_audit=audit(status="incomplete"))

    markdown = render_level10_review_packet_report(packet)

    assert "# Level 10 Review Packet" in markdown
    assert "## Readiness" in markdown
    assert "## Missing artifacts" in markdown
    assert "Review packet only: `True`" in markdown
    assert "Content read enabled: `False`" in markdown
    assert "Claim enabled: `False`" in markdown
    validate_level10_review_packet_report(markdown)


def test_review_packet_writers(tmp_path) -> None:
    packet = build_level10_review_packet(readiness_audit=audit())
    markdown = render_level10_review_packet_report(packet)
    packet_path = tmp_path / "level10-review-packet.json"
    report_path = tmp_path / "level10-review-packet.md"

    write_level10_review_packet(packet_path, packet)
    write_level10_review_packet_report(report_path, markdown)

    assert json.loads(packet_path.read_text(encoding="utf-8"))["format"] == LEVEL10_REVIEW_PACKET_FORMAT
    assert report_path.read_text(encoding="utf-8").startswith("# Level 10 Review Packet")

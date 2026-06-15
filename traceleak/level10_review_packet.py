"""Level 10 review packet for Level 9 readiness audits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level9_readiness_audit import (
    LEVEL9_READINESS_AUDIT_FORMAT,
    validate_level9_readiness_audit,
)

LEVEL10_REVIEW_PACKET_FORMAT = "traceleak.level10_review_packet.v1"
LEVEL10_REVIEW_PACKET_PHASE = "P125"
LEVEL10_REVIEW_PACKET_REPORT_PHASE = "P126"


class Level10ReviewPacketError(ValueError):
    """Raised when Level 10 review packet data is invalid."""


def build_level10_review_packet(
    *,
    readiness_audit: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a review packet from a validated Level 9 readiness audit."""

    validate_level9_readiness_audit(readiness_audit)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    packet = {
        "format": LEVEL10_REVIEW_PACKET_FORMAT,
        "phase": LEVEL10_REVIEW_PACKET_PHASE,
        "source_audit_format": readiness_audit["format"],
        "source_audit_phase": readiness_audit["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "readiness": {
            "status": readiness_audit["status"],
            "readiness_ratio": readiness_audit["readiness_ratio"],
            "entry_count": readiness_audit["entry_count"],
            "present_count": readiness_audit["present_count"],
            "missing_count": readiness_audit["missing_count"],
        },
        "missing_artifacts": list(readiness_audit["missing_artifacts"]),
        "review_items": {
            "path_only_confirmed": True,
            "payload_read_confirmed_false": readiness_audit["flags"]["payload_read"] is False,
            "claim_generated_confirmed_false": readiness_audit["flags"]["claim_generated"] is False,
            "ready_for_next_todo": readiness_audit["status"] == "ready",
        },
        "allowances": {
            "review_packet_only": True,
            "direct_action_enabled": False,
            "content_read_enabled": False,
            "claim_enabled": False,
        },
    }
    validate_level10_review_packet(packet)
    return packet


def validate_level10_review_packet(packet: dict[str, Any]) -> None:
    """Validate Level 10 review packet shape."""

    if not isinstance(packet, dict):
        raise Level10ReviewPacketError("packet must be an object")
    _eq(packet.get("format"), LEVEL10_REVIEW_PACKET_FORMAT, "packet.format")
    _eq(packet.get("phase"), LEVEL10_REVIEW_PACKET_PHASE, "packet.phase")
    _eq(packet.get("source_audit_format"), LEVEL9_READINESS_AUDIT_FORMAT, "packet.source_audit_format")
    _non_empty(packet.get("reviewer"), "packet.reviewer")
    _non_empty(packet.get("reviewed_at"), "packet.reviewed_at")
    readiness = packet.get("readiness")
    if not isinstance(readiness, dict):
        raise Level10ReviewPacketError("packet.readiness must be an object")
    if readiness.get("status") not in {"ready", "incomplete"}:
        raise Level10ReviewPacketError("packet.readiness.status is invalid")
    ratio = readiness.get("readiness_ratio")
    if not isinstance(ratio, int | float) or ratio < 0 or ratio > 1:
        raise Level10ReviewPacketError("packet.readiness.readiness_ratio must be between 0 and 1")
    for key in ["entry_count", "present_count", "missing_count"]:
        if not isinstance(readiness.get(key), int) or readiness[key] < 0:
            raise Level10ReviewPacketError(f"packet.readiness.{key} must be a non-negative integer")
    _eq(
        readiness["present_count"] + readiness["missing_count"],
        readiness["entry_count"],
        "packet.readiness.counts",
    )
    missing = packet.get("missing_artifacts")
    if not isinstance(missing, list):
        raise Level10ReviewPacketError("packet.missing_artifacts must be a list")
    _eq(len(missing), readiness["missing_count"], "packet.missing_artifacts length")
    review_items = packet.get("review_items")
    if not isinstance(review_items, dict):
        raise Level10ReviewPacketError("packet.review_items must be an object")
    for key in ["path_only_confirmed", "payload_read_confirmed_false", "claim_generated_confirmed_false"]:
        _eq(review_items.get(key), True, f"packet.review_items.{key}")
    expected_ready = readiness["status"] == "ready"
    _eq(review_items.get("ready_for_next_todo"), expected_ready, "packet.review_items.ready_for_next_todo")
    allowances = packet.get("allowances")
    if not isinstance(allowances, dict):
        raise Level10ReviewPacketError("packet.allowances must be an object")
    _eq(allowances.get("review_packet_only"), True, "packet.allowances.review_packet_only")
    for key in ["direct_action_enabled", "content_read_enabled", "claim_enabled"]:
        _eq(allowances.get(key), False, f"packet.allowances.{key}")


def render_level10_review_packet_report(packet: dict[str, Any]) -> str:
    """Render a Markdown report for a Level 10 review packet."""

    validate_level10_review_packet(packet)
    lines = [
        "# Level 10 Review Packet",
        "",
        f"- Phase: `{LEVEL10_REVIEW_PACKET_REPORT_PHASE}`",
        f"- Source audit: `{packet['source_audit_format']}`",
        f"- Reviewer: `{packet['reviewer']}`",
        f"- Reviewed at: `{packet['reviewed_at']}`",
        "",
        "## Readiness",
        "",
        f"- Status: `{packet['readiness']['status']}`",
        f"- Ratio: `{packet['readiness']['readiness_ratio']}`",
        f"- Entries: `{packet['readiness']['entry_count']}`",
        f"- Present: `{packet['readiness']['present_count']}`",
        f"- Missing: `{packet['readiness']['missing_count']}`",
        "",
        "## Missing artifacts",
        "",
    ]
    if packet["missing_artifacts"]:
        for item in packet["missing_artifacts"]:
            lines.append(f"- `{item['key']}`: `{item['relative_path']}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Allowances",
            "",
            "Review packet only: `True`",
            "Direct action enabled: `False`",
            "Content read enabled: `False`",
            "Claim enabled: `False`",
            "",
        ]
    )
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level10_review_packet_report(markdown)
    return markdown


def validate_level10_review_packet_report(markdown: str) -> None:
    """Validate Level 10 review packet Markdown."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level10ReviewPacketError("markdown must be a newline-terminated string")
    for text in [
        "# Level 10 Review Packet",
        "## Readiness",
        "## Missing artifacts",
        "## Allowances",
        "Review packet only: `True`",
        "Direct action enabled: `False`",
        "Content read enabled: `False`",
        "Claim enabled: `False`",
    ]:
        if text not in markdown:
            raise Level10ReviewPacketError(f"missing markdown text: {text}")


def write_level10_review_packet(path: Path, packet: dict[str, Any]) -> None:
    """Write Level 10 review packet JSON."""

    validate_level10_review_packet(packet)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level10_review_packet_report(path: Path, markdown: str) -> None:
    """Write Level 10 review packet Markdown."""

    validate_level10_review_packet_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level10ReviewPacketError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level10ReviewPacketError(f"{name} must be {expected!r}")

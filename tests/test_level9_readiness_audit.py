import json

import pytest

from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
)
from traceleak.level8_artifact_intake import (
    build_level8_artifact_intake_index,
    build_level8_artifact_intake_manifest,
)
from traceleak.level9_readiness_audit import (
    LEVEL9_READINESS_AUDIT_FORMAT,
    Level9ReadinessAuditError,
    build_level9_readiness_audit,
    render_level9_readiness_report,
    validate_level9_readiness_audit,
    validate_level9_readiness_report,
    write_level9_readiness_audit,
    write_level9_readiness_report,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def boundary_plan():
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
    gate = build_level7_review_gate(
        profile_demo_summary=summary,
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )
    contract = build_level7_planning_contract(review_gate=gate)
    return build_level7_artifact_boundary_plan(planning_contract=contract)


def intake_index(tmp_path, *, make_missing: bool):
    present = tmp_path / "reports" / "local" / "present.json"
    present.parent.mkdir(parents=True)
    present.write_text("{}\n", encoding="utf-8")
    if not make_missing:
        second = tmp_path / "reports" / "local" / "second.md"
        second.write_text("# Report\n", encoding="utf-8")
    entries = [
        {
            "key": "present",
            "artifact_class": "summary_json",
            "relative_path": "reports/local/present.json",
            "role": "present summary",
        },
        {
            "key": "second",
            "artifact_class": "markdown_report",
            "relative_path": "reports/local/second.md",
            "role": "second report",
        },
    ]
    manifest = build_level8_artifact_intake_manifest(
        artifact_boundary_plan=boundary_plan(),
        entries=entries,
    )
    return build_level8_artifact_intake_index(manifest=manifest, root_dir=tmp_path)


def test_level9_audit_marks_incomplete_when_missing(tmp_path) -> None:
    audit = build_level9_readiness_audit(intake_index=intake_index(tmp_path, make_missing=True))

    assert audit["format"] == LEVEL9_READINESS_AUDIT_FORMAT
    assert audit["phase"] == "P121"
    assert audit["status"] == "incomplete"
    assert audit["entry_count"] == 2
    assert audit["present_count"] == 1
    assert audit["missing_count"] == 1
    assert audit["readiness_ratio"] == 0.5
    assert audit["missing_artifacts"][0]["key"] == "second"
    assert audit["flags"]["payload_read"] is False
    assert audit["flags"]["claim_generated"] is False
    validate_level9_readiness_audit(audit)


def test_level9_audit_marks_ready_when_complete(tmp_path) -> None:
    audit = build_level9_readiness_audit(intake_index=intake_index(tmp_path, make_missing=False))

    assert audit["status"] == "ready"
    assert audit["missing_count"] == 0
    assert audit["readiness_ratio"] == 1.0
    assert audit["missing_artifacts"] == []


def test_level9_audit_rejects_claim_flag() -> None:
    audit = {
        "format": LEVEL9_READINESS_AUDIT_FORMAT,
        "phase": "P121",
        "source_index_format": "traceleak.level8_artifact_intake_index.v1",
        "source_index_phase": "P116",
        "entry_count": 1,
        "present_count": 1,
        "missing_count": 0,
        "readiness_ratio": 1.0,
        "status": "ready",
        "missing_artifacts": [],
        "flags": {"path_only": True, "payload_read": False, "claim_generated": True},
    }

    with pytest.raises(Level9ReadinessAuditError, match="claim_generated"):
        validate_level9_readiness_audit(audit)


def test_level9_report_renders_required_sections(tmp_path) -> None:
    audit = build_level9_readiness_audit(intake_index=intake_index(tmp_path, make_missing=True))

    markdown = render_level9_readiness_report(audit)

    assert "# Level 9 Readiness Audit" in markdown
    assert "## Missing artifacts" in markdown
    assert "## Boundary" in markdown
    assert "Payload read: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level9_readiness_report(markdown)


def test_level9_writers(tmp_path) -> None:
    audit = build_level9_readiness_audit(intake_index=intake_index(tmp_path, make_missing=False))
    markdown = render_level9_readiness_report(audit)
    audit_path = tmp_path / "level9-readiness-audit.json"
    report_path = tmp_path / "level9-readiness-report.md"

    write_level9_readiness_audit(audit_path, audit)
    write_level9_readiness_report(report_path, markdown)

    assert json.loads(audit_path.read_text(encoding="utf-8"))["format"] == LEVEL9_READINESS_AUDIT_FORMAT
    assert report_path.read_text(encoding="utf-8").startswith("# Level 9 Readiness Audit")

import json

import pytest

from traceleak.level13_closure import LEVEL13_HANDOFF_INVENTORY_FORMAT
from traceleak.level14_completeness import (
    LEVEL14_COMPLETENESS_AUDIT_FORMAT,
    Level14CompletenessError,
    REQUIRED_HANDOFF_FAMILIES,
    build_level14_completeness_audit,
    validate_level14_completeness_audit,
    write_level14_completeness_audit,
)


def inventory(*, omit_family: str | None = None):
    families = [
        {
            "family": family,
            "role": f"{family} artifacts",
            "paths": [f"reports/local/{family}/artifact.json"],
        }
        for family in REQUIRED_HANDOFF_FAMILIES
        if family != omit_family
    ]
    return {
        "format": LEVEL13_HANDOFF_INVENTORY_FORMAT,
        "phase": "P138",
        "closure_manifest_format": "traceleak.level13_closure_manifest.v1",
        "closure_manifest_phase": "P137",
        "closure_status": "ready_for_handoff",
        "families": families,
        "flags": {
            "path_only": True,
            "content_read": False,
            "claim_generated": False,
        },
    }


def test_completeness_audit_complete_inventory() -> None:
    audit = build_level14_completeness_audit(handoff_inventory=inventory())

    assert audit["format"] == LEVEL14_COMPLETENESS_AUDIT_FORMAT
    assert audit["phase"] == "P143"
    assert audit["completeness_status"] == "complete"
    assert audit["family_count"] == len(REQUIRED_HANDOFF_FAMILIES)
    assert audit["path_count"] == len(REQUIRED_HANDOFF_FAMILIES)
    assert audit["missing_required_families"] == []
    assert audit["flags"]["path_only"] is True
    assert audit["flags"]["content_read"] is False
    assert audit["flags"]["claim_generated"] is False
    validate_level14_completeness_audit(audit)


def test_completeness_audit_incomplete_inventory() -> None:
    audit = build_level14_completeness_audit(
        handoff_inventory=inventory(omit_family="level10_review"),
    )

    assert audit["completeness_status"] == "incomplete"
    assert audit["missing_required_families"] == ["level10_review"]


def test_completeness_audit_rejects_content_read_enabled() -> None:
    audit = build_level14_completeness_audit(handoff_inventory=inventory())
    audit["flags"]["content_read"] = True

    with pytest.raises(Level14CompletenessError, match="content_read"):
        validate_level14_completeness_audit(audit)


def test_completeness_audit_rejects_claim_generated_enabled() -> None:
    audit = build_level14_completeness_audit(handoff_inventory=inventory())
    audit["flags"]["claim_generated"] = True

    with pytest.raises(Level14CompletenessError, match="claim_generated"):
        validate_level14_completeness_audit(audit)


def test_completeness_audit_writer(tmp_path) -> None:
    audit = build_level14_completeness_audit(handoff_inventory=inventory())
    path = tmp_path / "level14-completeness-audit.json"

    write_level14_completeness_audit(path, audit)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL14_COMPLETENESS_AUDIT_FORMAT

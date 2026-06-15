from traceleak.level13_closure import LEVEL13_HANDOFF_INVENTORY_FORMAT
from traceleak.level14_completeness import (
    REQUIRED_HANDOFF_FAMILIES,
    build_level14_completeness_audit,
    render_level14_completeness_report,
    validate_level14_completeness_report,
    write_level14_completeness_report,
)


def inventory():
    return {
        "format": LEVEL13_HANDOFF_INVENTORY_FORMAT,
        "phase": "P138",
        "closure_manifest_format": "traceleak.level13_closure_manifest.v1",
        "closure_manifest_phase": "P137",
        "closure_status": "ready_for_handoff",
        "families": [
            {
                "family": family,
                "role": f"{family} artifacts",
                "paths": [f"reports/local/{family}/artifact.json"],
            }
            for family in REQUIRED_HANDOFF_FAMILIES
        ],
        "flags": {"path_only": True, "content_read": False, "claim_generated": False},
    }


def test_completeness_report_renders_required_sections() -> None:
    audit = build_level14_completeness_audit(handoff_inventory=inventory())

    markdown = render_level14_completeness_report(audit)

    assert "# Level 14 Completeness Report" in markdown
    assert "## Required families" in markdown
    assert "## Missing families" in markdown
    assert "## Handoff family counts" in markdown
    assert "## Path-only boundary" in markdown
    assert "Path only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level14_completeness_report(markdown)


def test_completeness_report_writer(tmp_path) -> None:
    audit = build_level14_completeness_audit(handoff_inventory=inventory())
    markdown = render_level14_completeness_report(audit)
    path = tmp_path / "level14-completeness-report.md"

    write_level14_completeness_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 14 Completeness Report")

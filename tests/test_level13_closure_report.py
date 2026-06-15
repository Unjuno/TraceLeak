from tests.test_level13_closure_manifest import checkpoint
from traceleak.level13_closure import (
    build_level13_closure_manifest,
    build_level13_handoff_inventory,
    render_level13_closure_report,
    validate_level13_closure_report,
    write_level13_closure_report,
)


def closure_artifacts():
    manifest = build_level13_closure_manifest(review_checkpoint=checkpoint())
    inventory = build_level13_handoff_inventory(closure_manifest=manifest)
    return manifest, inventory


def test_closure_report_renders_required_sections() -> None:
    manifest, inventory = closure_artifacts()

    markdown = render_level13_closure_report(
        closure_manifest=manifest,
        handoff_inventory=inventory,
    )

    assert "# Level 13 Closure Report" in markdown
    assert "## Required preconditions" in markdown
    assert "## Handoff inventory summary" in markdown
    assert "## Review-only boundary" in markdown
    assert "Closure only: `True`" in markdown
    assert "Path-only inventory: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level13_closure_report(markdown)


def test_closure_report_writer(tmp_path) -> None:
    manifest, inventory = closure_artifacts()
    markdown = render_level13_closure_report(
        closure_manifest=manifest,
        handoff_inventory=inventory,
    )
    path = tmp_path / "level13-closure-report.md"

    write_level13_closure_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 13 Closure Report")

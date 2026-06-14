from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
)
from traceleak.level8_artifact_intake import (
    build_level8_artifact_intake_index,
    build_level8_artifact_intake_manifest,
    render_level8_artifact_intake_report,
    validate_level8_artifact_intake_report,
    write_level8_artifact_intake_report,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def manifest_and_index(tmp_path):
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
    gate = build_level7_review_gate(
        profile_demo_summary=summary,
        reviewer="reviewer",
        reviewed_at="2026-06-15T00:00:00Z",
        decision="approve_planning_only",
    )
    contract = build_level7_planning_contract(review_gate=gate)
    boundary = build_level7_artifact_boundary_plan(planning_contract=contract)
    present = tmp_path / "reports" / "local" / "present.json"
    present.parent.mkdir(parents=True)
    present.write_text("{}\n", encoding="utf-8")
    manifest = build_level8_artifact_intake_manifest(
        artifact_boundary_plan=boundary,
        entries=[
            {
                "key": "present",
                "artifact_class": "summary_json",
                "relative_path": "reports/local/present.json",
                "role": "present summary",
            },
            {
                "key": "missing",
                "artifact_class": "markdown_report",
                "relative_path": "reports/local/missing.md",
                "role": "missing report",
            },
        ],
    )
    index = build_level8_artifact_intake_index(manifest=manifest, root_dir=tmp_path)
    return manifest, index


def test_level8_report_renders_required_sections(tmp_path) -> None:
    manifest, index = manifest_and_index(tmp_path)

    markdown = render_level8_artifact_intake_report(manifest=manifest, index=index)

    assert "# Level 8 Artifact Intake Report" in markdown
    assert "## Intake manifest status" in markdown
    assert "## Accepted artifact classes" in markdown
    assert "## Rejected artifact classes" in markdown
    assert "Payload contents were not read." in markdown
    assert "No claim was generated." in markdown
    assert "Artifacts remain under `reports/local/`." in markdown
    validate_level8_artifact_intake_report(markdown)


def test_level8_report_writer(tmp_path) -> None:
    manifest, index = manifest_and_index(tmp_path)
    markdown = render_level8_artifact_intake_report(manifest=manifest, index=index)
    path = tmp_path / "level8-artifact-intake-report.md"

    write_level8_artifact_intake_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 8 Artifact Intake Report")

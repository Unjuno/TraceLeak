import json

from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
)
from traceleak.level8_artifact_intake import (
    LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT,
    build_level8_artifact_intake_index,
    build_level8_artifact_intake_manifest,
    validate_level8_artifact_intake_index,
    write_level8_artifact_intake_index,
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


def test_index_records_existing_and_missing_files_without_reading_payload(tmp_path) -> None:
    present = tmp_path / "reports" / "local" / "present.json"
    present.parent.mkdir(parents=True)
    present.write_text('{"sample": true}\n', encoding="utf-8")
    entries = [
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
    ]
    manifest = build_level8_artifact_intake_manifest(
        artifact_boundary_plan=boundary_plan(),
        entries=entries,
    )

    index = build_level8_artifact_intake_index(manifest=manifest, root_dir=tmp_path)

    assert index["format"] == LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT
    assert index["entry_count"] == 2
    assert index["present_count"] == 1
    assert index["missing_count"] == 1
    assert index["payload_read"] is False
    assert index["claim_generated"] is False
    validate_level8_artifact_intake_index(index)


def test_index_writer(tmp_path) -> None:
    present = tmp_path / "reports" / "local" / "present.json"
    present.parent.mkdir(parents=True)
    present.write_text("{}\n", encoding="utf-8")
    manifest = build_level8_artifact_intake_manifest(
        artifact_boundary_plan=boundary_plan(),
        entries=[
            {
                "key": "present",
                "artifact_class": "summary_json",
                "relative_path": "reports/local/present.json",
                "role": "present summary",
            }
        ],
    )
    index = build_level8_artifact_intake_index(manifest=manifest, root_dir=tmp_path)
    path = tmp_path / "level8-artifact-intake-index.json"

    write_level8_artifact_intake_index(path, index)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["format"] == LEVEL8_ARTIFACT_INTAKE_INDEX_FORMAT
    assert loaded["payload_read"] is False

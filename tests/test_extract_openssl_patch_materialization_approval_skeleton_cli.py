import json
from pathlib import Path

from scripts import extract_openssl_patch_materialization_approval_skeleton as extract_cli


def test_extract_openssl_patch_materialization_approval_skeleton_cli_writes_skeleton(
    tmp_path: Path,
) -> None:
    skeleton = {
        "format": "traceleak.openssl_review_approval_record.v1",
        "report_type": "openssl_review_approval_record",
        "status": "pending_review",
        "decision": "pending",
        "approval_scope": "patch_materialization_only",
        "contract_id": "traceleak.openssl.rsa_keygen.v1",
        "source_pin": "openssl-source-pin-sample",
        "exact_commit_sha": "0123456789abcdef0123456789abcdef01234567",
        "bundle_sha256": "0" * 64,
        "artifact_digests": {
            "bundle_manifest_sha256": "1" * 64,
            "bundle_sha256": "0" * 64,
            "source_edit_proposal_sha256": "2" * 64,
        },
        "reviewer": "",
        "reviewed_at": "",
        "approval_recorded": False,
        "completed_review_recorded": False,
        "patch_materialization_allowed": False,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "approved_proposals": [
            {
                "proposal_id": "proposal-1",
                "group_id": "group-1",
                "target_path": "crypto/rsa/rsa_gen.c",
                "anchor_symbol": "RSA_generate_key_ex",
                "anchor_line": 1,
                "review_status": "pending",
                "decision": "pending",
                "check_results": [
                    {
                        "check_id": check_id,
                        "status": "pending",
                        "comment": "",
                    }
                    for check_id in [
                        "anchor_matches_expected_symbol",
                        "insertion_point_is_after_argument_collection",
                        "no_secret_value_materialized",
                        "redacted_event_fields_only",
                        "no_control_flow_change",
                        "no_error_path_change",
                        "no_key_material_logging",
                        "trace_event_contract_mapping_confirmed",
                    ]
                ],
            }
        ],
        "gates": [
            "source_pin_validated",
            "event_map_validated",
            "layout_inspected",
            "patch_plan_reviewed",
            "stub_spec_reviewed",
            "source_edit_proposal_reviewed",
            "bundle_manifest_validated",
            "artifact_digests_matched",
            "all_event_slots_approved",
            "patch_materialization_only",
            "no_source_mutation",
            "no_patch_application",
            "no_compilation",
            "no_execution",
            "no_raw_secret_capture",
        ],
        "notes": "pending skeleton",
    }
    template = {
        "format": "traceleak.openssl_patch_materialization_approval_template.v1",
        "report_type": "openssl_patch_materialization_approval_template",
        "status": "approval_template_ready",
        "decision": "pending",
        "approval_scope": "patch_materialization_only",
        "contract_id": skeleton["contract_id"],
        "source_pin": skeleton["source_pin"],
        "exact_commit_sha": skeleton["exact_commit_sha"],
        "bundle_sha256": skeleton["bundle_sha256"],
        "artifact_digests": skeleton["artifact_digests"],
        "reviewer": "",
        "reviewed_at": "",
        "approval_recorded": False,
        "completed_review_recorded": False,
        "patch_materialization_allowed": False,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "approval_record_skeleton": skeleton,
        "gates": [
            "source_edit_proposal_loaded",
            "bundle_manifest_loaded",
            "artifact_digests_bound",
            "approval_record_skeleton_created",
            "reviewer_left_blank",
            "reviewed_at_left_blank",
            "no_approval_recorded",
            "patch_materialization_not_allowed",
            "no_source_mutation",
            "no_patch_application",
            "no_compilation",
            "no_execution",
            "no_raw_secret_capture",
        ],
        "instructions": ["pending template"],
    }
    template_path = tmp_path / "template.json"
    out_path = tmp_path / "skeleton.json"
    template_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    old_parse = extract_cli.parse_args
    extract_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "template": template_path,
            "out": out_path,
        },
    )()
    try:
        assert extract_cli.main() == 0
    finally:
        extract_cli.parse_args = old_parse

    extracted = json.loads(out_path.read_text(encoding="utf-8"))
    assert extracted == skeleton
    assert extracted["decision"] == "pending"
    assert extracted["approval_recorded"] is False
    assert extracted["patch_materialization_allowed"] is False

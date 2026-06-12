import json
import subprocess
from pathlib import Path

import pytest

from scripts import validate_openssl_patch_materialization_gate as gate_cli
from traceleak.openssl_human_review_checklist import REQUIRED_CHECK_IDS
from traceleak.openssl_instrumentation_chain import (
    run_openssl_instrumentation_dry_run_chain,
    write_openssl_instrumentation_chain_outputs,
)
from traceleak.openssl_patch_materialization_gate import (
    OpenSSLPatchMaterializationGateError,
    build_openssl_patch_materialization_preflight_gate,
    expected_openssl_patch_materialization_artifact_digests,
    openssl_patch_materialization_preflight_gate_markdown,
    validate_openssl_review_approval_record,
)
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest

TEMPLATE = Path("examples/openssl_preflight/openssl_source_pin_sample.json")
EVENT_MAP = Path("examples/openssl_preflight/openssl_rsa_keygen_event_map_sample.json")
CONTRACT = Path("examples/openssl_trace_contract/openssl_rsa_keygen_trace_contract_sample.json")
EVENT_STREAM = Path("examples/openssl_trace_events/openssl_rsa_keygen_redacted_event_stream_sample.jsonl")


def init_worktree(path: Path) -> None:
    (path / "crypto" / "rsa").mkdir(parents=True)
    (path / "crypto" / "bn").mkdir(parents=True)
    (path / "crypto" / "rsa" / "rsa_gen.c").write_text(
        "int RSA_generate_key_ex(void);\n"
        "int ossl_rsa_generate_multi_prime_key(void);\n"
        "static int rsa_keygen(void);\n"
        "int RSA_generate_key_ex(void) { return 1; }\n",
        encoding="utf-8",
    )
    (path / "crypto" / "bn" / "bn_prime.c").write_text(
        "int BN_generate_prime_ex2(void);\n"
        "int BN_generate_prime_ex(void);\n"
        "static int probable_prime(void *rnd,\n"
        "                              int bits);\n"
        "static int bn_is_prime_int(void *w,\n"
        "                           int checks);\n"
        "int ossl_bn_check_prime(void);\n"
        "int ossl_bn_check_generated_prime(void);\n"
        "static int probable_prime(void) { return 1; }\n"
        "static int bn_is_prime_int(void) { return 1; }\n"
        "int ossl_bn_check_generated_prime(void) { return 1; }\n",
        encoding="utf-8",
    )
    run_git(path, "init")
    run_git(path, "config", "user.email", "traceleak@example.invalid")
    run_git(path, "config", "user.name", "TraceLeak Test")
    run_git(path, "add", ".")
    run_git(path, "commit", "-m", "initial")


def run_git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, text=True)


def make_source_pin(tmp_path: Path) -> Path:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)
    source_pin_path = tmp_path / "openssl_source_pin.json"
    write_pinned_manifest(source_pin_path, manifest)
    return source_pin_path


def make_bundle(tmp_path: Path) -> Path:
    source_pin = make_source_pin(tmp_path)
    report = run_openssl_instrumentation_dry_run_chain(
        source_pin_path=source_pin,
        event_map_path=EVENT_MAP,
        contract_path=CONTRACT,
        event_stream_path=EVENT_STREAM,
    )
    bundle_dir = tmp_path / "bundle"
    write_openssl_instrumentation_chain_outputs(bundle_dir, report)
    return bundle_dir


def load_gate_inputs(bundle_dir: Path) -> tuple[dict, dict]:
    source_edit = json.loads((bundle_dir / "openssl_source_edit_proposal.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (bundle_dir / "openssl_instrumentation_bundle_manifest.json").read_text(encoding="utf-8")
    )
    return source_edit, manifest


def make_approval_record(source_edit: dict, manifest: dict) -> dict:
    return {
        "format": "traceleak.openssl_review_approval_record.v1",
        "report_type": "openssl_review_approval_record",
        "status": "review_approved",
        "decision": "approved",
        "approval_scope": "patch_materialization_only",
        "contract_id": manifest["contract_id"],
        "source_pin": manifest["source_pin"],
        "exact_commit_sha": source_edit["exact_commit_sha"],
        "bundle_sha256": manifest["bundle_sha256"],
        "artifact_digests": expected_openssl_patch_materialization_artifact_digests(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
        ),
        "reviewer": "TraceLeak Human Reviewer",
        "reviewed_at": "2026-06-13T00:00:00+00:00",
        "approval_recorded": True,
        "completed_review_recorded": True,
        "patch_materialization_allowed": True,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "approved_proposals": [approved_proposal(item) for item in source_edit["proposals"]],
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
        "notes": "Approved for patch materialization preflight only.",
    }


def approved_proposal(proposal: dict) -> dict:
    return {
        "proposal_id": proposal["proposal_id"],
        "group_id": proposal["group_id"],
        "target_path": proposal["target_path"],
        "anchor_symbol": proposal["anchor_symbol"],
        "anchor_line": proposal["anchor_line"],
        "review_status": "reviewed",
        "decision": "approved",
        "check_results": [
            {"check_id": check_id, "status": "passed", "comment": "reviewed and accepted"}
            for check_id in REQUIRED_CHECK_IDS
        ],
    }


def test_patch_materialization_gate_accepts_complete_approved_record(tmp_path: Path) -> None:
    source_edit, manifest = load_gate_inputs(make_bundle(tmp_path))
    approval = make_approval_record(source_edit, manifest)

    gate = build_openssl_patch_materialization_preflight_gate(
        source_edit_proposal=source_edit,
        bundle_manifest=manifest,
        approval_record=approval,
    )
    markdown = openssl_patch_materialization_preflight_gate_markdown(gate)

    assert gate["status"] == "patch_materialization_preflight_passed"
    assert gate["patch_materialization_allowed"] is True
    assert gate["patch_application_allowed"] is False
    assert gate["execution_allowed"] is False
    assert gate["raw_secret_capture_allowed"] is False
    assert gate["approved_proposal_count"] == len(source_edit["proposals"])
    assert "TraceLeak OpenSSL Patch Materialization Preflight Gate" in markdown


def test_review_approval_record_rejects_missing_approval_record(tmp_path: Path) -> None:
    source_edit, manifest = load_gate_inputs(make_bundle(tmp_path))

    with pytest.raises(OpenSSLPatchMaterializationGateError, match="format"):
        validate_openssl_review_approval_record(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
            approval_record={},
        )


def test_review_approval_record_rejects_wrong_bundle_digest(tmp_path: Path) -> None:
    source_edit, manifest = load_gate_inputs(make_bundle(tmp_path))
    approval = make_approval_record(source_edit, manifest)
    approval["bundle_sha256"] = "0" * 64

    with pytest.raises(OpenSSLPatchMaterializationGateError, match="bundle_sha256"):
        validate_openssl_review_approval_record(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
            approval_record=approval,
        )


def test_review_approval_record_rejects_partial_approved_proposals(tmp_path: Path) -> None:
    source_edit, manifest = load_gate_inputs(make_bundle(tmp_path))
    approval = make_approval_record(source_edit, manifest)
    approval["approved_proposals"] = approval["approved_proposals"][:-1]

    with pytest.raises(OpenSSLPatchMaterializationGateError, match="approved_proposals"):
        validate_openssl_review_approval_record(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
            approval_record=approval,
        )


def test_review_approval_record_rejects_non_passed_check(tmp_path: Path) -> None:
    source_edit, manifest = load_gate_inputs(make_bundle(tmp_path))
    approval = make_approval_record(source_edit, manifest)
    approval["approved_proposals"][0]["check_results"][0]["status"] = "pending"

    with pytest.raises(OpenSSLPatchMaterializationGateError, match="status"):
        validate_openssl_review_approval_record(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
            approval_record=approval,
        )


def test_validate_openssl_patch_materialization_gate_cli_writes_json(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    source_edit, manifest = load_gate_inputs(bundle_dir)
    approval_path = tmp_path / "approval.json"
    out = tmp_path / "gate.json"
    approval_path.write_text(
        json.dumps(make_approval_record(source_edit, manifest), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    old_parse = gate_cli.parse_args
    gate_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_edit": bundle_dir / "openssl_source_edit_proposal.json",
            "manifest": bundle_dir / "openssl_instrumentation_bundle_manifest.json",
            "approval_record": approval_path,
            "out": out,
            "format": "json",
        },
    )()
    try:
        assert gate_cli.main() == 0
    finally:
        gate_cli.parse_args = old_parse

    gate = json.loads(out.read_text(encoding="utf-8"))
    assert gate["status"] == "patch_materialization_preflight_passed"
    assert gate["patch_materialization_allowed"] is True
    assert gate["patch_application_allowed"] is False

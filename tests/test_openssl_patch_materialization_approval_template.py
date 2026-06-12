import json
import subprocess
from pathlib import Path

import pytest

from scripts import build_openssl_patch_materialization_review_template as template_cli
from traceleak.openssl_instrumentation_chain import (
    run_openssl_instrumentation_dry_run_chain,
    write_openssl_instrumentation_chain_outputs,
)
from traceleak.openssl_patch_materialization_approval_template import (
    OpenSSLPatchMaterializationApprovalTemplateError,
    build_openssl_patch_materialization_approval_template,
    openssl_patch_materialization_approval_template_markdown,
    validate_openssl_patch_materialization_approval_template,
)
from traceleak.openssl_patch_materialization_gate import (
    OpenSSLPatchMaterializationGateError,
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


def load_template_inputs(bundle_dir: Path) -> tuple[dict, dict]:
    source_edit = json.loads((bundle_dir / "openssl_source_edit_proposal.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (bundle_dir / "openssl_instrumentation_bundle_manifest.json").read_text(encoding="utf-8")
    )
    return source_edit, manifest


def test_build_openssl_patch_materialization_approval_template_is_pending(tmp_path: Path) -> None:
    source_edit, manifest = load_template_inputs(make_bundle(tmp_path))

    template = build_openssl_patch_materialization_approval_template(
        source_edit_proposal=source_edit,
        bundle_manifest=manifest,
    )
    markdown = openssl_patch_materialization_approval_template_markdown(template)
    skeleton = template["approval_record_skeleton"]

    assert template["status"] == "approval_template_ready"
    assert template["decision"] == "pending"
    assert template["approval_recorded"] is False
    assert template["patch_materialization_allowed"] is False
    assert template["patch_application_allowed"] is False
    assert skeleton["format"] == "traceleak.openssl_review_approval_record.v1"
    assert skeleton["status"] == "pending_review"
    assert skeleton["decision"] == "pending"
    assert len(skeleton["approved_proposals"]) == len(source_edit["proposals"])
    assert "TraceLeak OpenSSL Patch Materialization Approval Template" in markdown


def test_template_skeleton_is_not_a_valid_approval_record(tmp_path: Path) -> None:
    source_edit, manifest = load_template_inputs(make_bundle(tmp_path))
    template = build_openssl_patch_materialization_approval_template(
        source_edit_proposal=source_edit,
        bundle_manifest=manifest,
    )

    with pytest.raises(OpenSSLPatchMaterializationGateError, match="status"):
        validate_openssl_review_approval_record(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
            approval_record=template["approval_record_skeleton"],
        )


def test_approval_template_rejects_recorded_approval(tmp_path: Path) -> None:
    source_edit, manifest = load_template_inputs(make_bundle(tmp_path))
    template = build_openssl_patch_materialization_approval_template(
        source_edit_proposal=source_edit,
        bundle_manifest=manifest,
    )
    template["approval_recorded"] = True

    with pytest.raises(OpenSSLPatchMaterializationApprovalTemplateError, match="approval_recorded"):
        validate_openssl_patch_materialization_approval_template(template)


def test_approval_template_rejects_source_material(tmp_path: Path) -> None:
    source_edit, manifest = load_template_inputs(make_bundle(tmp_path))
    template = build_openssl_patch_materialization_approval_template(
        source_edit_proposal=source_edit,
        bundle_manifest=manifest,
    )
    template["approval_record_skeleton"]["approved_proposals"][0]["patch"] = "not allowed"

    with pytest.raises(OpenSSLPatchMaterializationApprovalTemplateError, match="materialized source"):
        validate_openssl_patch_materialization_approval_template(template)


def test_build_openssl_patch_materialization_review_template_cli_writes_json(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    out = tmp_path / "template.json"
    old_parse = template_cli.parse_args
    template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_edit": bundle_dir / "openssl_source_edit_proposal.json",
            "manifest": bundle_dir / "openssl_instrumentation_bundle_manifest.json",
            "out": out,
            "format": "json",
        },
    )()
    try:
        assert template_cli.main() == 0
    finally:
        template_cli.parse_args = old_parse

    template = json.loads(out.read_text(encoding="utf-8"))
    assert template["status"] == "approval_template_ready"
    assert template["approval_recorded"] is False
    assert template["approval_record_skeleton"]["status"] == "pending_review"

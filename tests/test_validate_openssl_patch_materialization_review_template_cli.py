import json
import subprocess
from pathlib import Path

from scripts import build_openssl_patch_materialization_review_template as build_template_cli
from scripts import validate_openssl_patch_materialization_review_template as validate_template_cli
from traceleak.openssl_instrumentation_chain import (
    run_openssl_instrumentation_dry_run_chain,
    write_openssl_instrumentation_chain_outputs,
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


def test_validate_openssl_patch_materialization_review_template_cli_accepts_saved_template(
    tmp_path: Path,
) -> None:
    bundle_dir = make_bundle(tmp_path)
    template_path = tmp_path / "review_template.json"
    old_build_parse = build_template_cli.parse_args
    build_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_edit": bundle_dir / "openssl_source_edit_proposal.json",
            "manifest": bundle_dir / "openssl_instrumentation_bundle_manifest.json",
            "out": template_path,
            "format": "json",
        },
    )()
    try:
        assert build_template_cli.main() == 0
    finally:
        build_template_cli.parse_args = old_build_parse

    old_validate_parse = validate_template_cli.parse_args
    validate_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "template": template_path,
        },
    )()
    try:
        assert validate_template_cli.main() == 0
    finally:
        validate_template_cli.parse_args = old_validate_parse


def test_validate_openssl_patch_materialization_review_template_cli_rejects_edited_template(
    tmp_path: Path,
) -> None:
    bundle_dir = make_bundle(tmp_path)
    template_path = tmp_path / "review_template.json"
    old_build_parse = build_template_cli.parse_args
    build_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_edit": bundle_dir / "openssl_source_edit_proposal.json",
            "manifest": bundle_dir / "openssl_instrumentation_bundle_manifest.json",
            "out": template_path,
            "format": "json",
        },
    )()
    try:
        assert build_template_cli.main() == 0
    finally:
        build_template_cli.parse_args = old_build_parse

    template = json.loads(template_path.read_text(encoding="utf-8"))
    template["approval_recorded"] = True
    template_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    old_validate_parse = validate_template_cli.parse_args
    validate_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "template": template_path,
        },
    )()
    try:
        assert validate_template_cli.main() == 1
    finally:
        validate_template_cli.parse_args = old_validate_parse

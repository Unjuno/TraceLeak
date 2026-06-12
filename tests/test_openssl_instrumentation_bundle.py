import subprocess
from pathlib import Path

import pytest

from scripts import validate_openssl_instrumentation_bundle as validate_bundle_cli
from traceleak.openssl_instrumentation_bundle import (
    OpenSSLInstrumentationBundleError,
    openssl_instrumentation_bundle_markdown,
    validate_openssl_instrumentation_bundle,
    write_openssl_instrumentation_bundle_report_markdown,
)
from traceleak.openssl_instrumentation_chain import (
    run_openssl_instrumentation_dry_run_chain,
    write_openssl_instrumentation_chain_outputs,
)
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest
from traceleak.openssl_trace_contract import load_openssl_trace_contract

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


def test_validate_openssl_instrumentation_bundle_accepts_chain_outputs(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    report = validate_openssl_instrumentation_bundle(
        contract=load_openssl_trace_contract(CONTRACT),
        bundle_dir=bundle_dir,
    )
    markdown = openssl_instrumentation_bundle_markdown(report)

    assert report["status"] == "bundle_validated"
    assert report["event_count"] == 12
    assert report["record_count"] == 4
    assert report["self_check_run_count"] == 4
    assert report["self_check_event_count"] == 20
    assert "TraceLeak OpenSSL Instrumentation Bundle Validation" in markdown
    assert "Status: `bundle_validated`" in markdown


def test_validate_openssl_instrumentation_bundle_rejects_missing_file(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    (bundle_dir / "openssl_model_sequence_sample.json").unlink()

    with pytest.raises(OpenSSLInstrumentationBundleError, match="required bundle file not found"):
        validate_openssl_instrumentation_bundle(
            contract=load_openssl_trace_contract(CONTRACT),
            bundle_dir=bundle_dir,
        )


def test_validate_openssl_instrumentation_bundle_rejects_bad_status(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    summary_path = bundle_dir / "openssl_instrumentation_chain_summary.json"
    summary = summary_path.read_text(encoding="utf-8").replace(
        "dry_run_chain_ready_not_executed", "bad_status"
    )
    summary_path.write_text(summary, encoding="utf-8")

    with pytest.raises(OpenSSLInstrumentationBundleError, match="summary.status"):
        validate_openssl_instrumentation_bundle(
            contract=load_openssl_trace_contract(CONTRACT),
            bundle_dir=bundle_dir,
        )


def test_validate_openssl_instrumentation_bundle_cli_writes_report(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    out = tmp_path / "bundle.md"
    old_parse = validate_bundle_cli.parse_args
    validate_bundle_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "contract": CONTRACT,
            "bundle_dir": bundle_dir,
            "out": out,
            "format": "md",
        },
    )()
    try:
        assert validate_bundle_cli.main() == 0
    finally:
        validate_bundle_cli.parse_args = old_parse

    assert "bundle_validated" in out.read_text(encoding="utf-8")


def test_write_openssl_instrumentation_bundle_report_markdown(tmp_path: Path) -> None:
    report = validate_openssl_instrumentation_bundle(
        contract=load_openssl_trace_contract(CONTRACT),
        bundle_dir=make_bundle(tmp_path),
    )
    out = tmp_path / "bundle.md"

    write_openssl_instrumentation_bundle_report_markdown(out, report)

    assert "TraceLeak OpenSSL Instrumentation Bundle Validation" in out.read_text(encoding="utf-8")

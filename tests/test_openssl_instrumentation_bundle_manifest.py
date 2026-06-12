import json
import subprocess
from pathlib import Path

import pytest

from scripts import build_openssl_instrumentation_bundle_manifest as manifest_cli
from scripts import validate_openssl_instrumentation_bundle_manifest as validate_manifest_cli
from traceleak.openssl_instrumentation_bundle_manifest import (
    OpenSSLInstrumentationBundleManifestError,
    build_openssl_instrumentation_bundle_manifest,
    load_openssl_instrumentation_bundle_manifest,
    openssl_instrumentation_bundle_manifest_markdown,
    validate_openssl_instrumentation_bundle_manifest,
    write_openssl_instrumentation_bundle_manifest_json,
    write_openssl_instrumentation_bundle_manifest_markdown,
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


def test_build_openssl_instrumentation_bundle_manifest_validates_bundle(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    contract = load_openssl_trace_contract(CONTRACT)

    manifest = build_openssl_instrumentation_bundle_manifest(
        contract=contract,
        bundle_dir=bundle_dir,
    )
    markdown = openssl_instrumentation_bundle_manifest_markdown(manifest)

    assert manifest["status"] == "bundle_manifest_ready"
    assert manifest["validation_status"] == "bundle_validated"
    assert manifest["file_count"] == 23
    assert len(manifest["bundle_sha256"]) == 64
    assert "openssl_model_sequence_sample.json" in {entry["relative_path"] for entry in manifest["files"]}
    assert "TraceLeak OpenSSL Instrumentation Bundle Manifest" in markdown
    validate_openssl_instrumentation_bundle_manifest(
        contract=contract,
        bundle_dir=bundle_dir,
        manifest=manifest,
    )


def test_openssl_instrumentation_bundle_manifest_detects_tamper(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    contract = load_openssl_trace_contract(CONTRACT)
    manifest = build_openssl_instrumentation_bundle_manifest(contract=contract, bundle_dir=bundle_dir)
    md_path = bundle_dir / "openssl_trace_sample_acceptance_report.md"
    md_path.write_text(md_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(
        OpenSSLInstrumentationBundleManifestError,
        match="total_size_bytes|bundle_sha256|files",
    ):
        validate_openssl_instrumentation_bundle_manifest(
            contract=contract,
            bundle_dir=bundle_dir,
            manifest=manifest,
        )


def test_write_and_load_openssl_instrumentation_bundle_manifest(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    manifest = build_openssl_instrumentation_bundle_manifest(
        contract=load_openssl_trace_contract(CONTRACT),
        bundle_dir=bundle_dir,
    )
    json_path = tmp_path / "manifest.json"
    md_path = tmp_path / "manifest.md"

    write_openssl_instrumentation_bundle_manifest_json(json_path, manifest)
    write_openssl_instrumentation_bundle_manifest_markdown(md_path, manifest)
    loaded = load_openssl_instrumentation_bundle_manifest(json_path)

    assert loaded == manifest
    assert "Bundle SHA-256" in md_path.read_text(encoding="utf-8")


def test_build_openssl_instrumentation_bundle_manifest_cli_writes_json(tmp_path: Path) -> None:
    bundle_dir = make_bundle(tmp_path)
    out = tmp_path / "manifest.json"
    old_parse = manifest_cli.parse_args
    manifest_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "contract": CONTRACT,
            "bundle_dir": bundle_dir,
            "out": out,
            "format": "json",
        },
    )()
    try:
        assert manifest_cli.main() == 0
    finally:
        manifest_cli.parse_args = old_parse

    manifest = json.loads(out.read_text(encoding="utf-8"))
    assert manifest["status"] == "bundle_manifest_ready"
    assert manifest["validation_status"] == "bundle_validated"


def test_validate_openssl_instrumentation_bundle_manifest_cli_accepts_saved_manifest(
    tmp_path: Path,
) -> None:
    bundle_dir = make_bundle(tmp_path)
    manifest_path = bundle_dir / "openssl_instrumentation_bundle_manifest.json"
    old_parse = validate_manifest_cli.parse_args
    validate_manifest_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "contract": CONTRACT,
            "bundle_dir": bundle_dir,
            "manifest": manifest_path,
        },
    )()
    try:
        assert validate_manifest_cli.main() == 0
    finally:
        validate_manifest_cli.parse_args = old_parse

# ruff: noqa: I001

import json
import subprocess
from pathlib import Path

from scripts import run_openssl_event_emitter_self_check
from traceleak.openssl_event_emitter_artifact import build_openssl_event_emitter_artifact
from traceleak.openssl_event_emitter_self_check import (
    openssl_event_emitter_self_check_markdown,
    run_openssl_event_emitter_self_check as run_self_check,
    write_openssl_event_emitter_self_check_outputs,
)
from traceleak.openssl_instrumentation_stub import build_openssl_instrumentation_stub
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest
from traceleak.openssl_trace_acceptance import validate_openssl_trace_sample_acceptance
from traceleak.openssl_trace_contract import load_openssl_trace_contract
from traceleak.openssl_trace_event_stream import validate_openssl_redacted_event_stream

TEMPLATE = Path("examples/openssl_preflight/openssl_source_pin_sample.json")
EVENT_MAP = Path("examples/openssl_preflight/openssl_rsa_keygen_event_map_sample.json")
CONTRACT = Path("examples/openssl_trace_contract/openssl_rsa_keygen_trace_contract_sample.json")


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


def emitter_artifact(tmp_path: Path) -> dict:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)
    source_pin_path = tmp_path / "openssl_source_pin.json"
    write_pinned_manifest(source_pin_path, manifest)
    stub = build_openssl_instrumentation_stub(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    return build_openssl_event_emitter_artifact(
        contract=load_openssl_trace_contract(CONTRACT),
        instrumentation_stub=stub,
    )


def test_event_emitter_self_check_generates_acceptance_valid_outputs(tmp_path: Path) -> None:
    c = load_openssl_trace_contract(CONTRACT)
    report = run_self_check(contract=c, emitter_artifact=emitter_artifact(tmp_path), run_count=3)
    markdown = openssl_event_emitter_self_check_markdown(report)

    assert report["status"] == "emitter_self_check_passed"
    assert report["run_count"] == 3
    assert report["event_count"] == 15
    assert report["sample_acceptance_status"] == "accepted_redacted_model_sequence_sample"
    assert "TraceLeak OpenSSL Event Emitter Self-Check" in markdown
    runs = report["artifacts"]["event_stream_runs"]
    sample = report["artifacts"]["model_sequence_sample"]
    validate_openssl_redacted_event_stream(c, runs)
    validate_openssl_trace_sample_acceptance(c, sample)
    assert all("prime_candidate" not in key for record in sample["records"] for key in record["token_counts"])


def test_write_event_emitter_self_check_outputs(tmp_path: Path) -> None:
    report = run_self_check(
        contract=load_openssl_trace_contract(CONTRACT),
        emitter_artifact=emitter_artifact(tmp_path),
    )

    paths = write_openssl_event_emitter_self_check_outputs(tmp_path / "out", report)

    assert paths["summary_md"].exists()
    assert paths["event_stream_jsonl"].exists()
    assert paths["model_sequence_sample_json"].exists()
    assert paths["sample_acceptance_md"].exists()
    assert "traceleak.model_sequence.v1" in paths["model_sequence_sample_json"].read_text(encoding="utf-8")


def test_run_openssl_event_emitter_self_check_cli_writes_outputs(tmp_path: Path) -> None:
    artifact_path = tmp_path / "emitter.json"
    artifact_path.write_text(json.dumps(emitter_artifact(tmp_path), sort_keys=True), encoding="utf-8")
    out_dir = tmp_path / "self-check"
    old_parse = run_openssl_event_emitter_self_check.parse_args
    run_openssl_event_emitter_self_check.parse_args = lambda: type(
        "Args",
        (),
        {
            "contract": CONTRACT,
            "emitter_artifact": artifact_path,
            "out_dir": out_dir,
            "run_count": 2,
        },
    )()
    try:
        assert run_openssl_event_emitter_self_check.main() == 0
    finally:
        run_openssl_event_emitter_self_check.parse_args = old_parse

    assert (out_dir / "openssl_event_emitter_self_check_summary.md").exists()
    assert (out_dir / "openssl_event_emitter_self_check_events.jsonl").exists()

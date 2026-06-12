import subprocess
from pathlib import Path

from scripts import run_openssl_instrumentation_chain
from traceleak.openssl_instrumentation_chain import (
    openssl_instrumentation_chain_markdown,
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


def test_openssl_instrumentation_dry_run_chain_summarizes_all_stages(tmp_path: Path) -> None:
    source_pin = make_source_pin(tmp_path)

    report = run_openssl_instrumentation_dry_run_chain(
        source_pin_path=source_pin,
        event_map_path=EVENT_MAP,
        contract_path=CONTRACT,
        event_stream_path=EVENT_STREAM,
    )
    markdown = openssl_instrumentation_chain_markdown(report)

    assert report["status"] == "dry_run_chain_ready_not_executed"
    assert report["execution_allowed"] is False
    assert report["source_mutation_allowed"] is False
    assert report["patch_application_allowed"] is False
    assert report["compile_allowed"] is False
    assert report["raw_secret_capture_allowed"] is False
    assert report["stub_status"] == "stub_spec_ready"
    assert report["source_edit_status"] == "source_edit_proposal_ready"
    assert report["event_emitter_status"] == "emitter_artifact_ready_not_applied"
    assert report["emitter_self_check_status"] == "emitter_self_check_passed"
    assert report["event_stream_status"] == "accepted_redacted_openssl_event_stream"
    assert report["sample_acceptance_status"] == "accepted_redacted_model_sequence_sample"
    assert report["emitter_file_count"] == 2
    assert report["self_check_run_count"] == 4
    assert report["self_check_event_count"] == 20
    assert report["run_count"] == 4
    assert report["event_count"] == 12
    assert report["record_count"] == 4
    assert report["artifacts"]["trace_contract"]["contract_id"] == "openssl-rsa-keygen-trace-contract-sample"
    assert "TraceLeak OpenSSL Instrumentation Dry-Run Chain" in markdown
    assert "Event emitter self-check: `emitter_self_check_passed`" in markdown
    assert "Execution allowed: `false`" in markdown


def test_write_openssl_instrumentation_chain_outputs(tmp_path: Path) -> None:
    source_pin = make_source_pin(tmp_path)
    report = run_openssl_instrumentation_dry_run_chain(
        source_pin_path=source_pin,
        event_map_path=EVENT_MAP,
        contract_path=CONTRACT,
        event_stream_path=EVENT_STREAM,
    )
    paths = write_openssl_instrumentation_chain_outputs(tmp_path / "out", report)

    assert paths["summary_md"].exists()
    assert paths["stub_md"].exists()
    assert paths["source_edit_md"].exists()
    assert paths["event_emitter_md"].exists()
    assert paths["event_stream_md"].exists()
    assert paths["model_sequence_sample_json"].exists()
    assert paths["sample_acceptance_md"].exists()
    assert paths["event_emitter_self_check_md"].exists()
    assert paths["event_emitter_self_check_event_stream_jsonl"].exists()
    assert paths["bundle_manifest_json"].exists()
    assert paths["bundle_manifest_md"].exists()
    assert (paths["event_emitter_dir"] / "traceleak_openssl_event.h").exists()
    assert (paths["event_emitter_dir"] / "traceleak_openssl_event.c").exists()
    assert "dry_run_chain_ready_not_executed" in paths["summary_json"].read_text(encoding="utf-8")
    assert "traceleak.model_sequence.v1" in paths["model_sequence_sample_json"].read_text(encoding="utf-8")
    assert "bundle_manifest_ready" in paths["bundle_manifest_json"].read_text(encoding="utf-8")


def test_run_openssl_instrumentation_chain_cli_writes_outputs(tmp_path: Path) -> None:
    source_pin = make_source_pin(tmp_path)
    out_dir = tmp_path / "chain"
    old_parse = run_openssl_instrumentation_chain.parse_args
    run_openssl_instrumentation_chain.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_pin": source_pin,
            "event_map": EVENT_MAP,
            "contract": CONTRACT,
            "events": EVENT_STREAM,
            "out_dir": out_dir,
        },
    )()
    try:
        assert run_openssl_instrumentation_chain.main() == 0
    finally:
        run_openssl_instrumentation_chain.parse_args = old_parse

    assert (out_dir / "openssl_instrumentation_chain_summary.md").exists()
    assert (out_dir / "openssl_event_emitter_artifact.md").exists()
    assert (out_dir / "openssl_event_emitter_self_check_summary.md").exists()
    assert (out_dir / "openssl_model_sequence_sample.json").exists()
    assert (out_dir / "openssl_instrumentation_bundle_manifest.json").exists()

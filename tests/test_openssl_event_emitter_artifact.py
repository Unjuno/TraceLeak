# ruff: noqa: I001

import json
import subprocess
from pathlib import Path

import pytest

from scripts import build_openssl_event_emitter_artifact
from traceleak.openssl_event_emitter_artifact import (
    HEADER_FILENAME,
    SOURCE_FILENAME,
    OpenSSLEventEmitterArtifactError,
    build_openssl_event_emitter_artifact as build_artifact,
    openssl_event_emitter_artifact_markdown,
    validate_openssl_event_emitter_artifact,
    write_openssl_event_emitter_artifact_files,
    write_openssl_event_emitter_artifact_json,
    write_openssl_event_emitter_artifact_markdown,
)
from traceleak.openssl_instrumentation_stub import build_openssl_instrumentation_stub, write_instrumentation_stub_json
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest
from traceleak.openssl_trace_contract import load_openssl_trace_contract

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


def stub(tmp_path: Path) -> dict:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)
    source_pin_path = tmp_path / "openssl_source_pin.json"
    write_pinned_manifest(source_pin_path, manifest)
    return build_openssl_instrumentation_stub(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)


def test_builds_redacted_event_emitter_artifact(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    markdown = openssl_event_emitter_artifact_markdown(artifact)

    assert artifact["format"] == "traceleak.openssl_event_emitter_artifact.v1"
    assert artifact["status"] == "emitter_artifact_ready_not_applied"
    assert artifact["execution_allowed"] is False
    assert artifact["source_mutation_allowed"] is False
    assert artifact["compile_allowed"] is False
    assert artifact["raw_secret_capture_allowed"] is False
    assert artifact["emitter_api"]["function"] == "traceleak_event"
    assert HEADER_FILENAME in artifact["files"]
    assert SOURCE_FILENAME in artifact["files"]
    assert "value_redacted" in artifact["files"][HEADER_FILENAME]
    assert "value_raw" not in artifact["files"][HEADER_FILENAME]
    assert "TraceLeak OpenSSL Redacted Event Emitter Artifact" in markdown


def test_event_emitter_source_json_escapes_all_string_fields(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    source = artifact["files"][SOURCE_FILENAME]

    assert "tl_write_json_string" in source
    assert "%s" not in source
    assert "tl_write_json_string(out, run_id);" in source
    assert "tl_write_json_string(out, target);" in source
    assert "tl_write_json_string(out, label_key);" in source
    assert "tl_write_json_string(out, value_redacted_key);" in source
    assert "fprintf(out, \"%d\", step);" in source
    assert "fprintf(out, \"%d\", value_redacted_bucket);" in source


def test_write_event_emitter_artifact_files(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    out_dir = tmp_path / "emitter"

    write_openssl_event_emitter_artifact_files(out_dir, artifact)

    assert (out_dir / HEADER_FILENAME).exists()
    assert (out_dir / SOURCE_FILENAME).exists()
    assert "traceleak_event" in (out_dir / HEADER_FILENAME).read_text(encoding="utf-8")


def test_write_event_emitter_artifact_reports_create_parent_directories(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    out_json = tmp_path / "nested" / "artifact.json"
    out_md = tmp_path / "nested" / "artifact.md"

    write_openssl_event_emitter_artifact_json(out_json, artifact)
    write_openssl_event_emitter_artifact_markdown(out_md, artifact)

    assert json.loads(out_json.read_text(encoding="utf-8"))["status"] == "emitter_artifact_ready_not_applied"
    assert "TraceLeak OpenSSL Redacted Event Emitter Artifact" in out_md.read_text(encoding="utf-8")


def test_validate_event_emitter_artifact_rejects_raw_value_field(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    artifact["emitter_api"]["raw_value_field_allowed"] = True

    with pytest.raises(OpenSSLEventEmitterArtifactError, match="raw_value_field_allowed"):
        validate_openssl_event_emitter_artifact(artifact)


def test_validate_event_emitter_artifact_rejects_forbidden_source_term(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    artifact["files"][SOURCE_FILENAME] += "\n/* private_key */\n"

    with pytest.raises(OpenSSLEventEmitterArtifactError, match="private_key"):
        validate_openssl_event_emitter_artifact(artifact)


def test_validate_event_emitter_artifact_rejects_unsafe_string_interpolation(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    artifact["files"][SOURCE_FILENAME] = artifact["files"][SOURCE_FILENAME].replace(
        "tl_write_json_string(out, run_id);",
        "fprintf(out, \"%s\", run_id);",
        1,
    )

    with pytest.raises(OpenSSLEventEmitterArtifactError, match="%s"):
        validate_openssl_event_emitter_artifact(artifact)


def test_validate_event_emitter_artifact_rejects_missing_json_string_writer(tmp_path: Path) -> None:
    artifact = build_artifact(contract=load_openssl_trace_contract(CONTRACT), instrumentation_stub=stub(tmp_path))
    artifact["files"][SOURCE_FILENAME] = artifact["files"][SOURCE_FILENAME].replace(
        "tl_write_json_string",
        "tl_missing_json_string_writer",
    )

    with pytest.raises(OpenSSLEventEmitterArtifactError, match="tl_write_json_string"):
        validate_openssl_event_emitter_artifact(artifact)


def test_build_openssl_event_emitter_artifact_cli_writes_outputs(tmp_path: Path) -> None:
    stub_path = tmp_path / "stub.json"
    out_json = tmp_path / "artifact.json"
    out_dir = tmp_path / "emitter"
    out_report = tmp_path / "artifact.md"
    write_instrumentation_stub_json(stub_path, stub(tmp_path))
    old_parse = build_openssl_event_emitter_artifact.parse_args
    build_openssl_event_emitter_artifact.parse_args = lambda: type(
        "Args",
        (),
        {
            "contract": CONTRACT,
            "stub": stub_path,
            "out_json": out_json,
            "out_dir": out_dir,
            "out_report": out_report,
        },
    )()
    try:
        assert build_openssl_event_emitter_artifact.main() == 0
    finally:
        build_openssl_event_emitter_artifact.parse_args = old_parse

    assert json.loads(out_json.read_text(encoding="utf-8"))["status"] == "emitter_artifact_ready_not_applied"
    assert (out_dir / HEADER_FILENAME).exists()
    assert (out_dir / SOURCE_FILENAME).exists()
    assert "TraceLeak OpenSSL Redacted Event Emitter Artifact" in out_report.read_text(encoding="utf-8")

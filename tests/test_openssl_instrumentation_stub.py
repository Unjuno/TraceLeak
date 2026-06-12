# ruff: noqa: I001

import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_instrumentation_stub import (
    OpenSSLInstrumentationStubError,
    build_openssl_instrumentation_stub,
    instrumentation_stub_markdown,
    validate_openssl_instrumentation_stub,
)
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest


TEMPLATE = Path("examples/openssl_preflight/openssl_source_pin_sample.json")
EVENT_MAP = Path("examples/openssl_preflight/openssl_rsa_keygen_event_map_sample.json")


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


def make_source_pin(tmp_path) -> Path:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)
    source_pin_path = tmp_path / "openssl_source_pin.json"
    write_pinned_manifest(source_pin_path, manifest)
    return source_pin_path


def test_build_openssl_instrumentation_stub(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)

    stub = build_openssl_instrumentation_stub(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    markdown = instrumentation_stub_markdown(stub)

    assert stub["format"] == "traceleak.openssl_instrumentation_stub.v1"
    assert stub["report_type"] == "openssl_instrumentation_stub"
    assert stub["execution_allowed"] is False
    assert stub["source_mutation_allowed"] is False
    assert stub["compile_allowed"] is False
    assert stub["raw_secret_capture_allowed"] is False
    assert stub["stub_api"]["name"] == "traceleak_event"
    assert stub["stub_api"]["value_field"] == "value_redacted"
    assert len(stub["planned_events"]) == 5
    assert "TraceLeak OpenSSL Instrumentation Stub Spec" in markdown
    assert "value_redacted" in markdown


def test_validate_openssl_instrumentation_stub_rejects_raw_capture(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    stub = build_openssl_instrumentation_stub(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    stub["raw_secret_capture_allowed"] = True

    with pytest.raises(OpenSSLInstrumentationStubError, match="raw_secret_capture_allowed"):
        validate_openssl_instrumentation_stub(stub)


def test_validate_openssl_instrumentation_stub_rejects_raw_value_field(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    stub = build_openssl_instrumentation_stub(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    stub["stub_api"]["raw_value_field_allowed"] = True

    with pytest.raises(OpenSSLInstrumentationStubError, match="raw_value_field_allowed"):
        validate_openssl_instrumentation_stub(stub)

# ruff: noqa: I001

import json
import subprocess
import sys
from pathlib import Path

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


def test_define_openssl_instrumentation_stub_cli_writes_markdown(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    output_path = tmp_path / "stub.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/define_openssl_instrumentation_stub.py",
            "--source-pin",
            str(source_pin_path),
            "--event-map",
            str(EVENT_MAP),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "TraceLeak OpenSSL Instrumentation Stub Spec" in markdown
    assert "traceleak_event" in markdown


def test_define_openssl_instrumentation_stub_cli_writes_json(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    output_path = tmp_path / "stub.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/define_openssl_instrumentation_stub.py",
            "--source-pin",
            str(source_pin_path),
            "--event-map",
            str(EVENT_MAP),
            "--out",
            str(output_path),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["format"] == "traceleak.openssl_instrumentation_stub.v1"
    assert payload["stub_api"]["name"] == "traceleak_event"
    assert payload["raw_secret_capture_allowed"] is False


def test_define_openssl_instrumentation_stub_cli_rejects_missing_source_pin(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/define_openssl_instrumentation_stub.py",
            "--source-pin",
            str(tmp_path / "missing.json"),
            "--event-map",
            str(EVENT_MAP),
            "--out",
            str(tmp_path / "stub.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "source pin manifest not found" in result.stderr

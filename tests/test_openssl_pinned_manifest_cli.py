# ruff: noqa: I001

import json
import subprocess
import sys
from pathlib import Path


TEMPLATE = "examples/openssl_preflight/openssl_source_pin_sample.json"


def init_worktree(path: Path) -> None:
    (path / "crypto" / "rsa").mkdir(parents=True)
    (path / "crypto" / "bn").mkdir(parents=True)
    (path / "crypto" / "rsa" / "rsa_gen.c").write_text(
        "int RSA_generate_key_ex(void);\nint rsa_builtin_keygen(void);\n",
        encoding="utf-8",
    )
    (path / "crypto" / "bn" / "bn_prime.c").write_text(
        "int BN_generate_prime_ex(void);\nint BN_check_prime(void);\nint bn_is_prime_int(void);\n",
        encoding="utf-8",
    )
    run_git(path, "init")
    run_git(path, "config", "user.email", "traceleak@example.invalid")
    run_git(path, "config", "user.name", "TraceLeak Test")
    run_git(path, "add", ".")
    run_git(path, "commit", "-m", "initial")


def run_git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, text=True)


def test_generate_openssl_pinned_manifest_cli_writes_manifest(tmp_path) -> None:
    worktree = tmp_path / "worktree"
    output_path = tmp_path / "pinned.json"
    worktree.mkdir()
    init_worktree(worktree)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_openssl_pinned_manifest.py",
            "--template",
            TEMPLATE,
            "--worktree",
            str(worktree),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "pinned"
    assert payload["source"]["exact_commit_sha"]
    assert payload["source"]["dirty"] is False


def test_generate_openssl_pinned_manifest_cli_rejects_missing_worktree(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_openssl_pinned_manifest.py",
            "--template",
            TEMPLATE,
            "--worktree",
            str(tmp_path / "missing"),
            "--out",
            str(tmp_path / "pinned.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "worktree not found" in result.stderr

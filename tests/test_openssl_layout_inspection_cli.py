# ruff: noqa: I001

import subprocess
import sys
from pathlib import Path

from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest


TEMPLATE = Path("examples/openssl_preflight/openssl_source_pin_sample.json")


def init_worktree(path: Path) -> None:
    (path / "crypto" / "rsa").mkdir(parents=True)
    (path / "crypto" / "bn").mkdir(parents=True)
    (path / "crypto" / "rsa" / "rsa_gen.c").write_text(
        "int RSA_generate_key_ex(void);\n"
        "int ossl_rsa_generate_multi_prime_key(void);\n"
        "static int rsa_keygen(void);\n",
        encoding="utf-8",
    )
    (path / "crypto" / "bn" / "bn_prime.c").write_text(
        "int BN_generate_prime_ex2(void);\n"
        "int BN_generate_prime_ex(void);\n"
        "static int probable_prime(void);\n"
        "static int bn_is_prime_int(void);\n"
        "int ossl_bn_check_prime(void);\n"
        "int ossl_bn_check_generated_prime(void);\n",
        encoding="utf-8",
    )
    run_git(path, "init")
    run_git(path, "config", "user.email", "traceleak@example.invalid")
    run_git(path, "config", "user.name", "TraceLeak Test")
    run_git(path, "add", ".")
    run_git(path, "commit", "-m", "initial")


def run_git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, text=True)


def make_pinned_manifest(tmp_path) -> Path:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)
    manifest_path = tmp_path / "pinned.json"
    write_pinned_manifest(manifest_path, manifest)
    return manifest_path


def test_inspect_openssl_layout_cli_writes_markdown(tmp_path) -> None:
    manifest_path = make_pinned_manifest(tmp_path)
    output_path = tmp_path / "inspection.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_openssl_layout.py",
            "--in",
            str(manifest_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "TraceLeak OpenSSL Layout Inspection" in markdown
    assert "RSA_generate_key_ex" in markdown


def test_inspect_openssl_layout_cli_rejects_template(tmp_path) -> None:
    output_path = tmp_path / "inspection.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_openssl_layout.py",
            "--in",
            str(TEMPLATE),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "pinned manifest" in result.stderr


def test_inspect_openssl_layout_cli_rejects_missing_manifest(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_openssl_layout.py",
            "--in",
            str(tmp_path / "missing.json"),
            "--out",
            str(tmp_path / "inspection.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "source pin manifest not found" in result.stderr

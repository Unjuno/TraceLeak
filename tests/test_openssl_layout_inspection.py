# ruff: noqa: I001

import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_layout_inspection import (
    OpenSSLLayoutInspectionError,
    inspect_openssl_layout_manifest,
    layout_inspection_markdown,
)
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest


TEMPLATE = Path("examples/openssl_preflight/openssl_source_pin_sample.json")


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


def make_pinned_manifest(tmp_path) -> Path:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)
    manifest_path = tmp_path / "pinned.json"
    write_pinned_manifest(manifest_path, manifest)
    return manifest_path


def test_inspect_openssl_layout_manifest(tmp_path) -> None:
    manifest_path = make_pinned_manifest(tmp_path)

    report = inspect_openssl_layout_manifest(manifest_path)
    markdown = layout_inspection_markdown(report)

    assert report["report_type"] == "openssl_layout_inspection"
    assert report["status"] == "layout_inspected"
    assert report["exact_commit_sha"]
    assert report["layout"]
    assert "RSA_generate_key_ex" in markdown
    assert "TraceLeak OpenSSL Layout Inspection" in markdown


def test_inspect_openssl_layout_requires_pinned_manifest() -> None:
    with pytest.raises(OpenSSLLayoutInspectionError, match="pinned manifest"):
        inspect_openssl_layout_manifest(TEMPLATE)

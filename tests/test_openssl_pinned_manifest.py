import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_pinned_manifest import OpenSSLPinnedManifestError, generate_pinned_manifest
from traceleak.openssl_source_pin import validate_openssl_source_pin


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


def test_generate_pinned_manifest_from_clean_worktree(tmp_path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)

    manifest = generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)

    assert manifest["mode"] == "pinned"
    assert manifest["source"]["exact_commit_sha"]
    assert manifest["source"]["dirty"] is False
    assert all(item["resolved"]["target_exists"] for item in manifest["source_layout"])
    assert all(not item["resolved"]["missing_symbols"] for item in manifest["source_layout"])
    validate_openssl_source_pin(manifest)


def test_generate_pinned_manifest_rejects_dirty_worktree(tmp_path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    (worktree / "README.md").write_text("changed\n", encoding="utf-8")

    with pytest.raises(OpenSSLPinnedManifestError, match="uncommitted changes"):
        generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)


def test_generate_pinned_manifest_can_record_dirty_worktree(tmp_path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    (worktree / "README.md").write_text("changed\n", encoding="utf-8")

    manifest = generate_pinned_manifest(
        template_path=TEMPLATE,
        worktree_path=worktree,
        allow_dirty=True,
    )

    assert manifest["source"]["dirty"] is True
    assert manifest["source"]["status_porcelain"]


def test_generate_pinned_manifest_rejects_missing_symbol(tmp_path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    init_worktree(worktree)
    (worktree / "crypto" / "bn" / "bn_prime.c").write_text("int BN_generate_prime_ex(void);\n", encoding="utf-8")
    run_git(worktree, "add", ".")
    run_git(worktree, "commit", "-m", "update")

    with pytest.raises(OpenSSLPinnedManifestError, match="required symbols missing"):
        generate_pinned_manifest(template_path=TEMPLATE, worktree_path=worktree)

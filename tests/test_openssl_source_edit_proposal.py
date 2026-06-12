# ruff: noqa: I001

import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest
from traceleak.openssl_source_edit_proposal import (
    OpenSSLSourceEditProposalError,
    build_openssl_source_edit_proposal,
    source_edit_proposal_markdown,
    validate_openssl_source_edit_proposal,
)


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


def test_build_openssl_source_edit_proposal(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)

    proposal = build_openssl_source_edit_proposal(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    markdown = source_edit_proposal_markdown(proposal)

    assert proposal["format"] == "traceleak.openssl_source_edit_proposal.v1"
    assert proposal["source_mutation_allowed"] is False
    assert proposal["diff_generation_allowed"] is False
    assert proposal["patch_application_allowed"] is False
    assert proposal["raw_secret_capture_allowed"] is False
    assert len(proposal["proposals"]) == 5
    assert all(item["source_text_generated"] is False for item in proposal["proposals"])
    assert "TraceLeak OpenSSL Source Edit Proposal" in markdown


def test_validate_openssl_source_edit_proposal_rejects_source_text(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    proposal = build_openssl_source_edit_proposal(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    proposal["proposals"][0]["source_text"] = "not allowed"

    with pytest.raises(OpenSSLSourceEditProposalError, match="generated source fields"):
        validate_openssl_source_edit_proposal(proposal)


def test_validate_openssl_source_edit_proposal_rejects_diff_generation(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    proposal = build_openssl_source_edit_proposal(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    proposal["diff_generation_allowed"] = True

    with pytest.raises(OpenSSLSourceEditProposalError, match="diff_generation_allowed"):
        validate_openssl_source_edit_proposal(proposal)

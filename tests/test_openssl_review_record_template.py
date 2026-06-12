# ruff: noqa: I001

import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest
from traceleak.openssl_review_record_template import (
    OpenSSLReviewRecordTemplateError,
    build_openssl_review_record_template,
    review_record_template_markdown,
    validate_openssl_review_record_template,
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


def test_build_openssl_review_record_template(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)

    template = build_openssl_review_record_template(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    markdown = review_record_template_markdown(template)

    assert template["format"] == "traceleak.openssl_review_record_template.v1"
    assert template["approval_recorded"] is False
    assert template["completed_review_recorded"] is False
    assert template["source_mutation_allowed"] is False
    assert template["diff_generation_allowed"] is False
    assert template["patch_application_allowed"] is False
    assert len(template["records"]) == 5
    assert all(record["decision"] == "pending" for record in template["records"])
    assert all(record["review_status"] == "pending" for record in template["records"])
    assert "TraceLeak OpenSSL Review Record Template" in markdown


def test_validate_openssl_review_record_template_rejects_recorded_approval(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    template = build_openssl_review_record_template(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    template["approval_recorded"] = True

    with pytest.raises(OpenSSLReviewRecordTemplateError, match="approval_recorded"):
        validate_openssl_review_record_template(template)


def test_validate_openssl_review_record_template_rejects_non_pending_decision(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    template = build_openssl_review_record_template(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    template["records"][0]["decision"] = "accepted"

    with pytest.raises(OpenSSLReviewRecordTemplateError, match="decision"):
        validate_openssl_review_record_template(template)

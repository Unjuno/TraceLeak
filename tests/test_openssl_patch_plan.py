# ruff: noqa: I001

import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_patch_plan import (
    OpenSSLPatchPlanError,
    build_openssl_patch_plan,
    patch_plan_markdown,
    validate_openssl_patch_plan,
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


def test_build_openssl_patch_plan(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)

    plan = build_openssl_patch_plan(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    markdown = patch_plan_markdown(plan)

    assert plan["format"] == "traceleak.openssl_patch_plan.v1"
    assert plan["report_type"] == "openssl_patch_plan"
    assert plan["patch_application_allowed"] is False
    assert len(plan["planned_events"]) == 5
    assert {event["group_id"] for event in plan["planned_events"]} == {
        "rsa_keygen_entry",
        "prime_candidate_generation",
        "prime_candidate_filter",
        "probable_prime_test",
        "prime_candidate_result",
    }
    assert "TraceLeak OpenSSL Instrumentation Patch Plan" in markdown
    assert "rsa_keygen_entry" in markdown


def test_patch_plan_prefers_definition_line_over_declaration(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)

    plan = build_openssl_patch_plan(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    events = {event["group_id"]: event for event in plan["planned_events"]}

    assert events["rsa_keygen_entry"]["anchor_line"] == 4
    assert events["prime_candidate_generation"]["anchor_line"] == 9
    assert events["probable_prime_test"]["anchor_line"] == 10
    assert events["prime_candidate_result"]["anchor_line"] == 11


def test_validate_openssl_patch_plan_rejects_patch_application_allowed(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    plan = build_openssl_patch_plan(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    plan["patch_application_allowed"] = True

    with pytest.raises(OpenSSLPatchPlanError, match="patch_application_allowed"):
        validate_openssl_patch_plan(plan)


def test_validate_openssl_patch_plan_rejects_redacted_forbidden_overlap(tmp_path) -> None:
    source_pin_path = make_source_pin(tmp_path)
    plan = build_openssl_patch_plan(source_pin_path=source_pin_path, event_map_path=EVENT_MAP)
    plan["planned_events"][0]["redacted_values"].append("private_key")

    with pytest.raises(OpenSSLPatchPlanError, match="overlap forbidden_values"):
        validate_openssl_patch_plan(plan)

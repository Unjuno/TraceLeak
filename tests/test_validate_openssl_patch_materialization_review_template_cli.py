import json
from pathlib import Path

from scripts import build_openssl_patch_materialization_review_template as build_template_cli
from scripts import validate_openssl_patch_materialization_review_template as validate_template_cli
from tests.test_openssl_patch_materialization_approval_template import make_bundle


def test_validate_openssl_patch_materialization_review_template_cli_accepts_saved_template(
    tmp_path: Path,
) -> None:
    bundle_dir = make_bundle(tmp_path)
    template_path = tmp_path / "review_template.json"
    old_build_parse = build_template_cli.parse_args
    build_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_edit": bundle_dir / "openssl_source_edit_proposal.json",
            "manifest": bundle_dir / "openssl_instrumentation_bundle_manifest.json",
            "out": template_path,
            "format": "json",
        },
    )()
    try:
        assert build_template_cli.main() == 0
    finally:
        build_template_cli.parse_args = old_build_parse

    old_validate_parse = validate_template_cli.parse_args
    validate_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "template": template_path,
        },
    )()
    try:
        assert validate_template_cli.main() == 0
    finally:
        validate_template_cli.parse_args = old_validate_parse


def test_validate_openssl_patch_materialization_review_template_cli_rejects_edited_template(
    tmp_path: Path,
) -> None:
    bundle_dir = make_bundle(tmp_path)
    template_path = tmp_path / "review_template.json"
    old_build_parse = build_template_cli.parse_args
    build_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "source_edit": bundle_dir / "openssl_source_edit_proposal.json",
            "manifest": bundle_dir / "openssl_instrumentation_bundle_manifest.json",
            "out": template_path,
            "format": "json",
        },
    )()
    try:
        assert build_template_cli.main() == 0
    finally:
        build_template_cli.parse_args = old_build_parse

    template = json.loads(template_path.read_text(encoding="utf-8"))
    template["approval_recorded"] = True
    template_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    old_validate_parse = validate_template_cli.parse_args
    validate_template_cli.parse_args = lambda: type(
        "Args",
        (),
        {
            "template": template_path,
        },
    )()
    try:
        assert validate_template_cli.main() == 1
    finally:
        validate_template_cli.parse_args = old_validate_parse

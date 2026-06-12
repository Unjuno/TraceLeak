from pathlib import Path

import pytest

from traceleak.openssl_layout_inspection import (
    OpenSSLLayoutInspectionError,
    inspect_openssl_layout_manifest,
    layout_inspection_markdown,
)
from traceleak.openssl_pinned_manifest import generate_pinned_manifest, write_pinned_manifest
from tests.test_openssl_pinned_manifest import init_worktree


TEMPLATE = Path("examples/openssl_preflight/openssl_source_pin_sample.json")


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

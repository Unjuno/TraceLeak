# ruff: noqa: I001

import subprocess
import sys
from pathlib import Path

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

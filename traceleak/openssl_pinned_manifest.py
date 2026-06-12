"""Generate a pinned OpenSSL layout manifest from a local worktree.

The generator reads git metadata and source files only. It does not build, patch,
or execute OpenSSL.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

from traceleak.openssl_source_pin import (
    OpenSSLSourcePinError,
    load_openssl_source_pin,
    validate_openssl_source_pin,
)


class OpenSSLPinnedManifestError(ValueError):
    """Raised when a pinned manifest cannot be generated."""


def generate_pinned_manifest(
    *,
    template_path: str | Path,
    worktree_path: str | Path,
    allow_dirty: bool = False,
) -> dict[str, Any]:
    """Generate a pinned manifest from a template and a local OpenSSL worktree."""

    template = load_openssl_source_pin(template_path)
    worktree = Path(worktree_path)
    if not worktree.exists() or not worktree.is_dir():
        raise OpenSSLPinnedManifestError(f"worktree not found: {worktree}")

    commit_sha = _git(worktree, "rev-parse", "HEAD")
    status = _git(worktree, "status", "--porcelain")
    is_dirty = bool(status.strip())
    if is_dirty and not allow_dirty:
        raise OpenSSLPinnedManifestError("worktree has uncommitted changes; pass --allow-dirty to record them")

    pinned = copy.deepcopy(template)
    pinned["mode"] = "pinned"
    source = pinned["source"]
    source["exact_commit_sha"] = commit_sha
    source["worktree_path"] = str(worktree)
    source["dirty"] = is_dirty
    source["status_porcelain"] = status.splitlines()

    for item in pinned["source_layout"]:
        resolved = _resolve_layout_item(worktree=worktree, item=item)
        item["resolved"] = resolved
        if resolved["missing_symbols"]:
            missing = ", ".join(resolved["missing_symbols"])
            raise OpenSSLPinnedManifestError(
                f"required symbols missing in {item['target_path']}: {missing}"
            )

    notes = list(pinned.get("notes", []))
    notes.append("Pinned manifest generated from local OpenSSL worktree metadata and source inspection.")
    pinned["notes"] = notes
    validate_openssl_source_pin(pinned)
    return pinned


def write_pinned_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    """Write a pinned manifest JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_layout_item(*, worktree: Path, item: dict[str, Any]) -> dict[str, Any]:
    target_path = Path(item["target_path"])
    source_file = worktree / target_path
    if not source_file.exists() or not source_file.is_file():
        raise OpenSSLPinnedManifestError(f"target source file not found: {source_file}")
    text = source_file.read_text(encoding="utf-8", errors="replace")
    required_symbols = list(item.get("required_symbols", []))
    matched_symbols = [symbol for symbol in required_symbols if symbol in text]
    missing_symbols = [symbol for symbol in required_symbols if symbol not in matched_symbols]
    return {
        "target_exists": True,
        "matched_symbols": matched_symbols,
        "missing_symbols": missing_symbols,
        "line_binding_status": "unresolved_until_patch_plan",
    }


def _git(worktree: Path, *args: str) -> str:
    command = ["git", "-C", str(worktree), *args]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise OpenSSLPinnedManifestError(f"git command failed: {' '.join(command)}: {stderr}")
    return result.stdout.strip()

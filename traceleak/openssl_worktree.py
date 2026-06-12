"""Prepare a local OpenSSL worktree for pinned manifest generation.

This helper only clones/fetches/checks out source. It does not build, patch, run,
or trace OpenSSL.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

MOVING_REF_NAMES = {
    "HEAD",
    "main",
    "master",
    "origin/main",
    "origin/master",
    "refs/heads/main",
    "refs/heads/master",
}
_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class OpenSSLWorktreeError(ValueError):
    """Raised when an OpenSSL worktree cannot be prepared safely."""


def prepare_openssl_worktree(
    *,
    repository_url: str,
    worktree_path: str | Path,
    ref: str,
    allow_moving_ref: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Clone or update an OpenSSL worktree and detach it at the requested ref."""

    if not repository_url:
        raise OpenSSLWorktreeError("repository_url must not be empty")
    if not ref:
        raise OpenSSLWorktreeError("ref must not be empty")
    if _is_moving_ref(ref) and not allow_moving_ref:
        raise OpenSSLWorktreeError(
            "moving refs are rejected by default; use an exact commit SHA, tag, or pass --allow-moving-ref"
        )

    worktree = Path(worktree_path)
    if worktree.exists() and force:
        shutil.rmtree(worktree)
    if not worktree.exists():
        worktree.parent.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", "--no-checkout", repository_url, str(worktree)])
    elif not (worktree / ".git").exists():
        raise OpenSSLWorktreeError(f"worktree exists but is not a git checkout: {worktree}")

    _run(["git", "-C", str(worktree), "fetch", "--tags", "--prune", "origin"])
    _run(["git", "-C", str(worktree), "checkout", "--detach", ref])
    commit_sha = _git(worktree, "rev-parse", "HEAD")
    if not _COMMIT_RE.match(commit_sha):
        raise OpenSSLWorktreeError(f"resolved HEAD is not a 40-hex commit SHA: {commit_sha}")
    status = _git(worktree, "status", "--porcelain")
    dirty = bool(status.strip())
    if dirty:
        raise OpenSSLWorktreeError("prepared worktree is dirty after checkout")

    return {
        "repository_url": repository_url,
        "worktree_path": str(worktree),
        "requested_ref": ref,
        "resolved_commit_sha": commit_sha,
        "moving_ref_allowed": allow_moving_ref,
        "dirty": dirty,
        "status_porcelain": status.splitlines(),
    }


def write_worktree_record(path: str | Path, record: dict[str, Any]) -> None:
    """Write a worktree preparation record as JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_moving_ref(ref: str) -> bool:
    return ref in MOVING_REF_NAMES or ref.startswith("refs/heads/")


def _git(worktree: Path, *args: str) -> str:
    result = _run(["git", "-C", str(worktree), *args])
    return result.stdout.strip()


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise OpenSSLWorktreeError(f"command failed: {' '.join(command)}: {stderr}")
    return result

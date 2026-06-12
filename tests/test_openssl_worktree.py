import subprocess
from pathlib import Path

import pytest

from traceleak.openssl_worktree import OpenSSLWorktreeError, prepare_openssl_worktree


def init_repo(path: Path) -> str:
    path.mkdir()
    (path / "README.md").write_text("test repo\n", encoding="utf-8")
    run_git(path, "init")
    run_git(path, "config", "user.email", "traceleak@example.invalid")
    run_git(path, "config", "user.name", "TraceLeak Test")
    run_git(path, "add", ".")
    run_git(path, "commit", "-m", "initial")
    run_git(path, "branch", "main")
    return git_out(path, "rev-parse", "HEAD")


def run_git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, text=True)


def git_out(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_prepare_openssl_worktree_detaches_exact_commit(tmp_path) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "openssl"
    commit_sha = init_repo(repo)

    record = prepare_openssl_worktree(
        repository_url=str(repo),
        worktree_path=worktree,
        ref=commit_sha,
    )

    assert record["repository_url"] == str(repo)
    assert record["requested_ref"] == commit_sha
    assert record["resolved_commit_sha"] == commit_sha
    assert record["dirty"] is False
    assert git_out(worktree, "rev-parse", "--abbrev-ref", "HEAD") == "HEAD"


def test_prepare_openssl_worktree_rejects_moving_ref_by_default(tmp_path) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "openssl"
    init_repo(repo)

    with pytest.raises(OpenSSLWorktreeError, match="moving refs"):
        prepare_openssl_worktree(
            repository_url=str(repo),
            worktree_path=worktree,
            ref="main",
        )


def test_prepare_openssl_worktree_allows_moving_ref_when_explicit(tmp_path) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "openssl"
    init_repo(repo)

    record = prepare_openssl_worktree(
        repository_url=str(repo),
        worktree_path=worktree,
        ref="origin/main",
        allow_moving_ref=True,
    )

    assert record["requested_ref"] == "origin/main"
    assert record["resolved_commit_sha"]
    assert record["moving_ref_allowed"] is True


def test_prepare_openssl_worktree_rejects_non_git_existing_path(tmp_path) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "openssl"
    init_repo(repo)
    worktree.mkdir()

    with pytest.raises(OpenSSLWorktreeError, match="not a git checkout"):
        prepare_openssl_worktree(
            repository_url=str(repo),
            worktree_path=worktree,
            ref=git_out(repo, "rev-parse", "HEAD"),
        )

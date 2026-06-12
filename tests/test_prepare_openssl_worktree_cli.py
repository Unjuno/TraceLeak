# ruff: noqa: I001

import json
import subprocess
import sys
from pathlib import Path


def init_repo(path: Path) -> str:
    path.mkdir()
    (path / "README.md").write_text("test repo\n", encoding="utf-8")
    run_git(path, "init")
    run_git(path, "config", "user.email", "traceleak@example.invalid")
    run_git(path, "config", "user.name", "TraceLeak Test")
    run_git(path, "add", ".")
    run_git(path, "commit", "-m", "initial")
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


def test_prepare_worktree_cli_writes_record(tmp_path) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "checkout"
    output_path = tmp_path / "record.json"
    commit_sha = init_repo(repo)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_openssl_worktree.py",
            "--repo",
            str(repo),
            "--ref",
            commit_sha,
            "--worktree",
            str(worktree),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["resolved_commit_sha"] == commit_sha
    assert payload["dirty"] is False
    assert worktree.exists()


def test_prepare_worktree_cli_rejects_branch_ref(tmp_path) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "checkout"
    output_path = tmp_path / "record.json"
    init_repo(repo)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_openssl_worktree.py",
            "--repo",
            str(repo),
            "--ref",
            "main",
            "--worktree",
            str(worktree),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "moving refs" in result.stderr

#!/usr/bin/env python3
"""Prepare a local OpenSSL worktree at a requested ref."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_worktree import (
    OpenSSLWorktreeError,
    prepare_openssl_worktree,
    write_worktree_record,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a local OpenSSL worktree.")
    parser.add_argument("--repo", dest="repository_url", required=True, help="Git repository URL or path")
    parser.add_argument("--ref", required=True, help="Commit SHA or tag to check out")
    parser.add_argument(
        "--worktree",
        dest="worktree_path",
        type=Path,
        default=Path("external/openssl"),
        help="Local worktree path",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        type=Path,
        default=Path("reports/local/openssl_worktree.json"),
        help="Output worktree record JSON",
    )
    parser.add_argument(
        "--allow-moving-ref",
        action="store_true",
        help="Allow branch-like refs such as main or origin/main",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete and recreate the worktree path before cloning",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        record = prepare_openssl_worktree(
            repository_url=args.repository_url,
            worktree_path=args.worktree_path,
            ref=args.ref,
            allow_moving_ref=args.allow_moving_ref,
            force=args.force,
        )
        write_worktree_record(args.output_path, record)
    except OpenSSLWorktreeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        "prepared OpenSSL worktree: {worktree} ({sha})".format(
            worktree=record["worktree_path"],
            sha=record["resolved_commit_sha"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

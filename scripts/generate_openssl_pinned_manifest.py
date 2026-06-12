#!/usr/bin/env python3
"""Generate a pinned OpenSSL manifest from a local worktree."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_pinned_manifest import (
    OpenSSLPinnedManifestError,
    generate_pinned_manifest,
    write_pinned_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a pinned OpenSSL manifest.")
    parser.add_argument(
        "--template",
        dest="template_path",
        required=True,
        type=Path,
        help="Template source-layout manifest JSON",
    )
    parser.add_argument(
        "--worktree",
        dest="worktree_path",
        required=True,
        type=Path,
        help="Local OpenSSL worktree",
    )
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output pinned JSON")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow generating a manifest from a worktree with uncommitted changes",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = generate_pinned_manifest(
            template_path=args.template_path,
            worktree_path=args.worktree_path,
            allow_dirty=args.allow_dirty,
        )
        write_pinned_manifest(args.output_path, manifest)
    except OpenSSLPinnedManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        "wrote pinned OpenSSL manifest: {path} ({sha})".format(
            path=args.output_path,
            sha=manifest["source"]["exact_commit_sha"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

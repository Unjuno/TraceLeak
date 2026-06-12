#!/usr/bin/env python3
"""Build a pending OpenSSL patch-materialization review template."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_patch_materialization_approval_template import (
    OpenSSLPatchMaterializationApprovalTemplateError,
    build_openssl_patch_materialization_approval_template_from_paths,
    write_openssl_patch_materialization_approval_template_json,
    write_openssl_patch_materialization_approval_template_markdown,
)
from traceleak.openssl_patch_materialization_gate import OpenSSLPatchMaterializationGateError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a pending OpenSSL review template.")
    parser.add_argument("--source-edit", required=True, type=Path, help="Source edit proposal JSON")
    parser.add_argument("--manifest", required=True, type=Path, help="Bundle manifest JSON")
    parser.add_argument("--out", required=True, type=Path, help="Template output path")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        template = build_openssl_patch_materialization_approval_template_from_paths(
            source_edit_path=args.source_edit,
            manifest_path=args.manifest,
        )
    except (OpenSSLPatchMaterializationApprovalTemplateError, OpenSSLPatchMaterializationGateError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        write_openssl_patch_materialization_approval_template_json(args.out, template)
    else:
        write_openssl_patch_materialization_approval_template_markdown(args.out, template)
    print(f"wrote OpenSSL patch materialization review template: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

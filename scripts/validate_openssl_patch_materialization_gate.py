#!/usr/bin/env python3
"""Validate the OpenSSL patch-materialization review approval gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_patch_materialization_gate import (
    OpenSSLPatchMaterializationGateError,
    build_openssl_patch_materialization_preflight_gate,
    load_openssl_bundle_manifest_json,
    load_openssl_review_approval_record,
    load_openssl_source_edit_proposal_json,
    write_openssl_patch_materialization_preflight_gate_json,
    write_openssl_patch_materialization_preflight_gate_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an OpenSSL patch-materialization approval gate."
    )
    parser.add_argument("--source-edit", required=True, type=Path, help="Source edit proposal JSON")
    parser.add_argument("--manifest", required=True, type=Path, help="Bundle manifest JSON")
    parser.add_argument("--approval-record", required=True, type=Path, help="Review approval record JSON")
    parser.add_argument("--out", type=Path, default=None, help="Optional preflight gate report output")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source_edit = load_openssl_source_edit_proposal_json(args.source_edit)
        manifest = load_openssl_bundle_manifest_json(args.manifest)
        approval_record = load_openssl_review_approval_record(args.approval_record)
        gate = build_openssl_patch_materialization_preflight_gate(
            source_edit_proposal=source_edit,
            bundle_manifest=manifest,
            approval_record=approval_record,
        )
    except OpenSSLPatchMaterializationGateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.out is not None:
        if args.format == "json":
            write_openssl_patch_materialization_preflight_gate_json(args.out, gate)
        else:
            write_openssl_patch_materialization_preflight_gate_markdown(args.out, gate)
    print(f"valid OpenSSL patch materialization preflight gate: {args.approval_record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

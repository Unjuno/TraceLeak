#!/usr/bin/env python3
"""Build review-only OpenSSL event slots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_event_map import OpenSSLEventMapError
from traceleak.openssl_instrumentation_stub import OpenSSLInstrumentationStubError
from traceleak.openssl_layout_inspection import OpenSSLLayoutInspectionError
from traceleak.openssl_patch_plan import OpenSSLPatchPlanError
from traceleak.openssl_source_edit_proposal import (
    OpenSSLSourceEditProposalError,
    build_openssl_source_edit_proposal,
    write_source_edit_proposal_json,
    write_source_edit_proposal_markdown,
)
from traceleak.openssl_source_pin import OpenSSLSourcePinError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build review-only OpenSSL event slots.")
    parser.add_argument("--source-pin", required=True, type=Path)
    parser.add_argument("--event-map", required=True, type=Path)
    parser.add_argument("--out", dest="output_path", required=True, type=Path)
    parser.add_argument("--format", choices=["md", "json"], default="md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        proposal = build_openssl_source_edit_proposal(
            source_pin_path=args.source_pin,
            event_map_path=args.event_map,
        )
    except (
        OpenSSLEventMapError,
        OpenSSLInstrumentationStubError,
        OpenSSLLayoutInspectionError,
        OpenSSLPatchPlanError,
        OpenSSLSourceEditProposalError,
        OpenSSLSourcePinError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        write_source_edit_proposal_json(args.output_path, proposal)
    else:
        write_source_edit_proposal_markdown(args.output_path, proposal)
    print(f"wrote OpenSSL event slot review: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

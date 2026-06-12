#!/usr/bin/env python3
"""Build a human-review checklist for OpenSSL event slots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_event_map import OpenSSLEventMapError
from traceleak.openssl_human_review_checklist import (
    OpenSSLHumanReviewChecklistError,
    build_openssl_human_review_checklist,
    write_human_review_checklist_json,
    write_human_review_checklist_markdown,
)
from traceleak.openssl_instrumentation_stub import OpenSSLInstrumentationStubError
from traceleak.openssl_layout_inspection import OpenSSLLayoutInspectionError
from traceleak.openssl_patch_plan import OpenSSLPatchPlanError
from traceleak.openssl_source_edit_proposal import OpenSSLSourceEditProposalError
from traceleak.openssl_source_pin import OpenSSLSourcePinError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL human-review checklist.")
    parser.add_argument("--source-pin", required=True, type=Path)
    parser.add_argument("--event-map", required=True, type=Path)
    parser.add_argument("--out", dest="output_path", required=True, type=Path)
    parser.add_argument("--format", choices=["md", "json"], default="md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        checklist = build_openssl_human_review_checklist(
            source_pin_path=args.source_pin,
            event_map_path=args.event_map,
        )
    except (
        OpenSSLEventMapError,
        OpenSSLHumanReviewChecklistError,
        OpenSSLInstrumentationStubError,
        OpenSSLLayoutInspectionError,
        OpenSSLPatchPlanError,
        OpenSSLSourceEditProposalError,
        OpenSSLSourcePinError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        write_human_review_checklist_json(args.output_path, checklist)
    else:
        write_human_review_checklist_markdown(args.output_path, checklist)
    print(f"wrote OpenSSL human review checklist: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

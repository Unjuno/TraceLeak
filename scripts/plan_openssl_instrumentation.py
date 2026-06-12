#!/usr/bin/env python3
"""Build a review-only OpenSSL instrumentation patch plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_event_map import OpenSSLEventMapError
from traceleak.openssl_layout_inspection import OpenSSLLayoutInspectionError
from traceleak.openssl_patch_plan import (
    OpenSSLPatchPlanError,
    build_openssl_patch_plan,
    write_patch_plan_json,
    write_patch_plan_markdown,
)
from traceleak.openssl_source_pin import OpenSSLSourcePinError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL instrumentation patch plan.")
    parser.add_argument("--source-pin", required=True, type=Path, help="Pinned source manifest JSON")
    parser.add_argument("--event-map", required=True, type=Path, help="Event-map JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = build_openssl_patch_plan(
            source_pin_path=args.source_pin,
            event_map_path=args.event_map,
        )
    except (
        OpenSSLEventMapError,
        OpenSSLLayoutInspectionError,
        OpenSSLPatchPlanError,
        OpenSSLSourcePinError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        write_patch_plan_json(args.output_path, plan)
    else:
        write_patch_plan_markdown(args.output_path, plan)
    print(f"wrote OpenSSL patch plan: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a review-only OpenSSL instrumentation stub specification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_event_map import OpenSSLEventMapError
from traceleak.openssl_instrumentation_stub import (
    OpenSSLInstrumentationStubError,
    build_openssl_instrumentation_stub,
    write_instrumentation_stub_json,
    write_instrumentation_stub_markdown,
)
from traceleak.openssl_layout_inspection import OpenSSLLayoutInspectionError
from traceleak.openssl_patch_plan import OpenSSLPatchPlanError
from traceleak.openssl_source_pin import OpenSSLSourcePinError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL instrumentation stub specification.")
    parser.add_argument("--source-pin", required=True, type=Path, help="Pinned source manifest JSON")
    parser.add_argument("--event-map", required=True, type=Path, help="Event-map JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        stub = build_openssl_instrumentation_stub(
            source_pin_path=args.source_pin,
            event_map_path=args.event_map,
        )
    except (
        OpenSSLEventMapError,
        OpenSSLInstrumentationStubError,
        OpenSSLLayoutInspectionError,
        OpenSSLPatchPlanError,
        OpenSSLSourcePinError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        write_instrumentation_stub_json(args.output_path, stub)
    else:
        write_instrumentation_stub_markdown(args.output_path, stub)
    print(f"wrote OpenSSL instrumentation stub spec: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

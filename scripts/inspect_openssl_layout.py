#!/usr/bin/env python3
"""Inspect a pinned OpenSSL layout manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_layout_inspection import (
    OpenSSLLayoutInspectionError,
    inspect_openssl_layout_manifest,
    write_layout_inspection_json,
    write_layout_inspection_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a pinned OpenSSL layout manifest.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Pinned manifest JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = inspect_openssl_layout_manifest(args.input_path)
    except OpenSSLLayoutInspectionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        write_layout_inspection_json(args.output_path, report)
    else:
        write_layout_inspection_markdown(args.output_path, report)
    print(f"wrote OpenSSL layout inspection: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

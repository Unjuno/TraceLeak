#!/usr/bin/env python3
"""Render an OpenSSL layout manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

import traceleak.openssl_source_pin as layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an OpenSSL layout report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = layout.load_openssl_source_pin(args.input_path)
        report = layout.openssl_source_pin_report_dict(manifest)
    except layout.OpenSSLSourcePinError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        layout.write_openssl_source_pin_report_json(args.output_path, report)
    else:
        layout.write_openssl_source_pin_report_markdown(args.output_path, report)
    print(f"wrote OpenSSL layout report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

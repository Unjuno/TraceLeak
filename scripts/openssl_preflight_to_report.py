#!/usr/bin/env python3
"""Render an OpenSSL preflight manifest as a report."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.openssl_preflight import (
    OpenSSLPreflightError,
    load_openssl_preflight,
    openssl_preflight_report_dict,
    write_openssl_preflight_report_json,
    write_openssl_preflight_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an OpenSSL preflight report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input manifest JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = load_openssl_preflight(args.input_path)
        report = openssl_preflight_report_dict(manifest)
    except OpenSSLPreflightError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_openssl_preflight_report_json(args.output_path, report)
    else:
        write_openssl_preflight_report_markdown(args.output_path, report)
    print(f"wrote OpenSSL preflight report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

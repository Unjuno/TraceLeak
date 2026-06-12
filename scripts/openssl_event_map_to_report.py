#!/usr/bin/env python3
"""Render an OpenSSL event-map manifest as a report."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.openssl_event_map import (
    OpenSSLEventMapError,
    load_openssl_event_map,
    openssl_event_map_report_dict,
    write_openssl_event_map_report_json,
    write_openssl_event_map_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an OpenSSL event-map report.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input event-map JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        event_map = load_openssl_event_map(args.input_path)
        report = openssl_event_map_report_dict(event_map)
    except OpenSSLEventMapError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_openssl_event_map_report_json(args.output_path, report)
    else:
        write_openssl_event_map_report_markdown(args.output_path, report)
    print(f"wrote OpenSSL event-map report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render an OpenSSL redacted event stream report."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract
from traceleak.openssl_trace_event_stream import (
    OpenSSLTraceEventStreamError,
    load_openssl_redacted_event_stream,
    openssl_redacted_event_stream_report_dict,
    write_openssl_redacted_event_stream_report_json,
    write_openssl_redacted_event_stream_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an OpenSSL redacted event stream report.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSONL redacted event runs")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        runs = load_openssl_redacted_event_stream(args.input_path)
        report = openssl_redacted_event_stream_report_dict(contract, runs)
    except (OpenSSLTraceContractError, OpenSSLTraceEventStreamError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_openssl_redacted_event_stream_report_json(args.output_path, report)
    else:
        write_openssl_redacted_event_stream_report_markdown(args.output_path, report)
    print(f"wrote OpenSSL redacted event stream report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an OpenSSL redacted TraceLeak event stream."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract
from traceleak.openssl_trace_event_stream import (
    OpenSSLTraceEventStreamError,
    load_openssl_redacted_event_stream,
    validate_openssl_redacted_event_stream,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL redacted event stream.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSONL redacted event runs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        runs = load_openssl_redacted_event_stream(args.input_path)
        validate_openssl_redacted_event_stream(contract, runs)
    except (OpenSSLTraceContractError, OpenSSLTraceEventStreamError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    event_count = sum(len(run["events"]) for run in runs)
    print(f"valid OpenSSL redacted event stream: {len(runs)} run(s), {event_count} event(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

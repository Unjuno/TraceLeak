#!/usr/bin/env python3
"""Run the OpenSSL review-only instrumentation-to-sample dry-run chain."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_instrumentation_chain import (
    OpenSSLInstrumentationChainError,
    run_openssl_instrumentation_dry_run_chain,
    write_openssl_instrumentation_chain_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the OpenSSL instrumentation review dry-run chain."
    )
    parser.add_argument("--source-pin", required=True, type=Path, help="Pinned OpenSSL source manifest")
    parser.add_argument("--event-map", required=True, type=Path, help="OpenSSL event map JSON")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--events", required=True, type=Path, help="OpenSSL redacted event stream JSONL")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output artifact directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = run_openssl_instrumentation_dry_run_chain(
            source_pin_path=args.source_pin,
            event_map_path=args.event_map,
            contract_path=args.contract,
            event_stream_path=args.events,
        )
        paths = write_openssl_instrumentation_chain_outputs(args.out_dir, report)
    except OpenSSLInstrumentationChainError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote OpenSSL instrumentation dry-run chain: {paths['summary_md']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

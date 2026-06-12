#!/usr/bin/env python3
"""Validate an OpenSSL instrumentation dry-run output bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_instrumentation_bundle import (
    OpenSSLInstrumentationBundleError,
    validate_openssl_instrumentation_bundle,
    write_openssl_instrumentation_bundle_report_json,
    write_openssl_instrumentation_bundle_report_markdown,
)
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL instrumentation output bundle.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--bundle-dir", required=True, type=Path, help="Instrumentation chain output directory")
    parser.add_argument("--out", type=Path, help="Optional validation report output path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Report format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        report = validate_openssl_instrumentation_bundle(
            contract=contract,
            bundle_dir=args.bundle_dir,
        )
        if args.out is not None:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            if args.format == "json":
                write_openssl_instrumentation_bundle_report_json(args.out, report)
            else:
                write_openssl_instrumentation_bundle_report_markdown(args.out, report)
    except (OpenSSLInstrumentationBundleError, OpenSSLTraceContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL instrumentation bundle: {args.bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

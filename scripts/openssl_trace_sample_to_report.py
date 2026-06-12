#!/usr/bin/env python3
"""Render an OpenSSL trace sample acceptance report."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.openssl_trace_acceptance import (
    OpenSSLTraceAcceptanceError,
    load_contract_and_sample,
    openssl_trace_sample_acceptance_report_dict,
    write_openssl_trace_sample_acceptance_report_json,
    write_openssl_trace_sample_acceptance_report_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an OpenSSL trace sample acceptance report.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--sample", required=True, type=Path, help="Candidate model_sequence.v1 sample JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract, sample = load_contract_and_sample(args.contract, args.sample)
        report = openssl_trace_sample_acceptance_report_dict(contract, sample)
    except OpenSSLTraceAcceptanceError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_openssl_trace_sample_acceptance_report_json(args.output_path, report)
    else:
        write_openssl_trace_sample_acceptance_report_markdown(args.output_path, report)
    print(f"wrote OpenSSL trace sample acceptance report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

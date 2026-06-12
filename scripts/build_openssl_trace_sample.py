#!/usr/bin/env python3
"""Build a model_sequence.v1 sample from redacted OpenSSL TraceLeak runs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract
from traceleak.openssl_trace_sample_builder import (
    OpenSSLTraceSampleBuilderError,
    build_openssl_model_sequence_sample,
    load_redacted_event_runs,
    write_model_sequence_sample,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an OpenSSL model_sequence.v1 sample from redacted event runs."
    )
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSONL redacted event runs")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output model_sequence.v1 JSON")
    parser.add_argument("--label-key", help="Lab-only label key to copy into output records")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        runs = load_redacted_event_runs(args.input_path)
        sample = build_openssl_model_sequence_sample(
            contract=contract,
            runs=runs,
            input_name=str(args.input_path),
            label_key=args.label_key,
        )
        write_model_sequence_sample(args.output_path, sample)
    except (OpenSSLTraceContractError, OpenSSLTraceSampleBuilderError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote OpenSSL model-sequence sample: {args.output_path} ({sample['run_count']} run(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an OpenSSL actual trace-derived model-sequence sample."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_trace_acceptance import (
    OpenSSLTraceAcceptanceError,
    load_contract_and_sample,
    validate_openssl_trace_sample_acceptance,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL trace-derived sample.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--sample", required=True, type=Path, help="Candidate model_sequence.v1 sample JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract, sample = load_contract_and_sample(args.contract, args.sample)
        validate_openssl_trace_sample_acceptance(contract, sample)
    except OpenSSLTraceAcceptanceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"accepted OpenSSL trace-derived sample: {sample['target']} ({len(sample['records'])} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

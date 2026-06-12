#!/usr/bin/env python3
"""Validate an OpenSSL actual trace-derived model-sequence contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_trace_contract import (
    OpenSSLTraceContractError,
    load_openssl_trace_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL trace collector contract.")
    parser.add_argument("path", type=Path, help="OpenSSL trace contract JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.path)
    except OpenSSLTraceContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL trace contract: {contract['contract_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an OpenSSL source-pin manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_source_pin import OpenSSLSourcePinError, load_openssl_source_pin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL source-pin manifest.")
    parser.add_argument("path", type=Path, help="OpenSSL source-pin JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = load_openssl_source_pin(args.path)
    except OpenSSLSourcePinError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL source pin manifest: {manifest['experiment_id']} ({manifest['mode']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

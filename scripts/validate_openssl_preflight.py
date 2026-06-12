#!/usr/bin/env python3
"""Validate an OpenSSL experiment preflight manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_preflight import OpenSSLPreflightError, load_openssl_preflight


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL preflight manifest.")
    parser.add_argument("path", type=Path, help="OpenSSL preflight manifest JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = load_openssl_preflight(args.path)
    except OpenSSLPreflightError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL preflight manifest: {manifest['experiment_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

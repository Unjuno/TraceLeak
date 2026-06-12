#!/usr/bin/env python3
"""Validate an OpenSSL event-map manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_event_map import OpenSSLEventMapError, load_openssl_event_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL event-map manifest.")
    parser.add_argument("path", type=Path, help="OpenSSL event-map JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        event_map = load_openssl_event_map(args.path)
    except OpenSSLEventMapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL event map: {event_map['experiment_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

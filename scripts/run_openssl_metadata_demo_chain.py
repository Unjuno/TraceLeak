#!/usr/bin/env python3
"""Run the public-safe OpenSSL metadata demo chain."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.openssl_metadata_demo_chain import (
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenSSL metadata-only public demo chain.")
    parser.add_argument("--out-dir", default=Path("reports/local/openssl_metadata_demo"), type=Path)
    parser.add_argument("--record-count", default=4, type=int)
    parser.add_argument("--epochs", default=20, type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        artifacts = build_openssl_metadata_demo_chain(
            record_count=args.record_count,
            epochs=args.epochs,
        )
        paths = write_openssl_metadata_demo_chain(
            output_dir=args.out_dir,
            artifacts=artifacts,
        )
    except Exception as exc:
        print(f"invalid OpenSSL metadata demo chain request: {exc}")
        return 1
    print(f"wrote OpenSSL metadata demo chain artifacts: {args.out_dir} ({len(paths)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

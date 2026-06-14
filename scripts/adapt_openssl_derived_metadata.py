#!/usr/bin/env python3
"""Adapt OpenSSL-derived symbolic metadata into model-sequence records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_derived_metadata_adapter import (
    adapt_openssl_derived_metadata_to_model_sequence,
    write_openssl_derived_metadata_model_sequence,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adapt OpenSSL-derived metadata into model-sequence JSON.")
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--runtime-gate", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = adapt_openssl_derived_metadata_to_model_sequence(
            metadata_input=_load(args.metadata),
            runtime_gate=_load(args.runtime_gate),
        )
        write_openssl_derived_metadata_model_sequence(args.out, payload)
    except Exception as exc:
        print(f"invalid OpenSSL-derived metadata adapter input: {exc}")
        return 1
    print(f"wrote OpenSSL-derived metadata model-sequence sample: {args.out}")
    return 0


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

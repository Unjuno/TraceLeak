#!/usr/bin/env python3
"""Build an OpenSSL model-sequence ingestion preflight report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_handoff_contract import (
    validate_openssl_model_sequence_handoff_contract,
)
from traceleak.openssl_model_sequence_ingestion_preflight import (
    build_openssl_model_sequence_ingestion_preflight,
    validate_openssl_model_sequence_ingestion_preflight,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an OpenSSL model-sequence ingestion preflight report."
    )
    parser.add_argument("--handoff", required=True, type=Path, help="Handoff contract JSON path.")
    parser.add_argument("--out", required=True, type=Path, help="Preflight report JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    handoff = _load_object(args.handoff, "handoff")
    validate_openssl_model_sequence_handoff_contract(handoff)
    preflight = build_openssl_model_sequence_ingestion_preflight(handoff_contract=handoff)
    validate_openssl_model_sequence_ingestion_preflight(preflight)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote OpenSSL model-sequence ingestion preflight: {args.out}")
    return 0


def _load_object(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

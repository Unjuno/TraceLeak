#!/usr/bin/env python3
"""Build a model-sequence input contract from a preflight report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_ingestion_preflight import (
    validate_openssl_model_sequence_ingestion_preflight,
)
from traceleak.openssl_model_sequence_input_contract import (
    build_openssl_model_sequence_input_contract,
    validate_openssl_model_sequence_input_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a model-sequence input contract.")
    parser.add_argument("--preflight", required=True, type=Path)
    parser.add_argument("--output-sample-path", required=True)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    preflight = _load_object(args.preflight)
    validate_openssl_model_sequence_ingestion_preflight(preflight)
    contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=preflight,
        output_sample_path=args.output_sample_path,
    )
    validate_openssl_model_sequence_input_contract(contract)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote model-sequence input contract: {args.out}")
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build an OpenSSL model-sequence sample contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_input_contract import (
    validate_openssl_model_sequence_input_contract,
)
from traceleak.openssl_model_sequence_input_manifest import (
    validate_openssl_model_sequence_input_manifest,
)
from traceleak.openssl_model_sequence_sample_contract import (
    build_openssl_model_sequence_sample_contract,
    validate_openssl_model_sequence_sample_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL model-sequence sample contract.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--feature-field", action="append", required=True)
    parser.add_argument("--label-field", action="append", required=True)
    parser.add_argument("--metadata-field", action="append", required=True)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_contract = _load_object(args.contract)
    input_manifest = _load_object(args.manifest)
    validate_openssl_model_sequence_input_contract(input_contract)
    validate_openssl_model_sequence_input_manifest(
        manifest=input_manifest,
        input_contract=input_contract,
    )
    contract = build_openssl_model_sequence_sample_contract(
        input_manifest=input_manifest,
        input_contract=input_contract,
        feature_fields=args.feature_field,
        label_fields=args.label_field,
        metadata_fields=args.metadata_field,
    )
    validate_openssl_model_sequence_sample_contract(contract)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote OpenSSL model-sequence sample contract: {args.out}")
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an OpenSSL model-sequence sample manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_sample_contract import (
    validate_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    validate_openssl_model_sequence_sample_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a model-sequence sample manifest.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = _load_object(args.contract)
        manifest = _load_object(args.manifest)
        validate_openssl_model_sequence_sample_contract(contract)
        validate_openssl_model_sequence_sample_manifest(
            manifest=manifest,
            sample_contract=contract,
        )
    except Exception as exc:
        print(f"invalid model-sequence sample manifest: {exc}")
        return 1
    print("valid model-sequence sample manifest")
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

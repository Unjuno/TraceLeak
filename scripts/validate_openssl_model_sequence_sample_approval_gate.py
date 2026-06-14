#!/usr/bin/env python3
"""Validate an OpenSSL model-sequence sample approval gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_sample_approval_gate import (
    validate_openssl_model_sequence_sample_approval_gate,
    validate_openssl_model_sequence_sample_approval_record,
)
from traceleak.openssl_model_sequence_sample_contract import (
    validate_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    validate_openssl_model_sequence_sample_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a model-sequence sample approval gate."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--approval-record", required=True, type=Path)
    parser.add_argument("--gate", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = _load_object(args.contract)
        manifest = _load_object(args.manifest)
        approval_record = _load_object(args.approval_record)
        gate = _load_object(args.gate)
        validate_openssl_model_sequence_sample_contract(contract)
        validate_openssl_model_sequence_sample_manifest(
            manifest=manifest,
            sample_contract=contract,
        )
        validate_openssl_model_sequence_sample_approval_record(
            approval_record=approval_record,
            sample_manifest=manifest,
        )
        validate_openssl_model_sequence_sample_approval_gate(
            gate=gate,
            sample_manifest=manifest,
            approval_record=approval_record,
        )
    except Exception as exc:
        print(f"invalid model-sequence sample approval gate: {exc}")
        return 1
    print("valid model-sequence sample approval gate")
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

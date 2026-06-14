#!/usr/bin/env python3
"""Validate an OpenSSL model-sequence sample materialization output manifest."""

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
from traceleak.openssl_model_sequence_sample_materialization_output_contract import (
    validate_openssl_model_sequence_sample_materialization_output_contract,
)
from traceleak.openssl_model_sequence_sample_materialization_output_manifest import (
    validate_openssl_model_sequence_sample_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_request_contract import (
    validate_openssl_model_sequence_sample_materialization_request_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a model-sequence sample materialization output manifest."
    )
    parser.add_argument("--sample-contract", required=True, type=Path)
    parser.add_argument("--sample-manifest", required=True, type=Path)
    parser.add_argument("--approval-record", required=True, type=Path)
    parser.add_argument("--approval-gate", required=True, type=Path)
    parser.add_argument("--request-contract", required=True, type=Path)
    parser.add_argument("--output-contract", required=True, type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        sample_contract = _load_object(args.sample_contract)
        sample_manifest = _load_object(args.sample_manifest)
        approval_record = _load_object(args.approval_record)
        approval_gate = _load_object(args.approval_gate)
        request_contract = _load_object(args.request_contract)
        output_contract = _load_object(args.output_contract)
        output_manifest = _load_object(args.output_manifest)
        validate_openssl_model_sequence_sample_contract(sample_contract)
        validate_openssl_model_sequence_sample_manifest(
            manifest=sample_manifest,
            sample_contract=sample_contract,
        )
        validate_openssl_model_sequence_sample_approval_record(
            approval_record=approval_record,
            sample_manifest=sample_manifest,
        )
        validate_openssl_model_sequence_sample_approval_gate(
            gate=approval_gate,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
        )
        validate_openssl_model_sequence_sample_materialization_request_contract(
            request_contract=request_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
        )
        validate_openssl_model_sequence_sample_materialization_output_contract(
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )
        validate_openssl_model_sequence_sample_materialization_output_manifest(
            manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
        )
    except Exception as exc:
        print(f"invalid model-sequence sample materialization output manifest: {exc}")
        return 1
    print("valid model-sequence sample materialization output manifest")
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

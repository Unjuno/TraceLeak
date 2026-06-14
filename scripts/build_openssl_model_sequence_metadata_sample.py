#!/usr/bin/env python3
"""Build an OpenSSL metadata-only model-sequence sample artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_metadata_sample import (
    build_openssl_model_sequence_metadata_sample,
    write_openssl_model_sequence_metadata_sample,
)
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
        description="Build a public-safe OpenSSL metadata-only model-sequence sample."
    )
    parser.add_argument("--sample-contract", required=True, type=Path)
    parser.add_argument("--sample-manifest", required=True, type=Path)
    parser.add_argument("--approval-record", required=True, type=Path)
    parser.add_argument("--approval-gate", required=True, type=Path)
    parser.add_argument("--request-contract", required=True, type=Path)
    parser.add_argument("--output-contract", required=True, type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--record-count", default=4, type=int)
    parser.add_argument("--label-name", default="metadata_probe_bucket")
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
        sample = build_openssl_model_sequence_metadata_sample(
            output_manifest=output_manifest,
            output_contract=output_contract,
            sample_manifest=sample_manifest,
            approval_record=approval_record,
            approval_gate=approval_gate,
            request_contract=request_contract,
            record_count=args.record_count,
            label_name=args.label_name,
        )
        write_openssl_model_sequence_metadata_sample(args.out, sample)
    except Exception as exc:
        print(f"invalid OpenSSL metadata-only model-sequence sample request: {exc}")
        return 1
    print(
        "wrote OpenSSL metadata-only model-sequence sample: "
        f"{args.out} ({sample['run_count']} record(s))"
    )
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

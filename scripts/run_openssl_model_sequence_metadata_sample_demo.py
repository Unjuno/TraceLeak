#!/usr/bin/env python3
"""Run the OpenSSL metadata-only model-sequence public demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_metadata_sample_demo_result import (
    build_openssl_model_sequence_metadata_sample_demo_result,
    write_openssl_model_sequence_metadata_sample_demo_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run baseline/NN over an OpenSSL metadata-only model-sequence sample."
    )
    parser.add_argument("--sample-contract", required=True, type=Path)
    parser.add_argument("--sample-manifest", required=True, type=Path)
    parser.add_argument("--approval-record", required=True, type=Path)
    parser.add_argument("--approval-gate", required=True, type=Path)
    parser.add_argument("--request-contract", required=True, type=Path)
    parser.add_argument("--output-contract", required=True, type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    parser.add_argument("--sample", required=True, type=Path)
    parser.add_argument("--model-preflight", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--baseline-out", required=True, type=Path)
    parser.add_argument("--nn-out", required=True, type=Path)
    parser.add_argument("--epochs", default=80, type=int)
    parser.add_argument("--learning-rate", default=0.8, type=float)
    parser.add_argument("--experiment-id", default="exp_openssl_metadata_sample_demo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        outputs = build_openssl_model_sequence_metadata_sample_demo_result(
            sample=_load_object(args.sample),
            model_preflight=_load_object(args.model_preflight),
            output_manifest=_load_object(args.output_manifest),
            output_contract=_load_object(args.output_contract),
            sample_manifest=_load_object(args.sample_manifest),
            approval_record=_load_object(args.approval_record),
            approval_gate=_load_object(args.approval_gate),
            request_contract=_load_object(args.request_contract),
            experiment_id=args.experiment_id,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
        )
        write_openssl_model_sequence_metadata_sample_demo_outputs(
            summary_path=args.summary_out,
            baseline_path=args.baseline_out,
            nn_path=args.nn_out,
            outputs=outputs,
        )
    except Exception as exc:
        print(f"invalid OpenSSL metadata sample demo request: {exc}")
        return 1
    print(
        "wrote OpenSSL metadata sample demo outputs: "
        f"summary={args.summary_out}, baseline={args.baseline_out}, nn={args.nn_out}"
    )
    return 0


def _load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

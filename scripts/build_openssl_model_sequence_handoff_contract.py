#!/usr/bin/env python3
"""Build an OpenSSL model-sequence handoff contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_materialization_output_contract import (
    validate_openssl_materialization_output_contract,
)
from traceleak.openssl_materialization_output_manifest import (
    validate_openssl_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_handoff_contract import (
    build_openssl_model_sequence_handoff_contract,
    validate_openssl_model_sequence_handoff_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL model-sequence handoff contract.")
    parser.add_argument("--contract", required=True, type=Path, help="Output contract JSON path.")
    parser.add_argument("--manifest", required=True, type=Path, help="Output manifest JSON path.")
    parser.add_argument("--feature-namespace", required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--out", required=True, type=Path, help="Handoff contract JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_contract = _load_object(args.contract, "contract")
    materialization_manifest = _load_object(args.manifest, "manifest")
    validate_openssl_materialization_output_contract(output_contract)
    validate_openssl_materialization_output_manifest(
        manifest=materialization_manifest,
        output_contract=output_contract,
    )
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=materialization_manifest,
        output_contract=output_contract,
        feature_namespace=args.feature_namespace,
        sample_id=args.sample_id,
    )
    validate_openssl_model_sequence_handoff_contract(handoff)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote OpenSSL model-sequence handoff contract: {args.out}")
    return 0


def _load_object(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

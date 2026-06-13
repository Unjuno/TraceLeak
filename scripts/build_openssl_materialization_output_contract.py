#!/usr/bin/env python3
"""Build an OpenSSL materialization output contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_materialization_approval_gate import (
    build_openssl_materialization_approval_gate,
    validate_openssl_materialization_approval_record,
)
from traceleak.openssl_materialization_output_contract import (
    build_openssl_materialization_output_contract,
    validate_openssl_materialization_output_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    validate_openssl_reviewed_materialization_request,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL materialization output contract.")
    parser.add_argument("--request", required=True, type=Path, help="Reviewed request JSON path.")
    parser.add_argument("--approval-record", required=True, type=Path, help="Approval record JSON path.")
    parser.add_argument("--output-manifest-path", required=True)
    parser.add_argument("--out", required=True, type=Path, help="Output contract JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reviewed_request = _load_object(args.request, "request")
    approval_record = _load_object(args.approval_record, "approval_record")
    validate_openssl_reviewed_materialization_request(reviewed_request)
    validate_openssl_materialization_approval_record(
        approval_record=approval_record,
        reviewed_request=reviewed_request,
    )
    gate = build_openssl_materialization_approval_gate(
        reviewed_request=reviewed_request,
        approval_record=approval_record,
    )
    contract = build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path=args.output_manifest_path,
    )
    validate_openssl_materialization_output_contract(contract)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote OpenSSL materialization output contract: {args.out}")
    return 0


def _load_object(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

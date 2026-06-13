#!/usr/bin/env python3
"""Validate an OpenSSL materialization output manifest."""

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL materialization output manifest.")
    parser.add_argument("--contract", required=True, type=Path, help="Output contract JSON path.")
    parser.add_argument("--manifest", required=True, type=Path, help="Output manifest JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = _load_object(args.contract, "contract")
        manifest = _load_object(args.manifest, "manifest")
        validate_openssl_materialization_output_contract(contract)
        validate_openssl_materialization_output_manifest(
            manifest=manifest,
            output_contract=contract,
        )
    except Exception as exc:
        print(f"invalid OpenSSL materialization output manifest: {exc}")
        return 1
    print("valid OpenSSL materialization output manifest")
    return 0


def _load_object(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate or build an OpenSSL metadata demo manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_model_sequence_metadata_demo_manifest import (
    build_openssl_model_sequence_metadata_demo_manifest,
    validate_openssl_model_sequence_metadata_demo_manifest,
    write_openssl_model_sequence_metadata_demo_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL metadata demo manifest.")
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--baseline-result", required=True, type=Path)
    parser.add_argument("--nn-result", required=True, type=Path)
    parser.add_argument("--sample", required=True, type=Path)
    parser.add_argument("--model-preflight", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = _load(args.summary)
        baseline_result = _load(args.baseline_result)
        nn_result = _load(args.nn_result)
        sample = _load(args.sample)
        model_preflight = _load(args.model_preflight)
        if args.manifest is not None:
            manifest = _load(args.manifest)
            validate_openssl_model_sequence_metadata_demo_manifest(
                manifest=manifest,
                summary=summary,
                baseline_result=baseline_result,
                nn_result=nn_result,
                sample=sample,
                model_preflight=model_preflight,
            )
        else:
            manifest = build_openssl_model_sequence_metadata_demo_manifest(
                summary=summary,
                baseline_result=baseline_result,
                nn_result=nn_result,
                sample=sample,
                model_preflight=model_preflight,
            )
        if args.out is not None:
            write_openssl_model_sequence_metadata_demo_manifest(args.out, manifest)
    except Exception as exc:
        print(f"invalid OpenSSL metadata demo manifest: {exc}")
        return 1
    print("valid OpenSSL metadata demo manifest")
    return 0


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

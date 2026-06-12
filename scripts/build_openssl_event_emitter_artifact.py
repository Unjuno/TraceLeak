#!/usr/bin/env python3
"""Build reviewable OpenSSL redacted event emitter artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from traceleak.openssl_event_emitter_artifact import (
    OpenSSLEventEmitterArtifactError,
    build_openssl_event_emitter_artifact,
    write_openssl_event_emitter_artifact_files,
    write_openssl_event_emitter_artifact_json,
    write_openssl_event_emitter_artifact_markdown,
)
from traceleak.openssl_instrumentation_stub import OpenSSLInstrumentationStubError
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build OpenSSL redacted event emitter artifacts.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--stub", required=True, type=Path, help="OpenSSL instrumentation stub JSON")
    parser.add_argument("--out-json", required=True, type=Path, help="Combined artifact JSON output")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for generated C files")
    parser.add_argument("--out-report", type=Path, help="Optional Markdown report output")
    return parser.parse_args()


def load_stub(path: Path) -> dict:
    try:
        stub = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLEventEmitterArtifactError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(stub, dict):
        raise OpenSSLEventEmitterArtifactError("instrumentation stub must be a JSON object")
    return stub


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        stub = load_stub(args.stub)
        artifact = build_openssl_event_emitter_artifact(contract=contract, instrumentation_stub=stub)
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        write_openssl_event_emitter_artifact_json(args.out_json, artifact)
        write_openssl_event_emitter_artifact_files(args.out_dir, artifact)
        if args.out_report is not None:
            args.out_report.parent.mkdir(parents=True, exist_ok=True)
            write_openssl_event_emitter_artifact_markdown(args.out_report, artifact)
    except (
        OpenSSLEventEmitterArtifactError,
        OpenSSLInstrumentationStubError,
        OpenSSLTraceContractError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote OpenSSL redacted event emitter artifacts: {args.out_json} and {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

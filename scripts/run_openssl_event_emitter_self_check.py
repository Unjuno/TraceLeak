#!/usr/bin/env python3
"""Run the OpenSSL redacted event emitter self-check chain."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from traceleak.openssl_event_emitter_artifact import OpenSSLEventEmitterArtifactError
from traceleak.openssl_event_emitter_self_check import (
    OpenSSLEventEmitterSelfCheckError,
    run_openssl_event_emitter_self_check,
    write_openssl_event_emitter_self_check_outputs,
)
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenSSL redacted event emitter self-check.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--emitter-artifact", required=True, type=Path, help="OpenSSL event emitter artifact JSON")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output self-check directory")
    parser.add_argument("--run-count", type=int, default=4, help="Number of generated self-check runs")
    return parser.parse_args()


def load_emitter_artifact(path: Path) -> dict:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLEventEmitterArtifactError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(artifact, dict):
        raise OpenSSLEventEmitterArtifactError("event emitter artifact must be a JSON object")
    return artifact


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        emitter_artifact = load_emitter_artifact(args.emitter_artifact)
        report = run_openssl_event_emitter_self_check(
            contract=contract,
            emitter_artifact=emitter_artifact,
            run_count=args.run_count,
        )
        paths = write_openssl_event_emitter_self_check_outputs(args.out_dir, report)
    except (
        OpenSSLEventEmitterArtifactError,
        OpenSSLEventEmitterSelfCheckError,
        OpenSSLTraceContractError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote OpenSSL event emitter self-check: {paths['summary_md']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

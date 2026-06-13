#!/usr/bin/env python3
"""Build an OpenSSL actual execution preflight report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_actual_execution_preflight import (
    build_openssl_actual_execution_preflight_report,
    validate_openssl_actual_execution_preflight_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL actual execution preflight report.")
    parser.add_argument("--out", required=True, type=Path, help="Output JSON path.")
    parser.add_argument("--source-pin-digest", default="")
    parser.add_argument("--trace-contract-digest", default="")
    parser.add_argument("--workspace-root", default="")
    parser.add_argument("--cleanup-plan", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_openssl_actual_execution_preflight_report(
        source_pin_digest=args.source_pin_digest,
        trace_contract_digest=args.trace_contract_digest,
        workspace_root=args.workspace_root,
        cleanup_plan=args.cleanup_plan,
    )
    validate_openssl_actual_execution_preflight_report(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote OpenSSL actual execution preflight report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

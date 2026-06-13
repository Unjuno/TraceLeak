#!/usr/bin/env python3
"""Build an OpenSSL isolated execution plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_actual_execution_preflight import (
    build_openssl_actual_execution_preflight_report,
)
from traceleak.openssl_isolated_execution_plan import (
    build_openssl_isolated_execution_plan,
    validate_openssl_isolated_execution_plan,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL isolated execution plan.")
    parser.add_argument("--out", required=True, type=Path, help="Output JSON path.")
    parser.add_argument("--source-pin-digest", required=True)
    parser.add_argument("--trace-contract-digest", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--cleanup-plan", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    preflight_report = build_openssl_actual_execution_preflight_report(
        source_pin_digest=args.source_pin_digest,
        trace_contract_digest=args.trace_contract_digest,
        workspace_root=args.workspace_root,
        cleanup_plan=args.cleanup_plan,
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=preflight_report)
    validate_openssl_isolated_execution_plan(plan)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote OpenSSL isolated execution plan: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

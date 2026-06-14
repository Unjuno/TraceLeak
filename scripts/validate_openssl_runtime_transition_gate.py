#!/usr/bin/env python3
"""Build or validate an OpenSSL runtime transition gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.openssl_runtime_transition_gate import (
    build_openssl_runtime_transition_gate,
    validate_openssl_runtime_transition_gate,
    write_openssl_runtime_transition_gate,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or validate an OpenSSL runtime transition gate.")
    parser.add_argument("--gate", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-14T00:00:00Z")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.gate is not None:
            gate = json.loads(args.gate.read_text(encoding="utf-8"))
            if not isinstance(gate, dict):
                raise ValueError("JSON root must be an object")
            validate_openssl_runtime_transition_gate(gate)
        else:
            gate = build_openssl_runtime_transition_gate(
                reviewer=args.reviewer,
                reviewed_at=args.reviewed_at,
            )
        if args.out is not None:
            write_openssl_runtime_transition_gate(args.out, gate)
    except Exception as exc:
        print(f"invalid OpenSSL runtime transition gate: {exc}")
        return 1
    print("valid OpenSSL runtime transition gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

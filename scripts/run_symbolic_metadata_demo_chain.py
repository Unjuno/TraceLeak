#!/usr/bin/env python3
"""Run the authored symbolic metadata demo chain."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.symbolic_metadata_demo_chain import (
    build_symbolic_metadata_demo_chain,
    write_symbolic_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_report import (
    render_symbolic_metadata_demo_report,
    write_symbolic_metadata_demo_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the authored symbolic metadata demo chain.")
    parser.add_argument("--out-dir", default=Path("reports/local/symbolic_metadata_demo"), type=Path)
    parser.add_argument("--epochs", default=20, type=int)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-14T00:00:00Z")
    parser.add_argument("--write-report", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        artifacts = build_symbolic_metadata_demo_chain(
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
            epochs=args.epochs,
        )
        paths = write_symbolic_metadata_demo_chain(output_dir=args.out_dir, artifacts=artifacts)
        if args.write_report:
            write_symbolic_metadata_demo_report(
                args.out_dir / "symbolic-demo-report.md",
                render_symbolic_metadata_demo_report(artifacts["demo_summary"]),
            )
    except Exception as exc:
        print(f"invalid symbolic metadata demo chain request: {exc}")
        return 1
    print(f"wrote symbolic metadata demo chain artifacts: {args.out_dir} ({len(paths)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

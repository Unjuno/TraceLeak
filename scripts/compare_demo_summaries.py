#!/usr/bin/env python3
"""Compare metadata-only demo summary JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from traceleak.demo_summary_comparison import (
    build_demo_summary_comparison,
    render_demo_summary_comparison_markdown,
    write_demo_summary_comparison_json,
    write_demo_summary_comparison_markdown,
)


class CompareDemoSummariesCliError(ValueError):
    """Raised when demo summary comparison CLI input is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare metadata demo and symbolic demo summaries.")
    parser.add_argument("--metadata-summary", required=True, type=Path)
    parser.add_argument("--symbolic-summary", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--markdown-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        comparison = build_demo_summary_comparison(
            metadata_summary=_load_json(args.metadata_summary),
            symbolic_summary=_load_json(args.symbolic_summary),
        )
        write_demo_summary_comparison_json(args.out, comparison)
        if args.markdown_out is not None:
            write_demo_summary_comparison_markdown(
                args.markdown_out,
                render_demo_summary_comparison_markdown(comparison),
            )
    except Exception as exc:
        print(f"invalid demo summary comparison request: {exc}")
        return 1
    print(f"wrote demo summary comparison: {args.out}")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise CompareDemoSummariesCliError(f"input file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CompareDemoSummariesCliError("input JSON must be an object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render a Markdown summary from metadata demo JSON outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.metadata_demo_markdown_summary import (
    render_metadata_demo_markdown_summary,
    write_metadata_demo_markdown_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a metadata demo Markdown summary.")
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--ranking", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        markdown = render_metadata_demo_markdown_summary(
            summary=_load(args.summary),
            manifest=_load(args.manifest),
            ranking=_load(args.ranking) if args.ranking else None,
        )
        write_metadata_demo_markdown_summary(args.out, markdown)
    except Exception as exc:
        print(f"invalid metadata demo markdown summary request: {exc}")
        return 1
    print(f"wrote metadata demo markdown summary: {args.out}")
    return 0


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

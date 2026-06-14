#!/usr/bin/env python3
"""Write the local demo dashboard files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.local_demo_dashboard import (
    build_local_demo_dashboard,
    render_local_demo_dashboard_markdown,
    write_local_demo_dashboard_json,
    write_local_demo_dashboard_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write local demo dashboard files.")
    parser.add_argument("--root-dir", default=Path("reports/local"), type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--markdown-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        dashboard = build_local_demo_dashboard(root_dir=args.root_dir)
        write_local_demo_dashboard_json(args.out, dashboard)
        if args.markdown_out:
            write_local_demo_dashboard_markdown(
                args.markdown_out,
                render_local_demo_dashboard_markdown(dashboard),
            )
    except Exception as exc:
        print(f"invalid local demo dashboard request: {exc}")
        return 1
    print(f"wrote local demo dashboard: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

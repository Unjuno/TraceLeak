#!/usr/bin/env python3
"""Write Level 6 artifact files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
    write_openssl_derived_metadata_profile_demo_chain,
)
from traceleak.openssl_derived_metadata_profile_report import (
    render_openssl_derived_metadata_profile_report,
    write_openssl_derived_metadata_profile_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 6 artifact files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level6_profile"), type=Path)
    parser.add_argument("--epochs", default=20, type=int)
    parser.add_argument("--write-report", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        artifacts = build_openssl_derived_metadata_profile_demo_chain(epochs=args.epochs)
        written = write_openssl_derived_metadata_profile_demo_chain(
            output_dir=args.out_dir,
            artifacts=artifacts,
        )
        if args.write_report:
            report = args.out_dir / "profile-demo-report.md"
            write_openssl_derived_metadata_profile_report(
                report,
                render_openssl_derived_metadata_profile_report(artifacts["demo_summary"]),
            )
            written["profile_report"] = report
    except Exception as exc:
        print(f"invalid level6 artifact request: {exc}")
        return 1
    print(f"wrote level6 artifact files: {args.out_dir} ({len(written)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

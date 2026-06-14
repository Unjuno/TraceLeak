#!/usr/bin/env python3
"""Write Level 8 local files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
)
from traceleak.level8_artifact_intake import (
    build_level8_artifact_intake_index,
    build_level8_artifact_intake_manifest,
    render_level8_artifact_intake_report,
    write_level8_artifact_intake_index,
    write_level8_artifact_intake_manifest,
    write_level8_artifact_intake_report,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 8 local files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level8_intake"), type=Path)
    parser.add_argument("--root-dir", default=Path("."), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
        gate = build_level7_review_gate(
            profile_demo_summary=summary,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
            decision="approve_planning_only",
        )
        contract = build_level7_planning_contract(review_gate=gate)
        boundary = build_level7_artifact_boundary_plan(planning_contract=contract)
        manifest = build_level8_artifact_intake_manifest(artifact_boundary_plan=boundary)
        index = build_level8_artifact_intake_index(manifest=manifest, root_dir=args.root_dir)
        report = render_level8_artifact_intake_report(manifest=manifest, index=index)
        write_level8_artifact_intake_manifest(args.out_dir / "level8-manifest.json", manifest)
        write_level8_artifact_intake_index(args.out_dir / "level8-index.json", index)
        write_level8_artifact_intake_report(args.out_dir / "level8-report.md", report)
    except Exception as exc:
        print(f"invalid level8 request: {exc}")
        return 1
    print(f"wrote level8 files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

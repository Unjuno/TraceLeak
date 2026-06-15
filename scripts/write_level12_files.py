#!/usr/bin/env python3
"""Write Level 12 review checkpoint files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level10_review_packet import build_level10_review_packet
from traceleak.level11_next_todo_proposal import build_level11_next_todo_proposal
from traceleak.level12_review_checkpoint import (
    build_level12_review_checkpoint,
    render_level12_review_checkpoint_report,
    write_level12_review_checkpoint,
    write_level12_review_checkpoint_report,
)
from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_gate,
)
from traceleak.level8_artifact_intake import (
    build_level8_artifact_intake_index,
    build_level8_artifact_intake_manifest,
)
from traceleak.level9_readiness_audit import build_level9_readiness_audit
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 12 review checkpoint files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level12_checkpoint"), type=Path)
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
        audit = build_level9_readiness_audit(intake_index=index)
        packet = build_level10_review_packet(
            readiness_audit=audit,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        proposal = build_level11_next_todo_proposal(
            review_packet=packet,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        checkpoint = build_level12_review_checkpoint(
            next_todo_proposal=proposal,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level12_review_checkpoint_report(checkpoint)
        write_level12_review_checkpoint(args.out_dir / "level12-review-checkpoint.json", checkpoint)
        write_level12_review_checkpoint_report(args.out_dir / "level12-review-checkpoint.md", report)
    except Exception as exc:
        print(f"invalid level12 request: {exc}")
        return 1
    print(f"wrote level12 review checkpoint files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

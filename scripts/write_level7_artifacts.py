#!/usr/bin/env python3
"""Write Level 7 planning artifact files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level7_review_gate import (
    build_level7_artifact_boundary_plan,
    build_level7_planning_contract,
    build_level7_review_checklist,
    build_level7_review_gate,
    render_level7_readiness_report,
    write_level7_artifact_boundary_plan,
    write_level7_planning_contract,
    write_level7_readiness_report,
    write_level7_review_checklist,
    write_level7_review_gate,
)
from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 7 planning artifact files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level7_planning"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    parser.add_argument("--approve-planning-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        decision = "approve_planning_only" if args.approve_planning_only else "defer"
        summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
        gate = build_level7_review_gate(
            profile_demo_summary=summary,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
            decision=decision,
        )
        write_level7_review_gate(args.out_dir / "level7-review-gate.json", gate)
        if decision != "approve_planning_only":
            print("wrote level7 review gate only; planning was not approved")
            return 0
        contract = build_level7_planning_contract(review_gate=gate)
        boundary = build_level7_artifact_boundary_plan(planning_contract=contract)
        checklist = build_level7_review_checklist(artifact_boundary_plan=boundary)
        readiness = render_level7_readiness_report(
            review_gate=gate,
            planning_contract=contract,
            artifact_boundary_plan=boundary,
            checklist=checklist,
        )
        write_level7_planning_contract(args.out_dir / "level7-planning-contract.json", contract)
        write_level7_artifact_boundary_plan(args.out_dir / "level7-artifact-boundary-plan.json", boundary)
        write_level7_review_checklist(args.out_dir / "level7-review-checklist.json", checklist)
        write_level7_readiness_report(args.out_dir / "level7-readiness-report.md", readiness)
    except Exception as exc:
        print(f"invalid level7 artifact request: {exc}")
        return 1
    print(f"wrote level7 planning artifact files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

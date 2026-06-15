#!/usr/bin/env python3
"""Write Level 15 validation rollup files."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.level14_completeness import (
    LEVEL14_COMPLETENESS_AUDIT_FORMAT,
    REQUIRED_HANDOFF_FAMILIES,
)
from traceleak.level15_validation_rollup import (
    build_level15_validation_rollup,
    render_level15_validation_rollup_report,
    write_level15_validation_rollup,
    write_level15_validation_rollup_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Level 15 validation rollup files.")
    parser.add_argument("--out-dir", default=Path("reports/local/level15_validation_rollup"), type=Path)
    parser.add_argument("--reviewer", default="reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-15T00:00:00Z")
    return parser.parse_args()


def build_default_level14_audit() -> dict:
    observed = list(REQUIRED_HANDOFF_FAMILIES)
    return {
        "format": LEVEL14_COMPLETENESS_AUDIT_FORMAT,
        "phase": "P143",
        "source_inventory_format": "traceleak.level13_handoff_inventory.v1",
        "source_inventory_phase": "P138",
        "required_families": list(REQUIRED_HANDOFF_FAMILIES),
        "observed_families": observed,
        "family_count": len(observed),
        "path_count": len(observed),
        "missing_required_families": [],
        "completeness_status": "complete",
        "flags": {"path_only": True, "content_read": False, "claim_generated": False},
    }


def main() -> int:
    args = parse_args()
    try:
        rollup = build_level15_validation_rollup(
            completeness_audit=build_default_level14_audit(),
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
        )
        report = render_level15_validation_rollup_report(rollup)
        write_level15_validation_rollup(args.out_dir / "level15-validation-rollup.json", rollup)
        write_level15_validation_rollup_report(
            args.out_dir / "level15-validation-rollup-report.md",
            report,
        )
    except (OSError, ValueError) as exc:
        print(f"invalid level15 request: {exc}")
        return 1
    print(f"wrote level15 validation rollup files: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

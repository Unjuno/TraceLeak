"""Synthetic target used to generate public-safe TraceLeak examples.

This module creates a controlled source-level signal. It does not use real
cryptographic secrets. Labels are synthetic and lab-only.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def make_run(index: int, *, leak: bool) -> dict[str, Any]:
    """Create one public-safe synthetic trace run."""

    label = index % 2
    rng = random.Random(index)
    branch_taken = bool(label) if leak else bool(rng.randint(0, 1))
    loop_count = 64 + label * 32 + rng.randint(0, 7) if leak else 64 + rng.randint(0, 63)

    return {
        "run_id": f"synthetic_{index:06d}",
        "target": "synthetic-leak" if leak else "synthetic-control",
        "target_version": "v1",
        "view": "redacted",
        "events": [
            {
                "step": 1,
                "phase": "setup",
                "function": "synthetic_target",
                "file": "examples/synthetic/target.py",
                "line": 17,
                "event_type": "phase",
                "name": "start",
            },
            {
                "step": 2,
                "phase": "controlled_signal",
                "function": "synthetic_target",
                "file": "examples/synthetic/target.py",
                "line": 19,
                "event_type": "branch",
                "name": "synthetic_branch_event",
                "value_redacted": {"branch_taken": branch_taken},
            },
            {
                "step": 3,
                "phase": "controlled_signal",
                "function": "synthetic_target",
                "file": "examples/synthetic/target.py",
                "line": 20,
                "event_type": "loop",
                "name": "synthetic_loop_event",
                "value_redacted": {
                    "bucket": bucket_loop_count(loop_count),
                    "loop_count_mod_8": loop_count % 8,
                },
            },
        ],
        "labels_lab_only": {"synthetic_bucket": label},
    }


def bucket_loop_count(value: int) -> str:
    """Return a coarse public-safe loop-count bucket."""

    if value < 80:
        return "064-079"
    if value < 96:
        return "080-095"
    if value < 112:
        return "096-111"
    return "112-127"


def write_jsonl(path: Path, runs: list[dict[str, Any]]) -> None:
    """Write runs as JSONL."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for run in runs:
            handle.write(json.dumps(run, sort_keys=True, separators=(",", ":")) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic TraceLeak traces.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL path")
    parser.add_argument("--runs", type=int, default=16, help="Number of runs")
    parser.add_argument("--control", action="store_true", help="Generate control traces without the signal")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs <= 0:
        raise SystemExit("error: --runs must be positive")
    runs = [make_run(index, leak=not args.control) for index in range(args.runs)]
    write_jsonl(args.out, runs)
    print(f"wrote synthetic traces: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

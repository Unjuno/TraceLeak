#!/usr/bin/env python3
"""Run a lightweight TraceLeak experiment config.

Usage:
  python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json
  python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json --out-dir reports/local
"""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.workflow import run_lightweight_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight TraceLeak experiment config.")
    parser.add_argument("config", type=Path, help="Experiment config JSON")
    parser.add_argument("--out-dir", type=Path, default=Path("reports/local"), help="Output directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_lightweight_experiment(args.config, out_dir=args.out_dir)
    for path in result.written_paths:
        print(f"wrote: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

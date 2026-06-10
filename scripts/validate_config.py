#!/usr/bin/env python3
"""Validate TraceLeak experiment config files.

Usage:
  python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
  python scripts/validate_config.py --allow-raw local_raw_experiment/config.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.config import ConfigError, config_summary, load_config, validate_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate TraceLeak experiment config files.")
    parser.add_argument("paths", nargs="+", type=Path, help="Config JSON files to validate")
    parser.add_argument(
        "--allow-raw",
        action="store_true",
        help="Allow raw/cheat views and raw-trace flags. Intended only for local lab configs.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summaries")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = 0
    summaries = []
    for path in args.paths:
        try:
            config = load_config(path)
            validate_config(config, public_safe=not args.allow_raw)
        except ConfigError as exc:
            failed += 1
            print(f"{path}: invalid: {exc}")
            continue
        summary = config_summary(config)
        summaries.append(summary)
        if not args.json:
            print(f"{path}: ok ({summary['experiment_id']}, {summary['view']}, {summary['metric']})")

    if args.json:
        print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

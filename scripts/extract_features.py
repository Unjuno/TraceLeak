#!/usr/bin/env python3
"""Extract lightweight feature vectors from TraceLeak JSONL traces.

Usage:
  python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.json
  python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.csv --format csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from traceleak.features import build_feature_matrix, extract_feature_vector
from traceleak.io import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract lightweight TraceLeak feature vectors.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSONL trace file")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output feature file")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("--allow-raw", action="store_true", help="Allow raw or cheat views")
    return parser.parse_args()


def write_json(path: Path, runs: list[dict[str, Any]], *, allow_raw: bool) -> None:
    payload = [
        {
            "run_id": run["run_id"],
            "target": run["target"],
            "view": run["view"],
            "features": extract_feature_vector(run, allow_raw=allow_raw),
        }
        for run in runs
    ]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, runs: list[dict[str, Any]], *, allow_raw: bool) -> None:
    feature_names, matrix = build_feature_matrix(runs, allow_raw=allow_raw)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", *feature_names])
        for run, row in zip(runs, matrix, strict=True):
            writer.writerow([run["run_id"], *row])


def main() -> int:
    args = parse_args()
    runs = list(read_jsonl(args.input_path))
    if not runs:
        raise SystemExit(f"error: no runs found in {args.input_path}")

    if args.format == "json":
        write_json(args.output_path, runs, allow_raw=args.allow_raw)
    else:
        write_csv(args.output_path, runs, allow_raw=args.allow_raw)
    print(f"wrote features: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

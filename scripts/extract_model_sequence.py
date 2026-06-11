#!/usr/bin/env python3
"""Extract variable/control-flow model sequences from TraceLeak JSONL traces.

Usage:
  python scripts/extract_model_sequence.py --in examples/synthetic/synthetic_trace_sample.jsonl --out model_sequences.json
  python scripts/extract_model_sequence.py --in examples/synthetic/synthetic_trace_sample.jsonl --out model_sequences.json --counts
  python scripts/extract_model_sequence.py --in examples/synthetic/synthetic_trace_sample.jsonl --out model_sequences.json --counts --label-key secret_bucket
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from traceleak.model_features import (
    ModelFeatureError,
    sequence_token_counts,
    trace_to_model_sequence,
)
from traceleak.schema import TraceSchemaError, validate_run


class ModelSequenceCliError(ValueError):
    """Raised when model sequence extraction fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract public-safe variable/control-flow model sequences from TraceLeak JSONL traces."
    )
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input JSONL trace file")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output JSON file")
    parser.add_argument(
        "--allow-raw",
        action="store_true",
        help="Allow raw/cheat views. This is for local-only upper-bound experiments.",
    )
    parser.add_argument(
        "--counts",
        action="store_true",
        help="Include collapsed token counts for lightweight baselines.",
    )
    parser.add_argument(
        "--label-key",
        help="Optional labels_lab_only key to copy into each output record as label.",
    )
    parser.add_argument(
        "--no-redacted-values",
        action="store_true",
        help="Omit redacted value-derived tokens from sequence steps.",
    )
    return parser.parse_args()


def load_jsonl_runs(path: Path) -> list[dict[str, Any]]:
    """Load run dictionaries from a JSONL trace file."""

    if not path.exists():
        raise ModelSequenceCliError(f"input file not found: {path}")

    runs: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                run = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ModelSequenceCliError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(run, dict):
                raise ModelSequenceCliError(f"{path}:{line_number}: each JSONL record must be an object")
            runs.append(run)

    if not runs:
        raise ModelSequenceCliError(f"no trace runs found in {path}")
    return runs


def extract_model_sequences(
    runs: list[dict[str, Any]],
    *,
    allow_raw: bool = False,
    include_counts: bool = False,
    include_redacted_values: bool = True,
    label_key: str | None = None,
) -> list[dict[str, Any]]:
    """Extract model sequence records from run dictionaries."""

    records: list[dict[str, Any]] = []
    for index, run in enumerate(runs, start=1):
        try:
            validate_run(run, public_export=not allow_raw)
            sequence = trace_to_model_sequence(
                run,
                allow_raw=allow_raw,
                include_redacted_values=include_redacted_values,
            )
        except (TraceSchemaError, ModelFeatureError) as exc:
            run_id = run.get("run_id", f"record_{index}")
            raise ModelSequenceCliError(f"run {run_id!r} is invalid: {exc}") from exc

        record: dict[str, Any] = {
            "run_id": run["run_id"],
            "target": run["target"],
            "target_version": run["target_version"],
            "view": run["view"],
            "sequence": sequence,
        }
        if include_counts:
            record["token_counts"] = sequence_token_counts(sequence)
        if label_key is not None:
            record["label"] = _label_from_run(run, label_key)
        records.append(record)
    return records


def build_output(
    *,
    input_path: Path,
    records: list[dict[str, Any]],
    allow_raw: bool,
    include_counts: bool,
    include_redacted_values: bool,
    label_key: str | None = None,
) -> dict[str, Any]:
    """Build the output JSON payload."""

    payload: dict[str, Any] = {
        "format": "traceleak.model_sequence.v1",
        "input": str(input_path),
        "run_count": len(records),
        "public_safe": not allow_raw,
        "include_counts": include_counts,
        "include_redacted_values": include_redacted_values,
        "records": records,
    }
    if label_key is not None:
        payload["label_name"] = label_key
        payload["contains_lab_only_labels"] = True
    return payload


def write_output(path: Path, payload: dict[str, Any]) -> None:
    """Write the output JSON payload."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _label_from_run(run: dict[str, Any], label_key: str) -> str:
    labels = run.get("labels_lab_only")
    if not isinstance(labels, dict):
        raise ModelSequenceCliError(f"run {run['run_id']!r} has no labels_lab_only object")
    if label_key not in labels:
        raise ModelSequenceCliError(f"run {run['run_id']!r} is missing labels_lab_only.{label_key}")
    return str(labels[label_key])


def main() -> int:
    args = parse_args()
    try:
        runs = load_jsonl_runs(args.input_path)
        records = extract_model_sequences(
            runs,
            allow_raw=args.allow_raw,
            include_counts=args.counts,
            include_redacted_values=not args.no_redacted_values,
            label_key=args.label_key,
        )
        payload = build_output(
            input_path=args.input_path,
            records=records,
            allow_raw=args.allow_raw,
            include_counts=args.counts,
            include_redacted_values=not args.no_redacted_values,
            label_key=args.label_key,
        )
        write_output(args.output_path, payload)
    except ModelSequenceCliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote model sequences: {args.output_path} ({len(records)} run(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

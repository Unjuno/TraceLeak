#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from traceleak.model_sequence_comparison_reporting import (
    model_sequence_comparison_report_dict,
    model_sequence_comparison_report_markdown,
)
from traceleak.model_sequence_mlp_comparison import compare_model_sequence_mlp_to_baseline

DEFAULT_OUT = Path("reports/local")
SAMPLE = Path("examples/toy_rsa_like/model_sequence_nn_count_pattern_sample.json")
CONTROLS = [
    Path("examples/toy_rsa_like/model_sequence_nn_control_seed_001.json"),
    Path("examples/toy_rsa_like/model_sequence_nn_control_seed_002.json"),
    Path("examples/toy_rsa_like/model_sequence_nn_control_seed_003.json"),
]
EXPECTED = [
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:witness_refine_round",
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:acceptance_confirm_round",
]
TOY_LOCAL_VALIDATION_NOTES = [
    "Toy/local validation only: this MLP chain uses examples/toy_rsa_like sample data.",
    "This runner does not build, run, instrument, or collect actual OpenSSL traces.",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the toy RSA-like MLP comparison/control/attribution report chain."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory for generated report artifacts. Defaults to reports/local.",
    )
    return parser.parse_args(argv)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out = args.out_dir
    result = compare_model_sequence_mlp_to_baseline(
        load(SAMPLE), epochs=200, learning_rate=0.2, hidden_size=8
    )
    result["validation_scope"] = "toy_local_validation"
    result["actual_trace_derived"] = False
    result["notes"] = list(result.get("notes", [])) + TOY_LOCAL_VALIDATION_NOTES
    controls = [
        compare_model_sequence_mlp_to_baseline(load(path), epochs=200, learning_rate=0.2, hidden_size=8)
        for path in CONTROLS
    ]
    report = model_sequence_comparison_report_dict(
        result,
        controls=controls,
        expected_attribution_tokens=EXPECTED,
    )
    report["validation_scope"] = "toy_local_validation"
    report["actual_trace_derived"] = False
    dump(out / "toy_rsa_like_model_sequence_mlp_comparison.json", result)
    for index, control in enumerate(controls, start=1):
        dump(out / f"toy_rsa_like_model_sequence_mlp_control_seed_{index:03d}_comparison.json", control)
    dump(out / "toy_rsa_like_model_sequence_mlp_comparison_report.json", report)
    (out / "toy_rsa_like_model_sequence_mlp_comparison.md").write_text(
        model_sequence_comparison_report_markdown(report), encoding="utf-8"
    )
    print(f"wrote MLP report chain artifacts: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

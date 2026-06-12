#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from traceleak.model_sequence_mlp_comparison import compare_model_sequence_mlp_to_baseline

DEFAULT_OUT = Path("reports/local")
SRC = Path("examples/toy_rsa_like/model_sequence_nn_count_pattern_sample.json")
EXPECTED = [
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:witness_refine_round",
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:acceptance_confirm_round",
]
TOY_LOCAL_VALIDATION_NOTES = [
    "Toy/local validation only: this MLP expected-token check uses examples/toy_rsa_like sample data.",
    "This runner does not build, run, instrument, or collect actual OpenSSL traces.",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the toy RSA-like MLP expected-token sensitivity check."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory for generated expected-token artifacts. Defaults to reports/local.",
    )
    return parser.parse_args(argv)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def drop_expected_tokens(data: dict[str, Any]) -> dict[str, Any]:
    changed_data = copy.deepcopy(data)
    for record in changed_data["records"]:
        counts = record["token_counts"]
        for name in EXPECTED:
            counts.pop(name, None)
    return changed_data


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out = args.out_dir
    data = load(SRC)
    base = compare_model_sequence_mlp_to_baseline(data, epochs=200, learning_rate=0.2, hidden_size=8)
    changed = compare_model_sequence_mlp_to_baseline(
        drop_expected_tokens(data), epochs=200, learning_rate=0.2, hidden_size=8
    )
    drop = max(
        0.0,
        float(base["neural"]["leave_one_out_accuracy"])
        - float(changed["neural"]["leave_one_out_accuracy"]),
    )
    status = "expected_token_sensitive" if drop >= 0.25 else "expected_token_stable"
    report = {
        "status": status,
        "nn_accuracy_drop": drop,
        "expected_tokens": EXPECTED,
        "validation_scope": "toy_local_validation",
        "actual_trace_derived": False,
        "notes": TOY_LOCAL_VALIDATION_NOTES,
        "base": base,
        "changed": changed,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "toy_rsa_like_model_sequence_mlp_expected_check.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "toy_rsa_like_model_sequence_mlp_expected_check.md").write_text(
        "# MLP Expected Token Check\n\n"
        f"- Status: `{status}`\n"
        f"- NN accuracy drop: `{drop}`\n"
        "- Validation scope: `toy_local_validation`\n"
        "- Actual trace derived: `false`\n\n"
        "## Notes\n\n"
        + "".join(f"- {note}\n" for note in TOY_LOCAL_VALIDATION_NOTES),
        encoding="utf-8",
    )
    print(f"wrote MLP expected token check artifacts: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

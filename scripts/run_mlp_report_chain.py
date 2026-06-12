#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from traceleak.model_sequence_comparison_reporting import (
    model_sequence_comparison_report_dict,
    model_sequence_comparison_report_markdown,
)
from traceleak.model_sequence_mlp_comparison import compare_model_sequence_mlp_to_baseline

OUT = Path("reports/local")
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


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    result = compare_model_sequence_mlp_to_baseline(load(SAMPLE), epochs=200, learning_rate=0.2, hidden_size=8)
    controls = [
        compare_model_sequence_mlp_to_baseline(load(path), epochs=200, learning_rate=0.2, hidden_size=8)
        for path in CONTROLS
    ]
    report = model_sequence_comparison_report_dict(
        result,
        controls=controls,
        expected_attribution_tokens=EXPECTED,
    )
    dump(OUT / "toy_rsa_like_model_sequence_mlp_comparison.json", result)
    for index, control in enumerate(controls, start=1):
        dump(OUT / f"toy_rsa_like_model_sequence_mlp_control_seed_{index:03d}_comparison.json", control)
    dump(OUT / "toy_rsa_like_model_sequence_mlp_comparison_report.json", report)
    (OUT / "toy_rsa_like_model_sequence_mlp_comparison.md").write_text(
        model_sequence_comparison_report_markdown(report), encoding="utf-8"
    )
    print(f"wrote MLP report chain artifacts: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

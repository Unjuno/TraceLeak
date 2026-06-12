#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

from traceleak.model_sequence_mlp_comparison import compare_model_sequence_mlp_to_baseline

OUT = Path("reports/local")
SRC = Path("examples/toy_rsa_like/model_sequence_nn_count_pattern_sample.json")
EXPECTED = [
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:witness_refine_round",
    "event_token=loop:candidate_filter:toy_rsa_like_keygen:acceptance_confirm_round",
]


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    base = compare_model_sequence_mlp_to_baseline(data, epochs=200, learning_rate=0.2, hidden_size=8)
    changed_data = copy.deepcopy(data)
    for record in changed_data["records"]:
        counts = record["token_counts"]
        for name in EXPECTED:
            counts.pop(name, None)
    changed = compare_model_sequence_mlp_to_baseline(changed_data, epochs=200, learning_rate=0.2, hidden_size=8)
    drop = max(0.0, float(base["neural"]["leave_one_out_accuracy"]) - float(changed["neural"]["leave_one_out_accuracy"]))
    status = "expected_token_sensitive" if drop >= 0.25 else "expected_token_stable"
    report = {"status": status, "nn_accuracy_drop": drop, "expected_tokens": EXPECTED, "base": base, "changed": changed}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "toy_rsa_like_model_sequence_mlp_expected_check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "toy_rsa_like_model_sequence_mlp_expected_check.md").write_text(f"# MLP Expected Token Check\n\n- Status: `{status}`\n- NN accuracy drop: `{drop}`\n", encoding="utf-8")
    print(f"wrote MLP expected token check artifacts: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""End-to-end demo chain for authored symbolic metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.evaluate_model_sequence_baseline import build_result as build_baseline_result
from traceleak.metadata_symbolic_authoring import (
    build_symbolic_metadata_input,
    validate_symbolic_metadata_input,
)
from traceleak.model_results import validate_model_result
from traceleak.model_sequence_nn import train_model_sequence_nn_result
from traceleak.openssl_derived_metadata_adapter import adapt_openssl_derived_metadata_to_model_sequence
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate

SYMBOLIC_METADATA_DEMO_CHAIN_FORMAT = "traceleak.symbolic_metadata_demo_chain.v1"
SYMBOLIC_METADATA_DEMO_CHAIN_PHASE = "P84"
DEFAULT_OUTPUT_NAMES = {
    "symbolic_metadata_input": "symbolic-metadata-input.json",
    "runtime_gate": "runtime-gate.json",
    "model_sequence_sample": "symbolic-model-sequence.json",
    "baseline_result": "symbolic-baseline-result.json",
    "nn_result": "symbolic-nn-result.json",
    "demo_summary": "symbolic-demo-summary.json",
}


class SymbolicMetadataDemoChainError(ValueError):
    """Raised when the authored symbolic metadata demo chain is invalid."""


def build_symbolic_metadata_demo_chain(
    *,
    records: list[dict[str, Any]] | None = None,
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-14T00:00:00Z",
    epochs: int = 20,
) -> dict[str, Any]:
    """Build authored symbolic metadata, adapter output, baseline, NN, and summary."""

    if epochs <= 0:
        raise SymbolicMetadataDemoChainError("epochs must be positive")
    symbolic_input = build_symbolic_metadata_input(records=records or _default_records())
    runtime_gate = build_openssl_runtime_transition_gate(
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )
    sample = adapt_openssl_derived_metadata_to_model_sequence(
        metadata_input=symbolic_input,
        runtime_gate=runtime_gate,
    )
    baseline_result = build_baseline_result(sample)
    baseline_result.setdefault("notes", []).append(
        "Authored symbolic metadata-only demo baseline; not OpenSSL leakage evidence."
    )
    nn_result = train_model_sequence_nn_result(
        sample,
        experiment_id="exp_symbolic_metadata_demo",
        epochs=epochs,
        learning_rate=0.8,
    )
    nn_result.setdefault("notes", []).append(
        "Authored symbolic metadata-only demo NN result; not OpenSSL leakage evidence."
    )
    validate_model_result(nn_result)
    summary = build_symbolic_metadata_demo_summary(
        symbolic_input=symbolic_input,
        sample=sample,
        baseline_result=baseline_result,
        nn_result=nn_result,
    )
    return {
        "symbolic_metadata_input": symbolic_input,
        "runtime_gate": runtime_gate,
        "model_sequence_sample": sample,
        "baseline_result": baseline_result,
        "nn_result": nn_result,
        "demo_summary": summary,
    }


def build_symbolic_metadata_demo_summary(
    *,
    symbolic_input: dict[str, Any],
    sample: dict[str, Any],
    baseline_result: dict[str, Any],
    nn_result: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact JSON summary for the authored symbolic metadata demo."""

    validate_symbolic_metadata_input(symbolic_input)
    validate_model_result(nn_result)
    summary = {
        "format": SYMBOLIC_METADATA_DEMO_CHAIN_FORMAT,
        "phase": SYMBOLIC_METADATA_DEMO_CHAIN_PHASE,
        "mode": "metadata_only_symbolic_demo",
        "input_format": symbolic_input["format"],
        "sample_format": sample["format"],
        "artifact_format": sample["artifact_format"],
        "target": sample["target"],
        "view": sample["view"],
        "record_count": sample["run_count"],
        "label_name": sample["label_name"],
        "label_distribution": baseline_result["label_distribution"],
        "baseline_summary": {
            "majority_accuracy": baseline_result["baselines"]["leave_one_out_majority_accuracy"],
            "nearest_neighbor_accuracy": baseline_result["baselines"][
                "leave_one_out_nearest_neighbor_accuracy"
            ],
        },
        "nn_summary": {
            "model_name": nn_result["model"]["name"],
            "accuracy": nn_result["metrics"]["leave_one_out"]["accuracy"],
            "attribution_count": len(nn_result.get("attributions", [])),
        },
        "flags": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "openssl_leakage_claim": False,
            "model_result_generated": True,
            "baseline_result_generated": True,
        },
        "notes": [
            "Authored symbolic metadata-only demo output.",
            "This does not claim or prove OpenSSL leakage.",
        ],
    }
    validate_symbolic_metadata_demo_summary(summary)
    return summary


def validate_symbolic_metadata_demo_summary(summary: dict[str, Any]) -> None:
    """Validate the authored symbolic metadata demo summary shape."""

    _eq(summary.get("format"), SYMBOLIC_METADATA_DEMO_CHAIN_FORMAT, "summary.format")
    _eq(summary.get("phase"), SYMBOLIC_METADATA_DEMO_CHAIN_PHASE, "summary.phase")
    _eq(summary.get("mode"), "metadata_only_symbolic_demo", "summary.mode")
    _eq(summary.get("sample_format"), "traceleak.model_sequence.v1", "summary.sample_format")
    _eq(summary.get("target"), "openssl-derived-metadata", "summary.target")
    _eq(summary.get("view"), "meta", "summary.view")
    if not isinstance(summary.get("record_count"), int) or summary["record_count"] < 4:
        raise SymbolicMetadataDemoChainError("summary.record_count must be at least four")
    labels = summary.get("label_distribution")
    if not isinstance(labels, dict) or len(labels) < 2:
        raise SymbolicMetadataDemoChainError("summary.label_distribution must contain at least two labels")
    _score(summary["baseline_summary"].get("majority_accuracy"), "summary.baseline_summary.majority_accuracy")
    _score(
        summary["baseline_summary"].get("nearest_neighbor_accuracy"),
        "summary.baseline_summary.nearest_neighbor_accuracy",
    )
    _score(summary["nn_summary"].get("accuracy"), "summary.nn_summary.accuracy")
    if not isinstance(summary["nn_summary"].get("attribution_count"), int):
        raise SymbolicMetadataDemoChainError("summary.nn_summary.attribution_count must be an integer")
    flags = summary.get("flags")
    if not isinstance(flags, dict):
        raise SymbolicMetadataDemoChainError("summary.flags must be an object")
    for key in ["metadata_only", "payload_free", "public_safe", "model_result_generated", "baseline_result_generated"]:
        _eq(flags.get(key), True, f"summary.flags.{key}")
    _eq(flags.get("openssl_leakage_claim"), False, "summary.flags.openssl_leakage_claim")


def write_symbolic_metadata_demo_chain(*, output_dir: Path, artifacts: dict[str, Any]) -> dict[str, Path]:
    """Write authored symbolic metadata demo outputs as deterministic JSON."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for key, filename in DEFAULT_OUTPUT_NAMES.items():
        if key not in artifacts:
            raise SymbolicMetadataDemoChainError(f"missing artifact: {key}")
        path = output_dir / filename
        path.write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths[key] = path
    return paths


def _default_records() -> list[dict[str, str]]:
    return [
        {
            "source_region_token": "ct_helper_family_a",
            "transition_token": "branch_symbolic_a",
            "label": "bucket_a",
        },
        {
            "source_region_token": "ct_helper_family_a2",
            "transition_token": "branch_symbolic_a2",
            "label": "bucket_a",
        },
        {
            "source_region_token": "ct_helper_family_b",
            "transition_token": "branch_symbolic_b",
            "label": "bucket_b",
        },
        {
            "source_region_token": "ct_helper_family_b2",
            "transition_token": "branch_symbolic_b2",
            "label": "bucket_b",
        },
    ]


def _score(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or value < 0 or value > 1:
        raise SymbolicMetadataDemoChainError(f"{name} must be a score between 0 and 1")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise SymbolicMetadataDemoChainError(f"{name} must be {expected!r}")

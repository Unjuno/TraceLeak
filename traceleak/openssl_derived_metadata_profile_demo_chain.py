"""Level 6 demo chain for OpenSSL-derived metadata profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.evaluate_model_sequence_baseline import build_result as build_baseline_result
from traceleak.model_results import validate_model_result
from traceleak.model_sequence_nn import train_model_sequence_nn_result
from traceleak.openssl_derived_metadata_adapter import adapt_openssl_derived_metadata_to_model_sequence
from traceleak.openssl_derived_metadata_profile import (
    adapt_openssl_derived_metadata_profile_to_adapter_input,
    build_openssl_derived_metadata_profile_input,
    validate_openssl_derived_metadata_profile_input,
)
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate

OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT = (
    "traceleak.openssl_derived_metadata_profile_demo_chain.v1"
)
OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_PHASE = "P99"
DEFAULT_PROFILE_DEMO_OUTPUT_NAMES = {
    "profile_input": "profile-input.json",
    "adapter_input": "adapter-input.json",
    "runtime_gate": "runtime-gate.json",
    "model_sequence_sample": "profile-model-sequence.json",
    "baseline_result": "profile-baseline-result.json",
    "nn_result": "profile-nn-result.json",
    "demo_summary": "profile-demo-summary.json",
}


class OpenSSLDerivedMetadataProfileDemoChainError(ValueError):
    """Raised when the Level 6 profile demo chain is invalid."""


def build_openssl_derived_metadata_profile_demo_chain(
    *,
    records: list[dict[str, Any]] | None = None,
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-14T00:00:00Z",
    epochs: int = 20,
) -> dict[str, Any]:
    """Build Level 6 profile demo artifacts in memory."""

    if epochs <= 0:
        raise OpenSSLDerivedMetadataProfileDemoChainError("epochs must be positive")
    profile_input = build_openssl_derived_metadata_profile_input(records=records)
    validate_openssl_derived_metadata_profile_input(profile_input)
    adapter_input = adapt_openssl_derived_metadata_profile_to_adapter_input(profile_input)
    runtime_gate = build_openssl_runtime_transition_gate(
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )
    model_sequence_sample = adapt_openssl_derived_metadata_to_model_sequence(
        metadata_input=adapter_input,
        runtime_gate=runtime_gate,
    )
    baseline_result = build_baseline_result(model_sequence_sample)
    nn_result = train_model_sequence_nn_result(
        model_sequence_sample,
        experiment_id="openssl-derived-metadata-profile-demo-nn",
        epochs=epochs,
        learning_rate=0.1,
    )
    validate_model_result(nn_result)
    demo_summary = build_openssl_derived_metadata_profile_demo_summary(
        profile_input=profile_input,
        adapter_input=adapter_input,
        model_sequence_sample=model_sequence_sample,
        baseline_result=baseline_result,
        nn_result=nn_result,
    )
    return {
        "profile_input": profile_input,
        "adapter_input": adapter_input,
        "runtime_gate": runtime_gate,
        "model_sequence_sample": model_sequence_sample,
        "baseline_result": baseline_result,
        "nn_result": nn_result,
        "demo_summary": demo_summary,
    }


def build_openssl_derived_metadata_profile_demo_summary(
    *,
    profile_input: dict[str, Any],
    adapter_input: dict[str, Any],
    model_sequence_sample: dict[str, Any],
    baseline_result: dict[str, Any],
    nn_result: dict[str, Any],
) -> dict[str, Any]:
    """Build compact Level 6 profile demo summary."""

    summary = {
        "format": OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT,
        "phase": OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_PHASE,
        "mode": "metadata_only_profile_demo",
        "target": "openssl-derived-metadata",
        "view": "meta",
        "profile_format": profile_input["format"],
        "adapter_input_format": adapter_input["format"],
        "model_sequence_format": model_sequence_sample["format"],
        "record_count": len(profile_input["records"]),
        "label_distribution": dict(sorted(baseline_result["label_distribution"].items())),
        "baseline_summary": {
            "majority_accuracy": baseline_result["baselines"]["leave_one_out_majority_accuracy"],
            "nearest_neighbor_accuracy": baseline_result["baselines"][
                "leave_one_out_nearest_neighbor_accuracy"
            ],
        },
        "nn_summary": {
            "model_name": nn_result["model"]["name"],
            "accuracy": nn_result["metrics"]["leave_one_out"]["accuracy"],
            "attribution_count": len(nn_result["attributions"]),
        },
        "bridge_summary": {
            "profile_to_adapter": True,
            "adapter_to_model_sequence": True,
            "baseline_generated": True,
            "nn_generated": True,
        },
        "flags": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "payload_inspected": False,
            "openssl_leakage_claim": False,
        },
        "next_level": {
            "level": 7,
            "name": "review before OpenSSL runtime proximity",
            "requires_review": True,
        },
    }
    validate_openssl_derived_metadata_profile_demo_summary(summary)
    return summary


def validate_openssl_derived_metadata_profile_demo_summary(summary: dict[str, Any]) -> None:
    """Validate Level 6 profile demo summary."""

    _eq(summary.get("format"), OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT, "summary.format")
    _eq(summary.get("phase"), OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_PHASE, "summary.phase")
    _eq(summary.get("mode"), "metadata_only_profile_demo", "summary.mode")
    if not isinstance(summary.get("record_count"), int) or summary["record_count"] < 4:
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.record_count must be at least four")
    labels = summary.get("label_distribution")
    if not isinstance(labels, dict) or len(labels) < 2:
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.label_distribution invalid")
    baseline = summary.get("baseline_summary")
    if not isinstance(baseline, dict):
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.baseline_summary must be object")
    _score(baseline.get("majority_accuracy"), "summary.baseline_summary.majority_accuracy")
    _score(
        baseline.get("nearest_neighbor_accuracy"),
        "summary.baseline_summary.nearest_neighbor_accuracy",
    )
    nn = summary.get("nn_summary")
    if not isinstance(nn, dict):
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.nn_summary must be object")
    _score(nn.get("accuracy"), "summary.nn_summary.accuracy")
    if not isinstance(nn.get("attribution_count"), int) or nn["attribution_count"] < 0:
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.nn_summary.attribution_count invalid")
    bridge = summary.get("bridge_summary")
    if not isinstance(bridge, dict):
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.bridge_summary must be object")
    for key in ["profile_to_adapter", "adapter_to_model_sequence", "baseline_generated", "nn_generated"]:
        _eq(bridge.get(key), True, f"summary.bridge_summary.{key}")
    flags = summary.get("flags")
    if not isinstance(flags, dict):
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.flags must be object")
    for key in ["metadata_only", "payload_free", "public_safe"]:
        _eq(flags.get(key), True, f"summary.flags.{key}")
    _eq(flags.get("payload_inspected"), False, "summary.flags.payload_inspected")
    _eq(flags.get("openssl_leakage_claim"), False, "summary.flags.openssl_leakage_claim")
    next_level = summary.get("next_level")
    if not isinstance(next_level, dict):
        raise OpenSSLDerivedMetadataProfileDemoChainError("summary.next_level must be object")
    _eq(next_level.get("level"), 7, "summary.next_level.level")
    _eq(next_level.get("requires_review"), True, "summary.next_level.requires_review")


def write_openssl_derived_metadata_profile_demo_chain(
    *,
    output_dir: Path,
    artifacts: dict[str, Any],
) -> dict[str, Path]:
    """Write Level 6 profile demo artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for key, filename in DEFAULT_PROFILE_DEMO_OUTPUT_NAMES.items():
        if key not in artifacts:
            raise OpenSSLDerivedMetadataProfileDemoChainError(f"missing artifact: {key}")
        path = output_dir / filename
        path.write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths[key] = path
    return paths


def _score(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or value < 0 or value > 1:
        raise OpenSSLDerivedMetadataProfileDemoChainError(f"{name} must be a score between 0 and 1")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLDerivedMetadataProfileDemoChainError(f"{name} must be {expected!r}")

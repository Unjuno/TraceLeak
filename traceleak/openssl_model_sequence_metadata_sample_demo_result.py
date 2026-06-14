"""OpenSSL metadata-only model-sequence demo result helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.evaluate_model_sequence_baseline import build_result as build_baseline_result
from traceleak.model_results import validate_model_result
from traceleak.model_sequence_nn import train_model_sequence_nn_result
from traceleak.openssl_model_sequence_metadata_sample import (
    validate_openssl_model_sequence_metadata_sample,
)
from traceleak.openssl_model_sequence_metadata_sample_model_preflight import (
    validate_openssl_model_sequence_metadata_sample_model_preflight,
)

OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_DEMO_RESULT_FORMAT = (
    "traceleak.openssl_model_sequence_metadata_sample_demo_result.v1"
)
DEMO_TRUE_FLAGS = [
    "metadata_only",
    "payload_free",
    "public_safe",
    "baseline_result_generated",
    "model_result_generated",
]
DEMO_FALSE_FLAGS = [
    "openssl_leakage_claim",
    "runtime_action_enabled",
    "payload_access_enabled",
]


class OpenSSLModelSequenceMetadataSampleDemoResultError(ValueError):
    """Raised when a metadata-only sample demo result is invalid."""


def build_openssl_model_sequence_metadata_sample_demo_result(
    *,
    sample: dict[str, Any],
    model_preflight: dict[str, Any],
    output_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
    experiment_id: str = "exp_openssl_metadata_sample_demo",
    epochs: int = 80,
    learning_rate: float = 0.8,
) -> dict[str, Any]:
    """Run metadata-only baseline and NN demo evaluation and return a summary."""

    validate_openssl_model_sequence_metadata_sample(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    validate_openssl_model_sequence_metadata_sample_model_preflight(
        preflight=model_preflight,
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    baseline_result = build_baseline_result(sample)
    baseline_result.setdefault("notes", []).extend(
        [
            "OpenSSL metadata-only public demo result; not OpenSSL leakage evidence.",
            "Synthetic lab-only labels are used only to check the pipeline path.",
        ]
    )
    nn_result = train_model_sequence_nn_result(
        sample,
        experiment_id=experiment_id,
        epochs=epochs,
        learning_rate=learning_rate,
    )
    nn_result.setdefault("notes", []).extend(
        [
            "OpenSSL metadata-only public demo result; not OpenSSL leakage evidence.",
            "Synthetic lab-only labels are used only to check the pipeline path.",
        ]
    )
    validate_model_result(nn_result)
    summary = {
        "format": OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_DEMO_RESULT_FORMAT,
        "status": "metadata_sample_demo_result_ready",
        "phase": "P24",
        "target": "openssl_model_sequence_metadata_sample_demo",
        "mode": "metadata_only_demo",
        "sample_id": sample["sample_metadata"]["sample_id"],
        "input_digest": sample["sample_metadata"]["input_digest"],
        "sample_digest": sample["sample_metadata"]["sample_digest"],
        "source_pin_digest": sample["sample_metadata"]["source_pin_digest"],
        "trace_contract_digest": sample["sample_metadata"]["trace_contract_digest"],
        "feature_namespace": sample["sample_metadata"]["feature_namespace"],
        "record_count": sample["run_count"],
        "label_name": sample["label_name"],
        "label_distribution": model_preflight["label_distribution"],
        "baseline_summary": {
            "result_type": baseline_result["result_type"],
            "majority_accuracy": baseline_result["baselines"][
                "leave_one_out_majority_accuracy"
            ],
            "nearest_neighbor_accuracy": baseline_result["baselines"][
                "leave_one_out_nearest_neighbor_accuracy"
            ],
        },
        "nn_summary": {
            "result_type": nn_result["result_type"],
            "model_name": nn_result["model"]["name"],
            "accuracy": nn_result["metrics"]["leave_one_out"]["accuracy"],
            "attribution_count": len(nn_result.get("attributions", [])),
        },
        "flags": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "baseline_result_generated": True,
            "model_result_generated": True,
            "openssl_leakage_claim": False,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
        },
        "notes": [
            "This is a public metadata-only demo of the model-sequence baseline/NN path.",
            "It does not claim or prove OpenSSL leakage.",
            "It contains no OpenSSL source text, command text, build output, execution output, raw capture, or runtime payload.",
        ],
    }
    validate_openssl_model_sequence_metadata_sample_demo_result(
        summary=summary,
        baseline_result=baseline_result,
        nn_result=nn_result,
        sample=sample,
        model_preflight=model_preflight,
    )
    return {
        "summary": summary,
        "baseline_result": baseline_result,
        "nn_result": nn_result,
    }


def validate_openssl_model_sequence_metadata_sample_demo_result(
    *,
    summary: dict[str, Any],
    baseline_result: dict[str, Any],
    nn_result: dict[str, Any],
    sample: dict[str, Any],
    model_preflight: dict[str, Any],
) -> None:
    """Validate a metadata-only sample demo result summary and its outputs."""

    _require_equal(summary.get("format"), OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_DEMO_RESULT_FORMAT, "format")
    _require_equal(summary.get("status"), "metadata_sample_demo_result_ready", "status")
    _require_equal(summary.get("phase"), "P24", "phase")
    _require_equal(summary.get("target"), "openssl_model_sequence_metadata_sample_demo", "target")
    _require_equal(summary.get("mode"), "metadata_only_demo", "mode")
    for field in [
        "sample_id",
        "input_digest",
        "sample_digest",
        "source_pin_digest",
        "trace_contract_digest",
        "feature_namespace",
    ]:
        _require_equal(summary.get(field), sample["sample_metadata"][field], field)
    _require_equal(summary.get("record_count"), sample["run_count"], "record_count")
    _require_equal(summary.get("label_name"), sample["label_name"], "label_name")
    _require_equal(
        summary.get("label_distribution"),
        model_preflight["label_distribution"],
        "label_distribution",
    )
    _require_equal(baseline_result.get("result_type"), "model_sequence_baseline", "baseline_result.result_type")
    _require_equal(nn_result.get("result_type"), "model_sequence_nn", "nn_result.result_type")
    validate_model_result(nn_result)
    _require_flags(summary)
    notes = _require_non_empty_list(summary.get("notes"), "notes")
    joined_notes = " ".join(str(note) for note in notes).lower()
    if "not claim" not in joined_notes and "does not claim" not in joined_notes:
        raise OpenSSLModelSequenceMetadataSampleDemoResultError(
            "notes must explicitly state that this is not an OpenSSL leakage claim"
        )


def write_openssl_model_sequence_metadata_sample_demo_outputs(
    *,
    summary_path: Path,
    baseline_path: Path,
    nn_path: Path,
    outputs: dict[str, dict[str, Any]],
) -> None:
    """Write P24 summary, baseline result, and NN result as deterministic JSON."""

    for path, payload in [
        (summary_path, outputs["summary"]),
        (baseline_path, outputs["baseline_result"]),
        (nn_path, outputs["nn_result"]),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_flags(summary: dict[str, Any]) -> None:
    flags = _require_dict(summary.get("flags"), "flags")
    for flag in DEMO_TRUE_FLAGS:
        _require_equal(flags.get(flag), True, f"flags.{flag}")
    for flag in DEMO_FALSE_FLAGS:
        _require_equal(flags.get(flag), False, f"flags.{flag}")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceMetadataSampleDemoResultError(f"{name} must be an object")
    return value


def _require_non_empty_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise OpenSSLModelSequenceMetadataSampleDemoResultError(
            f"{name} must be a non-empty list"
        )
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceMetadataSampleDemoResultError(
            f"{name} must be {expected!r}"
        )

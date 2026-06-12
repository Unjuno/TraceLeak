"""Classify toy/local vs actual trace-derived model-sequence samples."""

from __future__ import annotations

from typing import Any


class ModelSequenceBoundaryError(ValueError):
    """Raised when model-sequence sample boundary metadata is unsafe or inconsistent."""


BOUNDARY_KEYS = (
    "validation_scope",
    "actual_trace_derived",
    "trace_collection_mode",
    "raw_secret_captured",
    "target_version",
    "source_pin",
    "build_id",
    "public_safe",
)


def model_sequence_sample_boundary(data: dict[str, Any]) -> dict[str, Any]:
    """Return normalized toy/local vs actual trace-derived boundary metadata.

    Missing boundary metadata is interpreted conservatively as toy/local validation,
    not as evidence from an actual target execution.
    """

    actual_trace_derived = _optional_bool(data, "actual_trace_derived", default=False)
    raw_secret_captured = _optional_bool(data, "raw_secret_captured", default=False)
    public_safe = _optional_bool(data, "public_safe", default=not raw_secret_captured)
    trace_collection_mode = str(
        data.get("trace_collection_mode")
        or ("redacted" if actual_trace_derived else "not_applicable")
    )
    validation_scope = str(
        data.get("validation_scope")
        or ("actual_trace_derived" if actual_trace_derived else "toy_local_validation")
    )
    return {
        "validation_scope": validation_scope,
        "actual_trace_derived": actual_trace_derived,
        "trace_collection_mode": trace_collection_mode,
        "raw_secret_captured": raw_secret_captured,
        "target_version": str(data.get("target_version", "unknown")),
        "source_pin": str(data.get("source_pin", data.get("source_commit", "unknown"))),
        "build_id": str(data.get("build_id", "unknown")),
        "public_safe": public_safe,
    }


def validate_model_sequence_sample_boundary(data: dict[str, Any]) -> dict[str, Any]:
    """Validate boundary metadata before treating a sample as actual trace-derived."""

    boundary = model_sequence_sample_boundary(data)
    if boundary["raw_secret_captured"]:
        raise ModelSequenceBoundaryError("model-sequence samples must not capture raw secrets")
    if not boundary["public_safe"]:
        raise ModelSequenceBoundaryError("model-sequence samples must be public-safe")
    if not boundary["actual_trace_derived"]:
        return boundary

    if boundary["validation_scope"] != "actual_trace_derived":
        raise ModelSequenceBoundaryError(
            "actual trace-derived samples must use validation_scope=actual_trace_derived"
        )
    if boundary["trace_collection_mode"] != "redacted":
        raise ModelSequenceBoundaryError(
            "actual trace-derived samples must use trace_collection_mode=redacted"
        )
    for key in ("target_version", "source_pin", "build_id"):
        if boundary[key] in {"", "unknown", "not_applicable"}:
            raise ModelSequenceBoundaryError(
                f"actual trace-derived samples must declare non-empty {key}"
            )
    return boundary


def attach_model_sequence_boundary(
    result: dict[str, Any], data: dict[str, Any]
) -> dict[str, Any]:
    """Attach normalized boundary metadata to a result dictionary in-place."""

    boundary = validate_model_sequence_sample_boundary(data)
    for key in BOUNDARY_KEYS:
        result[key] = boundary[key]
    return result


def _optional_bool(data: dict[str, Any], key: str, *, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ModelSequenceBoundaryError(f"{key} must be a boolean")
    return value

"""Model output contract schema v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MODEL_OUTPUT_FORMAT = "traceleak.model_output.v1"

ALLOWED_OUTPUT_CONSUMERS: tuple[str, ...] = (
    "sequence",
    "graph",
    "hybrid",
)

REQUIRED_MODEL_OUTPUT_FIELDS: tuple[str, ...] = (
    "sample_id",
    "model_id",
    "consumer_mode",
    "prediction",
    "confidence",
    "metadata",
)


class ModelOutputContractError(ValueError):
    """Raised when a model output contract is invalid."""


@dataclass(frozen=True)
class ModelOutputRecord:
    """Schema-level model output record."""

    sample_id: str
    model_id: str
    consumer_mode: str
    prediction: dict[str, Any]
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "sample_id": self.sample_id,
            "format": MODEL_OUTPUT_FORMAT,
            "model_id": self.model_id,
            "consumer_mode": self.consumer_mode,
            "prediction": dict(self.prediction),
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


def model_output_record(
    *,
    sample_id: str,
    model_id: str,
    consumer_mode: str,
    prediction: dict[str, Any],
    confidence: float,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one model output record."""

    record = {
        "sample_id": sample_id,
        "format": MODEL_OUTPUT_FORMAT,
        "model_id": model_id,
        "consumer_mode": consumer_mode,
        "prediction": dict(prediction),
        "confidence": float(confidence),
        "metadata": {
            "schema_kind": "model_output",
            "claim_scope": "model_output_only",
            **(metadata or {}),
        },
    }
    validate_model_output_record(record)
    return record


def validate_model_output_record(record: dict[str, Any]) -> None:
    """Validate one model output record."""

    if not isinstance(record, dict):
        raise ModelOutputContractError("model output record must be an object")
    for field_name in REQUIRED_MODEL_OUTPUT_FIELDS:
        if field_name not in record:
            raise ModelOutputContractError(f"missing required model output field: {field_name}")
    if record.get("format") != MODEL_OUTPUT_FORMAT:
        raise ModelOutputContractError("invalid model output format")
    if record["consumer_mode"] not in ALLOWED_OUTPUT_CONSUMERS:
        raise ModelOutputContractError("invalid consumer_mode")
    if not isinstance(record["prediction"], dict):
        raise ModelOutputContractError("prediction must be an object")
    confidence = record["confidence"]
    if not isinstance(confidence, int | float) or not 0.0 <= confidence <= 1.0:
        raise ModelOutputContractError("confidence must be between 0.0 and 1.0")
    if not isinstance(record["metadata"], dict):
        raise ModelOutputContractError("metadata must be an object")

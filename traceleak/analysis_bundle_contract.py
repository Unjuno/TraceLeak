"""Analysis bundle contract schema v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ANALYSIS_BUNDLE_FORMAT = "traceleak.analysis_bundle.v1"

REQUIRED_ANALYSIS_BUNDLE_FIELDS: tuple[str, ...] = (
    "bundle_id",
    "sample_id",
    "model_output_id",
    "attribution_ids",
    "view_contract_ids",
    "metadata",
)


class AnalysisBundleContractError(ValueError):
    """Raised when an analysis bundle contract is invalid."""


@dataclass(frozen=True)
class AnalysisBundleRecord:
    """Schema-level analysis bundle record."""

    bundle_id: str
    sample_id: str
    model_output_id: str
    attribution_ids: list[str]
    view_contract_ids: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "bundle_id": self.bundle_id,
            "format": ANALYSIS_BUNDLE_FORMAT,
            "sample_id": self.sample_id,
            "model_output_id": self.model_output_id,
            "attribution_ids": list(self.attribution_ids),
            "view_contract_ids": list(self.view_contract_ids),
            "metadata": dict(self.metadata),
        }


def analysis_bundle_record(
    *,
    bundle_id: str,
    sample_id: str,
    model_output_id: str,
    attribution_ids: list[str],
    view_contract_ids: list[str],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one analysis bundle record."""

    record = {
        "bundle_id": bundle_id,
        "format": ANALYSIS_BUNDLE_FORMAT,
        "sample_id": sample_id,
        "model_output_id": model_output_id,
        "attribution_ids": list(attribution_ids),
        "view_contract_ids": list(view_contract_ids),
        "metadata": {
            "schema_kind": "analysis_bundle",
            "claim_scope": "schema_only",
            **(metadata or {}),
        },
    }
    validate_analysis_bundle_record(record)
    return record


def validate_analysis_bundle_record(record: dict[str, Any]) -> None:
    """Validate one analysis bundle record."""

    if not isinstance(record, dict):
        raise AnalysisBundleContractError("analysis bundle record must be an object")
    for field_name in REQUIRED_ANALYSIS_BUNDLE_FIELDS:
        if field_name not in record:
            raise AnalysisBundleContractError(f"missing required analysis bundle field: {field_name}")
    if record.get("format") != ANALYSIS_BUNDLE_FORMAT:
        raise AnalysisBundleContractError("invalid analysis bundle format")
    for field_name in ("bundle_id", "sample_id", "model_output_id"):
        if not isinstance(record[field_name], str) or not record[field_name]:
            raise AnalysisBundleContractError(f"{field_name} must be a non-empty string")
    for field_name in ("attribution_ids", "view_contract_ids"):
        value = record[field_name]
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise AnalysisBundleContractError(f"{field_name} must contain only non-empty strings")
    if not isinstance(record["metadata"], dict):
        raise AnalysisBundleContractError("metadata must be an object")

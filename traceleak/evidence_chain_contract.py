"""Evidence chain contract schema v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

EVIDENCE_CHAIN_FORMAT = "traceleak.evidence_chain.v1"

REQUIRED_EVIDENCE_CHAIN_FIELDS: tuple[str, ...] = (
    "chain_id",
    "sample_id",
    "model_output_id",
    "attribution_ids",
    "view_contract_ids",
    "metadata",
)


class EvidenceChainContractError(ValueError):
    """Raised when an evidence chain contract is invalid."""


@dataclass(frozen=True)
class EvidenceChainRecord:
    """Schema-level evidence chain record."""

    chain_id: str
    sample_id: str
    model_output_id: str
    attribution_ids: list[str]
    view_contract_ids: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "chain_id": self.chain_id,
            "format": EVIDENCE_CHAIN_FORMAT,
            "sample_id": self.sample_id,
            "model_output_id": self.model_output_id,
            "attribution_ids": list(self.attribution_ids),
            "view_contract_ids": list(self.view_contract_ids),
            "metadata": dict(self.metadata),
        }


def evidence_chain_record(
    *,
    chain_id: str,
    sample_id: str,
    model_output_id: str,
    attribution_ids: list[str],
    view_contract_ids: list[str],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one evidence chain record."""

    record = {
        "chain_id": chain_id,
        "format": EVIDENCE_CHAIN_FORMAT,
        "sample_id": sample_id,
        "model_output_id": model_output_id,
        "attribution_ids": list(attribution_ids),
        "view_contract_ids": list(view_contract_ids),
        "metadata": {
            "schema_kind": "evidence_chain",
            "claim_scope": "schema_only",
            **(metadata or {}),
        },
    }
    validate_evidence_chain_record(record)
    return record


def validate_evidence_chain_record(record: dict[str, Any]) -> None:
    """Validate one evidence chain record."""

    if not isinstance(record, dict):
        raise EvidenceChainContractError("evidence chain record must be an object")
    for field_name in REQUIRED_EVIDENCE_CHAIN_FIELDS:
        if field_name not in record:
            raise EvidenceChainContractError(f"missing required evidence chain field: {field_name}")
    if record.get("format") != EVIDENCE_CHAIN_FORMAT:
        raise EvidenceChainContractError("invalid evidence chain format")
    for field_name in ("chain_id", "sample_id", "model_output_id"):
        if not isinstance(record[field_name], str) or not record[field_name]:
            raise EvidenceChainContractError(f"{field_name} must be a non-empty string")
    for field_name in ("attribution_ids", "view_contract_ids"):
        value = record[field_name]
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise EvidenceChainContractError(f"{field_name} must contain only non-empty strings")
    if not isinstance(record["metadata"], dict):
        raise EvidenceChainContractError("metadata must be an object")

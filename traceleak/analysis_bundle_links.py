"""Helpers that link analysis records into analysis bundles."""

from __future__ import annotations

from typing import Any

from traceleak.analysis_bundle_contract import analysis_bundle_record
from traceleak.attribution_export_schema import validate_attribution_export_records
from traceleak.model_output_contract import validate_model_output_record
from traceleak.view_contract import validate_view_contracts


class AnalysisBundleLinkError(ValueError):
    """Raised when records cannot be linked into one analysis bundle."""


def analysis_bundle_from_records(
    *,
    bundle_id: str,
    model_output: dict[str, Any],
    attribution_records: list[dict[str, Any]],
    view_contracts: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an analysis bundle from validated model, attribution, and view records."""

    validate_model_output_record(model_output)
    validate_attribution_export_records(attribution_records)
    validate_view_contracts(view_contracts)

    sample_id = str(model_output["sample_id"])
    _require_same_sample_id(sample_id, attribution_records, "attribution_records")
    _require_same_sample_id(sample_id, view_contracts, "view_contracts")

    model_output_id = _model_output_id(model_output)
    attribution_ids = [_attribution_id(record) for record in attribution_records]
    view_contract_ids = [str(record["contract_id"]) for record in view_contracts]

    return analysis_bundle_record(
        bundle_id=bundle_id,
        sample_id=sample_id,
        model_output_id=model_output_id,
        attribution_ids=attribution_ids,
        view_contract_ids=view_contract_ids,
        metadata={
            "schema_kind": "analysis_bundle_link",
            "linked_record_count": 1 + len(attribution_records) + len(view_contracts),
            **(metadata or {}),
        },
    )


def _require_same_sample_id(sample_id: str, records: list[dict[str, Any]], label: str) -> None:
    for index, record in enumerate(records):
        if str(record.get("sample_id")) != sample_id:
            raise AnalysisBundleLinkError(f"{label}[{index}] sample_id does not match model output sample_id")


def _model_output_id(model_output: dict[str, Any]) -> str:
    metadata = model_output.get("metadata", {})
    if isinstance(metadata, dict) and isinstance(metadata.get("output_id"), str) and metadata["output_id"]:
        return metadata["output_id"]
    return f"{model_output['model_id']}:{model_output['consumer_mode']}"


def _attribution_id(record: dict[str, Any]) -> str:
    return ":".join(
        [
            str(record["model_id"]),
            str(record["method"]),
            str(record["rank"]),
            str(record["entity_id"]),
        ]
    )

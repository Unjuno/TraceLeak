"""Attention and attribution export schema v1."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from traceleak.program_event_schema import FORBIDDEN_PUBLIC_FIELD_KEYS

ATTRIBUTION_EXPORT_FORMAT = "traceleak.attention_attribution_export.v1"

ALLOWED_ATTRIBUTION_LEVELS: set[str] = {"token", "event", "variable", "graph_node", "graph_edge"}
ALLOWED_MODEL_FAMILIES: set[str] = {"transformer", "gnn", "hybrid", "mlp", "sparse_softmax", "sequence_model", "unknown"}
ALLOWED_METHODS: set[str] = {"attention_weight", "ablation_drop", "gradient", "integrated_gradients", "feature_weight", "mlp_bridge", "sparse_softmax_weight_separation", "manual_annotation"}
ALLOWED_SCORE_SEMANTICS: set[str] = {"attention_pattern", "local_ablation_effect", "gradient_sensitivity", "model_weight_proxy", "manual_evidence_score"}
METHOD_SCORE_SEMANTICS: dict[str, str] = {
    "attention_weight": "attention_pattern",
    "ablation_drop": "local_ablation_effect",
    "gradient": "gradient_sensitivity",
    "integrated_gradients": "gradient_sensitivity",
    "feature_weight": "model_weight_proxy",
    "mlp_bridge": "model_weight_proxy",
    "sparse_softmax_weight_separation": "model_weight_proxy",
    "manual_annotation": "manual_evidence_score",
}

REQUIRED_ATTRIBUTION_EXPORT_FIELDS: tuple[str, ...] = (
    "sample_id", "model_id", "model_family", "attribution_level", "entity_id",
    "entity_type", "score", "score_semantics", "rank", "method", "evidence", "metadata",
)


class AttributionExportSchemaError(ValueError):
    """Raised when an export record is invalid."""


@dataclass(frozen=True)
class AttributionExportRecord:
    """Normalized attention or attribution export record."""

    sample_id: str
    model_id: str
    model_family: str
    attribution_level: str
    entity_id: str
    entity_type: str
    score: float
    score_semantics: str
    rank: int
    method: str
    evidence: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "model_id": self.model_id,
            "model_family": self.model_family,
            "attribution_level": self.attribution_level,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "score": self.score,
            "score_semantics": self.score_semantics,
            "rank": self.rank,
            "method": self.method,
            "evidence": dict(self.evidence),
            "metadata": dict(self.metadata),
        }


def attribution_export_record_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> AttributionExportRecord:
    validate_attribution_export_record(data, public_safe=public_safe)
    return AttributionExportRecord(
        sample_id=data["sample_id"], model_id=data["model_id"], model_family=data["model_family"],
        attribution_level=data["attribution_level"], entity_id=data["entity_id"], entity_type=data["entity_type"],
        score=float(data["score"]), score_semantics=data["score_semantics"], rank=data["rank"], method=data["method"],
        evidence=dict(data["evidence"]), metadata=dict(data["metadata"]),
    )


def validate_attribution_export_record(record: dict[str, Any], *, public_safe: bool = True) -> None:
    if not isinstance(record, dict):
        raise AttributionExportSchemaError("attribution export record must be an object")
    for field_name in REQUIRED_ATTRIBUTION_EXPORT_FIELDS:
        if field_name not in record:
            raise AttributionExportSchemaError(f"missing required attribution export field: {field_name}")
    _require_non_empty_string(record["sample_id"], "sample_id")
    _require_non_empty_string(record["model_id"], "model_id")
    _validate_enum(record["model_family"], "model_family", ALLOWED_MODEL_FAMILIES)
    level = _validate_enum(record["attribution_level"], "attribution_level", ALLOWED_ATTRIBUTION_LEVELS)
    _require_non_empty_string(record["entity_id"], "entity_id")
    entity_type = _require_non_empty_string(record["entity_type"], "entity_type")
    if entity_type != level:
        raise AttributionExportSchemaError("entity_type must match attribution_level")
    if not isinstance(record["score"], int | float) or not math.isfinite(float(record["score"])):
        raise AttributionExportSchemaError("score must be a finite number")
    score_semantics = _validate_enum(record["score_semantics"], "score_semantics", ALLOWED_SCORE_SEMANTICS)
    if not isinstance(record["rank"], int) or record["rank"] <= 0:
        raise AttributionExportSchemaError("rank must be a positive integer")
    method = _validate_enum(record["method"], "method", ALLOWED_METHODS)
    expected_semantics = METHOD_SCORE_SEMANTICS[method]
    if score_semantics != expected_semantics:
        raise AttributionExportSchemaError(f"method={method} requires score_semantics={expected_semantics}")
    _validate_evidence(_require_object(record["evidence"], "evidence"))
    _require_object(record["metadata"], "metadata")
    if public_safe:
        _reject_forbidden_public_fields(record, "record")


def validate_attribution_export_records(records: list[dict[str, Any]], *, public_safe: bool = True) -> None:
    if not isinstance(records, list) or not records:
        raise AttributionExportSchemaError("attribution export records must be a non-empty list")
    seen_keys: set[tuple[str, str, str, int, str]] = set()
    for index, record in enumerate(records):
        try:
            validate_attribution_export_record(record, public_safe=public_safe)
        except AttributionExportSchemaError as exc:
            raise AttributionExportSchemaError(f"records[{index}]: {exc}") from exc
        key = (str(record["sample_id"]), str(record["model_id"]), str(record["entity_id"]), int(record["rank"]), str(record["method"]))
        if key in seen_keys:
            raise AttributionExportSchemaError("duplicate attribution export record key")
        seen_keys.add(key)


def sort_attribution_export_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_attribution_export_records(records)
    return sorted(records, key=lambda record: (str(record["sample_id"]), str(record["model_id"]), str(record["attribution_level"]), int(record["rank"]), str(record["entity_id"])))


def attribution_export_record(*, sample_id: str, model_id: str, model_family: str, attribution_level: str, entity_id: str, score: float, rank: int, method: str, evidence_summary: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    _require_non_empty_string(evidence_summary, "evidence_summary")
    record = {
        "sample_id": sample_id,
        "model_id": model_id,
        "model_family": model_family,
        "attribution_level": attribution_level,
        "entity_id": entity_id,
        "entity_type": attribution_level,
        "score": float(score),
        "score_semantics": METHOD_SCORE_SEMANTICS.get(method, "manual_evidence_score"),
        "rank": rank,
        "method": method,
        "evidence": {"summary": evidence_summary, "claim_scope": _claim_scope_for_method(method)},
        "metadata": dict(metadata or {}),
    }
    validate_attribution_export_record(record)
    return record


def _claim_scope_for_method(method: str) -> str:
    if method == "attention_weight":
        return "attention_pattern_only"
    if method in {"ablation_drop", "gradient", "integrated_gradients"}:
        return "local_model_explanation"
    return "model_explanation_proxy"


def _validate_evidence(evidence: dict[str, Any]) -> None:
    if "summary" not in evidence:
        raise AttributionExportSchemaError("evidence.summary is required")
    _require_non_empty_string(evidence["summary"], "evidence.summary")
    if "claim_scope" not in evidence:
        raise AttributionExportSchemaError("evidence.claim_scope is required")
    _require_non_empty_string(evidence["claim_scope"], "evidence.claim_scope")


def _validate_enum(value: Any, name: str, allowed: set[str]) -> str:
    text = _require_non_empty_string(value, name)
    if text not in allowed:
        raise AttributionExportSchemaError(_allowed_error(name, text, allowed))
    return text


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AttributionExportSchemaError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise AttributionExportSchemaError(f"{name} must be a non-empty string")
    return value


def _reject_forbidden_public_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PUBLIC_FIELD_KEYS:
                raise AttributionExportSchemaError(f"public-safe attribution export must not contain raw field: {path}.{key_text}")
            _reject_forbidden_public_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_public_fields(child, f"{path}[{index}]")


def _allowed_error(name: str, value: str, allowed: set[str]) -> str:
    return f"invalid {name}: {value!r}; allowed: {', '.join(sorted(allowed))}"

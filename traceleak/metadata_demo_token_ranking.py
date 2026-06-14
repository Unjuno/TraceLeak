"""Metadata demo token ranking helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

METADATA_DEMO_TOKEN_RANKING_FORMAT = "traceleak.metadata_demo_token_ranking.v1"


class MetadataDemoTokenRankingError(ValueError):
    """Raised when a metadata demo token ranking is invalid."""


def build_metadata_demo_token_ranking(
    *,
    demo_manifest: dict[str, Any],
    nn_result: dict[str, Any],
    target_selection: str = "constant_time_helper_misuse_path",
) -> dict[str, Any]:
    """Build a public-safe metadata-demo token ranking."""

    rows = []
    for rank, item in enumerate(nn_result.get("attributions", []), start=1):
        rows.append(
            {
                "rank": rank,
                "group_id": item["group_id"],
                "group_type": item.get("group_type", "model_sequence_token"),
                "score": item["score"],
                "evidence": item.get("evidence", []),
                "confidence": "metadata_demo_only",
            }
        )
    ranking = {
        "format": METADATA_DEMO_TOKEN_RANKING_FORMAT,
        "status": "metadata_demo_token_ranking_ready",
        "phase": "P30",
        "target": "metadata_demo_token_ranking",
        "mode": "metadata_only_ranking",
        "target_selection": target_selection,
        "sample_id": demo_manifest["sample_id"],
        "sample_digest": demo_manifest["sample_digest"],
        "source_pin_digest": demo_manifest["source_pin_digest"],
        "trace_contract_digest": demo_manifest["trace_contract_digest"],
        "ranked_token_count": len(rows),
        "ranked_tokens": rows,
        "public_status": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "real_world_claim": False,
            "external_report_material": False,
        },
        "notes": [
            "This ranks tokens from the metadata-only public demo path.",
            "It is not evidence about a real deployed system.",
            "Later reviewed evidence is required before making any external claim.",
        ],
    }
    validate_metadata_demo_token_ranking(ranking)
    return ranking


def validate_metadata_demo_token_ranking(ranking: dict[str, Any]) -> None:
    """Validate a public-safe metadata-demo token ranking."""

    _eq(ranking.get("format"), METADATA_DEMO_TOKEN_RANKING_FORMAT, "format")
    _eq(ranking.get("status"), "metadata_demo_token_ranking_ready", "status")
    _eq(ranking.get("phase"), "P30", "phase")
    _eq(ranking.get("target"), "metadata_demo_token_ranking", "target")
    _eq(ranking.get("mode"), "metadata_only_ranking", "mode")
    for field in ["target_selection", "sample_id", "sample_digest", "source_pin_digest", "trace_contract_digest"]:
        _non_empty(ranking.get(field), field)
    rows = ranking.get("ranked_tokens")
    if not isinstance(rows, list):
        raise MetadataDemoTokenRankingError("ranked_tokens must be a list")
    _eq(ranking.get("ranked_token_count"), len(rows), "ranked_token_count")
    for index, item in enumerate(rows):
        if not isinstance(item, dict):
            raise MetadataDemoTokenRankingError(f"ranked_tokens[{index}] must be an object")
        _non_empty(item.get("group_id"), f"ranked_tokens[{index}].group_id")
        if not isinstance(item.get("score"), int | float):
            raise MetadataDemoTokenRankingError(f"ranked_tokens[{index}].score must be numeric")
    status = ranking.get("public_status")
    if not isinstance(status, dict):
        raise MetadataDemoTokenRankingError("public_status must be an object")
    for flag in ["metadata_only", "payload_free", "public_safe"]:
        _eq(status.get(flag), True, f"public_status.{flag}")
    for flag in ["real_world_claim", "external_report_material"]:
        _eq(status.get(flag), False, f"public_status.{flag}")


def write_metadata_demo_token_ranking(path: Path, ranking: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ranking, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise MetadataDemoTokenRankingError(f"{name} must be a non-empty string")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise MetadataDemoTokenRankingError(f"{name} must be {expected!r}")

"""Claim level validation for TraceLeak reports.

Claim levels describe how strong a TraceLeak statement is allowed to be. They do
not prove cryptographic security; they constrain report language by requiring the
right public-safe evidence for each level.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.schema import PUBLIC_SAFE_VIEWS, SECRET_EQUIVALENT_KEYS

CLAIM_LEVELS: tuple[str, ...] = ("L0", "L1", "L2", "L3", "L4", "L5")

LEVEL_DESCRIPTIONS: dict[str, str] = {
    "L0": "Tooling sanity check only.",
    "L1": "Synthetic known-signal localization.",
    "L2": "Toy target localization with public-safe derived data.",
    "L3": "Local implementation observation with public-safe report data.",
    "L4": "Cross-run or cross-build stability evidence.",
    "L5": "Patch verification with repeated-run stability evidence.",
}


class ClaimLevelError(ValueError):
    """Raised when a claim level file is invalid."""


def load_claim(path: str | Path) -> dict[str, Any]:
    """Load a TraceLeak claim JSON file."""

    claim_path = Path(path)
    if not claim_path.exists():
        raise ClaimLevelError(f"claim file not found: {claim_path}")
    try:
        return json.loads(claim_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClaimLevelError(f"invalid JSON in {claim_path}: {exc}") from exc


def validate_claim(claim: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a TraceLeak claim dictionary."""

    for key in ("claim_id", "level", "target", "view", "metric", "evidence", "safety"):
        if key not in claim:
            raise ClaimLevelError(f"missing required claim field: {key}")

    _require_non_empty_string(claim["claim_id"], "claim_id")
    _require_non_empty_string(claim["target"], "target")
    _require_non_empty_string(claim["metric"], "metric")

    level = claim["level"]
    if level not in CLAIM_LEVELS:
        allowed = ", ".join(CLAIM_LEVELS)
        raise ClaimLevelError(f"invalid claim level: {level!r}; allowed: {allowed}")

    view = claim["view"]
    _require_non_empty_string(view, "view")
    if public_safe and view not in PUBLIC_SAFE_VIEWS:
        raise ClaimLevelError(f"view {view!r} is not allowed in public-safe claims")

    evidence = claim["evidence"]
    if not isinstance(evidence, dict):
        raise ClaimLevelError("evidence must be an object")

    _validate_safety(claim["safety"], public_safe=public_safe)
    _validate_level_requirements(level, evidence)
    _reject_secret_equivalent_fields(claim)


def claim_summary(claim: dict[str, Any]) -> dict[str, Any]:
    """Return a compact summary for a validated claim."""

    evidence = claim["evidence"]
    return {
        "claim_id": claim["claim_id"],
        "level": claim["level"],
        "target": claim["target"],
        "view": claim["view"],
        "metric": claim["metric"],
        "description": LEVEL_DESCRIPTIONS[claim["level"]],
        "has_patch_verification": "patch_verification" in evidence,
        "has_stability": "stability" in evidence,
    }


def claim_report_dict(claim: dict[str, Any], *, public_safe: bool = True) -> dict[str, Any]:
    """Return a normalized claim report dictionary."""

    validate_claim(claim, public_safe=public_safe)
    summary = claim_summary(claim)
    return {
        "report_type": "claim_level",
        "claim_id": summary["claim_id"],
        "level": summary["level"],
        "description": summary["description"],
        "target": summary["target"],
        "view": summary["view"],
        "metric": summary["metric"],
        "evidence": claim["evidence"],
        "safety": claim["safety"],
        "notes": claim.get("notes", []),
    }


def _validate_level_requirements(level: str, evidence: dict[str, Any]) -> None:
    if level == "L0":
        return
    if level == "L1":
        _require_evidence(evidence, "attribution_report", level)
        return
    if level == "L2":
        _require_evidence(evidence, "toy_or_synthetic_target", level)
        _require_evidence(evidence, "attribution_report", level)
        return
    if level == "L3":
        _require_evidence(evidence, "implementation_observation", level)
        _require_evidence(evidence, "attribution_report", level)
        return
    if level == "L4":
        _require_reduced_or_stable_stability(evidence, level)
        return
    if level == "L5":
        _require_reduced_patch_verification(evidence, level)
        _require_reduced_or_stable_stability(evidence, level)
        return
    raise ClaimLevelError(f"unsupported claim level: {level}")


def _require_evidence(evidence: dict[str, Any], key: str, level: str) -> Any:
    if key not in evidence:
        raise ClaimLevelError(f"claim level {level} requires evidence.{key}")
    return evidence[key]


def _require_reduced_patch_verification(evidence: dict[str, Any], level: str) -> None:
    patch = _require_evidence(evidence, "patch_verification", level)
    if not isinstance(patch, dict):
        raise ClaimLevelError("evidence.patch_verification must be an object")
    _require_non_empty_string(patch.get("verification_id"), "evidence.patch_verification.verification_id")
    if patch.get("status") != "reduced":
        raise ClaimLevelError("L5 requires evidence.patch_verification.status == 'reduced'")


def _require_reduced_or_stable_stability(evidence: dict[str, Any], level: str) -> None:
    stability = _require_evidence(evidence, "stability", level)
    if not isinstance(stability, dict):
        raise ClaimLevelError("evidence.stability must be an object")
    _require_non_empty_string(stability.get("stability_id"), "evidence.stability.stability_id")
    status = stability.get("status")
    if status not in {"reduced", "unchanged"}:
        raise ClaimLevelError("L4/L5 requires evidence.stability.status to be 'reduced' or 'unchanged'")
    if level == "L5" and status != "reduced":
        raise ClaimLevelError("L5 requires evidence.stability.status == 'reduced'")


def _validate_safety(safety: Any, *, public_safe: bool) -> None:
    if not isinstance(safety, dict):
        raise ClaimLevelError("safety must be an object")
    if public_safe:
        if safety.get("public_safe") is not True:
            raise ClaimLevelError("public claims require safety.public_safe == true")
        if safety.get("contains_raw_trace") is True:
            raise ClaimLevelError("public claims must not contain raw traces")
        if safety.get("contains_secret_equivalent") is True:
            raise ClaimLevelError("public claims must not contain secret-equivalent data")


def _require_non_empty_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ClaimLevelError(f"{name} must be a non-empty string")


def _reject_secret_equivalent_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SECRET_EQUIVALENT_KEYS:
                raise ClaimLevelError(f"secret-equivalent field is not allowed: {key}")
            _reject_secret_equivalent_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_equivalent_fields(child)

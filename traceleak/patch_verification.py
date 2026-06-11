"""Patch verification result validation for TraceLeak.

Patch verification compares before/after measurements and records whether a
source-level change reduced the measured signal. It is report metadata, not raw
trace data.
"""

from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
from typing import Any

from traceleak.schema import PUBLIC_SAFE_VIEWS, SECRET_EQUIVALENT_KEYS

ALLOWED_PATCH_STATUSES: set[str] = {
    "reduced",
    "unchanged",
    "increased",
    "inconclusive",
}


class PatchVerificationError(ValueError):
    """Raised when a patch verification result is invalid."""


def load_patch_verification(path: str | Path) -> dict[str, Any]:
    """Load a patch verification JSON file."""

    verification_path = Path(path)
    if not verification_path.exists():
        raise PatchVerificationError(f"patch verification file not found: {verification_path}")
    try:
        return json.loads(verification_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchVerificationError(f"invalid JSON in {verification_path}: {exc}") from exc


def verification_delta(before_score: float, after_score: float) -> float:
    """Return before-after score reduction.

    Positive values mean the measured score decreased after the patch.
    """

    _require_number(before_score, "before_score")
    _require_number(after_score, "after_score")
    return before_score - after_score


def classify_delta(delta: float, *, tolerance: float = 1e-9) -> str:
    """Classify a before-after delta."""

    _require_number(delta, "delta")
    _require_number(tolerance, "tolerance")
    if tolerance < 0:
        raise PatchVerificationError("tolerance must be non-negative")
    if delta > tolerance:
        return "reduced"
    if delta < -tolerance:
        return "increased"
    return "unchanged"


def validate_patch_verification(result: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a patch verification result dictionary."""

    for key in ("verification_id", "target", "view", "metric", "before", "after", "status"):
        if key not in result:
            raise PatchVerificationError(f"missing required patch verification field: {key}")

    _require_non_empty_string(result["verification_id"], "verification_id")
    _require_non_empty_string(result["target"], "target")
    _require_non_empty_string(result["metric"], "metric")

    view = result["view"]
    _require_non_empty_string(view, "view")
    if public_safe and view not in PUBLIC_SAFE_VIEWS:
        raise PatchVerificationError(f"view {view!r} is not allowed in public-safe verification")

    if result["status"] not in ALLOWED_PATCH_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_PATCH_STATUSES))
        raise PatchVerificationError(f"invalid status: {result['status']!r}; allowed: {allowed}")

    _validate_measurement(result["before"], "before")
    _validate_measurement(result["after"], "after")

    computed_delta = verification_delta(result["before"]["score"], result["after"]["score"])
    if "delta" in result:
        _require_number(result["delta"], "delta")
        if abs(float(result["delta"]) - computed_delta) > 1e-9:
            raise PatchVerificationError("delta does not match before.score - after.score")

    _reject_secret_equivalent_fields(result)


def patch_verification_summary(result: dict[str, Any]) -> dict[str, Any]:
    """Return a compact summary for a validated patch verification result."""

    delta = verification_delta(result["before"]["score"], result["after"]["score"])
    return {
        "verification_id": result["verification_id"],
        "target": result["target"],
        "view": result["view"],
        "metric": result["metric"],
        "before_score": result["before"]["score"],
        "after_score": result["after"]["score"],
        "delta": delta,
        "status": result["status"],
    }


def _validate_measurement(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        raise PatchVerificationError(f"{name} must be an object")
    _require_non_empty_string(value.get("run_id"), f"{name}.run_id")
    _require_number(value.get("score"), f"{name}.score")
    if "report" in value:
        _require_non_empty_string(value["report"], f"{name}.report")


def _require_non_empty_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise PatchVerificationError(f"{name} must be a non-empty string")


def _require_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or not isfinite(value):
        raise PatchVerificationError(f"{name} must be a finite number")


def _reject_secret_equivalent_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SECRET_EQUIVALENT_KEYS:
                raise PatchVerificationError(f"secret-equivalent field is not allowed: {key}")
            _reject_secret_equivalent_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_equivalent_fields(child)

"""OpenSSL experiment preflight validation and reporting.

This module intentionally does not run OpenSSL. It validates the experiment plan
that must be satisfied before any real OpenSSL trace collection begins.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OPENSSL_PREFLIGHT_FORMAT = "traceleak.openssl_preflight.v1"
REQUIRED_DISALLOWED_FIELDS = {
    "p",
    "q",
    "d",
    "private_key",
    "raw_bignum",
    "prime_candidate",
    "seed",
    "rng_state",
}
REQUIRED_CONTROLS = {
    "shuffled_label_negative_control",
    "public_only_baseline",
}
REQUIRED_GATES = {
    "source_ref_pinned",
    "redacted_view_only",
    "no_raw_secret_fields",
    "lab_only_labels_only",
    "negative_controls_planned",
    "baseline_comparison_planned",
    "attribution_review_planned",
}


class OpenSSLPreflightError(ValueError):
    """Raised when an OpenSSL preflight manifest is invalid."""


def load_openssl_preflight(path: str | Path) -> dict[str, Any]:
    """Load and validate an OpenSSL preflight manifest."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        raise OpenSSLPreflightError(f"preflight manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLPreflightError(f"invalid JSON in {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise OpenSSLPreflightError("preflight manifest must be a JSON object")
    validate_openssl_preflight(manifest)
    return manifest


def validate_openssl_preflight(manifest: dict[str, Any]) -> None:
    """Validate the OpenSSL preflight manifest contract."""

    _require_equal(manifest.get("format"), OPENSSL_PREFLIGHT_FORMAT, "format")
    _require_string(manifest.get("experiment_id"), "experiment_id")
    _require_equal(manifest.get("mode"), "preflight_only", "mode")
    _require_equal(manifest.get("public_safe"), True, "public_safe")
    _require_equal(manifest.get("execution_allowed"), False, "execution_allowed")

    target_family = _require_string(manifest.get("target_family"), "target_family")
    if "openssl" not in target_family.lower():
        raise OpenSSLPreflightError("target_family must identify an OpenSSL target")

    _validate_source(_require_object(manifest.get("source"), "source"))
    _validate_instrumentation(_require_object(manifest.get("instrumentation"), "instrumentation"))
    _validate_labels(_require_object(manifest.get("labels"), "labels"))
    _validate_string_list(manifest.get("planned_artifacts"), "planned_artifacts", min_items=1)

    controls = set(_validate_string_list(manifest.get("required_controls"), "required_controls", min_items=1))
    missing_controls = sorted(REQUIRED_CONTROLS - controls)
    if missing_controls:
        raise OpenSSLPreflightError(f"required_controls missing: {', '.join(missing_controls)}")

    stages = _require_list(manifest.get("pipeline_stages"), "pipeline_stages", min_items=1)
    for index, stage in enumerate(stages):
        _validate_pipeline_stage(stage, index=index)

    gates = set(_validate_string_list(manifest.get("gates"), "gates", min_items=len(REQUIRED_GATES)))
    missing_gates = sorted(REQUIRED_GATES - gates)
    if missing_gates:
        raise OpenSSLPreflightError(f"gates missing: {', '.join(missing_gates)}")


def openssl_preflight_report_dict(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized preflight report dictionary."""

    validate_openssl_preflight(manifest)
    instrumentation = manifest["instrumentation"]
    labels = manifest["labels"]
    return {
        "report_type": "openssl_preflight_report",
        "status": "preflight_ready",
        "experiment_id": manifest["experiment_id"],
        "target_family": manifest["target_family"],
        "mode": manifest["mode"],
        "execution_allowed": manifest["execution_allowed"],
        "public_safe": manifest["public_safe"],
        "trace_view": instrumentation["trace_view"],
        "raw_secret_capture_allowed": instrumentation["raw_secret_capture_allowed"],
        "lab_only_labels": labels["lab_only"],
        "planned_artifact_count": len(manifest["planned_artifacts"]),
        "required_controls": list(manifest["required_controls"]),
        "gates": list(manifest["gates"]),
        "pipeline_stages": [stage["name"] for stage in manifest["pipeline_stages"]],
        "notes": list(manifest.get("notes", [])),
    }


def openssl_preflight_report_markdown(report: dict[str, Any]) -> str:
    """Render an OpenSSL preflight report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Preflight Report",
        "",
        f"- Experiment: `{report['experiment_id']}`",
        f"- Target family: `{report['target_family']}`",
        f"- Status: `{report['status']}`",
        f"- Mode: `{report['mode']}`",
        f"- Execution allowed: `{str(report['execution_allowed']).lower()}`",
        f"- Public safe: `{str(report['public_safe']).lower()}`",
        f"- Trace view: `{report['trace_view']}`",
        f"- Raw secret capture allowed: `{str(report['raw_secret_capture_allowed']).lower()}`",
        f"- Lab-only labels: `{str(report['lab_only_labels']).lower()}`",
        f"- Planned artifacts: `{report['planned_artifact_count']}`",
        "",
        "## Pipeline Stages",
        "",
    ]
    lines.extend(f"- `{stage}`" for stage in report["pipeline_stages"])
    lines.extend(["", "## Required Controls", ""])
    lines.extend(f"- `{control}`" for control in report["required_controls"])
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in report["gates"])

    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.append("")
    return "\n".join(lines)


def write_openssl_preflight_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL preflight report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_preflight_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL preflight report as Markdown."""

    Path(path).write_text(openssl_preflight_report_markdown(report), encoding="utf-8")


def _validate_source(source: dict[str, Any]) -> None:
    _require_string(source.get("kind"), "source.kind")
    _require_string(source.get("name"), "source.name")
    _require_string(source.get("ref_policy"), "source.ref_policy")
    _validate_string_list(source.get("target_paths"), "source.target_paths", min_items=1)
    if "pin" not in source["ref_policy"].lower():
        raise OpenSSLPreflightError("source.ref_policy must require pinning an exact source ref")


def _validate_instrumentation(instrumentation: dict[str, Any]) -> None:
    _require_equal(instrumentation.get("trace_view"), "redacted", "instrumentation.trace_view")
    _require_equal(
        instrumentation.get("raw_secret_capture_allowed"),
        False,
        "instrumentation.raw_secret_capture_allowed",
    )
    _require_string(instrumentation.get("event_schema"), "instrumentation.event_schema")
    _validate_string_list(
        instrumentation.get("required_event_fields"),
        "instrumentation.required_event_fields",
        min_items=1,
    )
    disallowed = set(
        _validate_string_list(
            instrumentation.get("disallowed_fields"),
            "instrumentation.disallowed_fields",
            min_items=len(REQUIRED_DISALLOWED_FIELDS),
        )
    )
    missing = sorted(REQUIRED_DISALLOWED_FIELDS - disallowed)
    if missing:
        raise OpenSSLPreflightError(
            f"instrumentation.disallowed_fields missing: {', '.join(missing)}"
        )


def _validate_labels(labels: dict[str, Any]) -> None:
    _require_equal(labels.get("lab_only"), True, "labels.lab_only")
    _validate_string_list(labels.get("allowed_label_keys"), "labels.allowed_label_keys", min_items=1)


def _validate_pipeline_stage(stage: Any, *, index: int) -> None:
    if not isinstance(stage, dict):
        raise OpenSSLPreflightError(f"pipeline_stages[{index}] must be an object")
    _require_string(stage.get("name"), f"pipeline_stages[{index}].name")
    _require_equal(stage.get("status"), "preflight_only", f"pipeline_stages[{index}].status")
    _require_string(stage.get("command_hint"), f"pipeline_stages[{index}].command_hint")


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLPreflightError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLPreflightError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLPreflightError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLPreflightError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLPreflightError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLPreflightError(f"{name} must be {expected!r}")

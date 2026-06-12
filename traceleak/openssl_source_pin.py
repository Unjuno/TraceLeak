"""OpenSSL source pin and source-layout validation.

This module validates a pre-experiment source-layout contract. It does not clone,
build, patch, or execute OpenSSL.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

OPENSSL_SOURCE_PIN_FORMAT = "traceleak.openssl_source_pin.v1"
ALLOWED_MODES = {"template", "pinned"}
REQUIRED_CHECKS = {
    "exact_commit_sha_recorded_before_execution",
    "target_files_exist_after_pin",
    "required_symbols_checked_after_pin",
    "event_map_groups_covered",
    "line_bindings_resolved_after_pin",
    "no_vendored_openssl_source",
}
REQUIRED_GATES = {
    "source_ref_pinned_before_execution",
    "source_layout_review_required",
    "event_map_sync_required",
    "line_binding_after_pin_required",
    "no_raw_secret_fields",
}
_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class OpenSSLSourcePinError(ValueError):
    """Raised when an OpenSSL source-pin manifest is invalid."""


def load_openssl_source_pin(path: str | Path) -> dict[str, Any]:
    """Load and validate an OpenSSL source-pin manifest."""

    input_path = Path(path)
    if not input_path.exists():
        raise OpenSSLSourcePinError(f"source pin manifest not found: {input_path}")
    try:
        manifest = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLSourcePinError(f"invalid JSON in {input_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise OpenSSLSourcePinError("source pin manifest must be a JSON object")
    validate_openssl_source_pin(manifest)
    return manifest


def validate_openssl_source_pin(manifest: dict[str, Any]) -> None:
    """Validate a source-pin/source-layout contract."""

    _require_equal(manifest.get("format"), OPENSSL_SOURCE_PIN_FORMAT, "format")
    _require_string(manifest.get("experiment_id"), "experiment_id")
    target_family = _require_string(manifest.get("target_family"), "target_family")
    if "openssl" not in target_family.lower():
        raise OpenSSLSourcePinError("target_family must identify an OpenSSL target")
    mode = _require_string(manifest.get("mode"), "mode")
    if mode not in ALLOWED_MODES:
        raise OpenSSLSourcePinError(f"mode must be one of: {', '.join(sorted(ALLOWED_MODES))}")
    _require_equal(manifest.get("execution_allowed"), False, "execution_allowed")
    _require_equal(manifest.get("public_safe"), True, "public_safe")

    source = _require_object(manifest.get("source"), "source")
    _validate_source(source, mode=mode)
    _require_string(manifest.get("event_map_path"), "event_map_path")

    layout = _require_list(manifest.get("source_layout"), "source_layout", min_items=1)
    seen_paths: set[str] = set()
    covered_groups: set[str] = set()
    for index, item in enumerate(layout):
        covered_groups.update(_validate_layout_item(item, index=index, seen_paths=seen_paths))
    if not covered_groups:
        raise OpenSSLSourcePinError("source_layout must cover at least one event group")

    checks = set(_validate_string_list(manifest.get("required_checks"), "required_checks", min_items=1))
    missing_checks = sorted(REQUIRED_CHECKS - checks)
    if missing_checks:
        raise OpenSSLSourcePinError(f"required_checks missing: {', '.join(missing_checks)}")

    gates = set(_validate_string_list(manifest.get("gates"), "gates", min_items=1))
    missing_gates = sorted(REQUIRED_GATES - gates)
    if missing_gates:
        raise OpenSSLSourcePinError(f"gates missing: {', '.join(missing_gates)}")
    _validate_string_list(manifest.get("planned_artifacts"), "planned_artifacts", min_items=1)


def openssl_source_pin_report_dict(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized source-pin report."""

    validate_openssl_source_pin(manifest)
    source = manifest["source"]
    layout = manifest["source_layout"]
    return {
        "report_type": "openssl_source_pin_report",
        "status": "source_layout_template_ready" if manifest["mode"] == "template" else "source_pinned_ready",
        "experiment_id": manifest["experiment_id"],
        "target_family": manifest["target_family"],
        "mode": manifest["mode"],
        "execution_allowed": manifest["execution_allowed"],
        "source_kind": source["kind"],
        "source_name": source["name"],
        "worktree_hint": source["worktree_hint"],
        "exact_commit_sha": source.get("exact_commit_sha"),
        "event_map_path": manifest["event_map_path"],
        "target_paths": [item["target_path"] for item in layout],
        "event_groups": sorted(
            {group for item in layout for group in item.get("related_event_groups", [])}
        ),
        "layout": [
            {
                "target_path": item["target_path"],
                "required_symbols": list(item["required_symbols"]),
                "related_event_groups": list(item["related_event_groups"]),
                "line_binding_policy": item["line_binding_policy"],
            }
            for item in layout
        ],
        "gates": list(manifest["gates"]),
        "required_checks": list(manifest["required_checks"]),
        "notes": list(manifest.get("notes", [])),
    }


def openssl_source_pin_report_markdown(report: dict[str, Any]) -> str:
    """Render a source-pin report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Source Pin Report",
        "",
        f"- Experiment: `{report['experiment_id']}`",
        f"- Target family: `{report['target_family']}`",
        f"- Status: `{report['status']}`",
        f"- Mode: `{report['mode']}`",
        f"- Execution allowed: `{str(report['execution_allowed']).lower()}`",
        f"- Worktree hint: `{report['worktree_hint']}`",
        f"- Exact commit SHA: `{report['exact_commit_sha']}`",
        f"- Event map: `{report['event_map_path']}`",
        "",
        "## Source Layout",
        "",
        "| Path | Required symbols | Event groups | Line binding |",
        "|---|---|---|---|",
    ]
    for item in report["layout"]:
        lines.append(
            "| `{path}` | `{symbols}` | `{groups}` | `{policy}` |".format(
                path=item["target_path"],
                symbols=", ".join(item["required_symbols"]),
                groups=", ".join(item["related_event_groups"]),
                policy=item["line_binding_policy"],
            )
        )
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in report["gates"])
    lines.extend(["", "## Required Checks", ""])
    lines.extend(f"- `{check}`" for check in report["required_checks"])
    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.append("")
    return "\n".join(lines)


def write_openssl_source_pin_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a source-pin report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_source_pin_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write a source-pin report as Markdown."""

    Path(path).write_text(openssl_source_pin_report_markdown(report), encoding="utf-8")


def _validate_source(source: dict[str, Any], *, mode: str) -> None:
    _require_equal(source.get("kind"), "external_worktree", "source.kind")
    _require_equal(source.get("name"), "openssl", "source.name")
    _require_string(source.get("repository_hint"), "source.repository_hint")
    _require_string(source.get("worktree_hint"), "source.worktree_hint")
    _require_equal(source.get("pin_required_before_execution"), True, "source.pin_required_before_execution")
    _require_equal(source.get("ref_policy"), "pin_exact_commit_before_run", "source.ref_policy")
    exact_commit_sha = source.get("exact_commit_sha")
    if mode == "template":
        if exact_commit_sha is not None:
            _validate_commit_sha(str(exact_commit_sha), field="source.exact_commit_sha")
        return
    if exact_commit_sha is None:
        raise OpenSSLSourcePinError("source.exact_commit_sha is required in pinned mode")
    _validate_commit_sha(str(exact_commit_sha), field="source.exact_commit_sha")


def _validate_commit_sha(value: str, *, field: str) -> None:
    if not _COMMIT_RE.match(value) or set(value) == {"0"}:
        raise OpenSSLSourcePinError(f"{field} must be a non-zero 40-hex commit SHA")


def _validate_layout_item(item: Any, *, index: int, seen_paths: set[str]) -> set[str]:
    if not isinstance(item, dict):
        raise OpenSSLSourcePinError(f"source_layout[{index}] must be an object")
    target_path = _require_string(item.get("target_path"), f"source_layout[{index}].target_path")
    if target_path in seen_paths:
        raise OpenSSLSourcePinError(f"duplicate source_layout target_path: {target_path}")
    seen_paths.add(target_path)
    if not target_path.endswith(".c"):
        raise OpenSSLSourcePinError(f"source_layout[{index}].target_path must be a C source file")
    symbols = _validate_string_list(
        item.get("required_symbols"),
        f"source_layout[{index}].required_symbols",
        min_items=1,
    )
    for symbol in symbols:
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", symbol):
            raise OpenSSLSourcePinError(f"source_layout[{index}].required_symbols contains invalid symbol: {symbol}")
    groups = set(
        _validate_string_list(
            item.get("related_event_groups"),
            f"source_layout[{index}].related_event_groups",
            min_items=1,
        )
    )
    _require_equal(
        item.get("line_binding_policy"),
        "resolve_after_exact_commit_pin",
        f"source_layout[{index}].line_binding_policy",
    )
    return groups


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLSourcePinError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLSourcePinError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLSourcePinError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLSourcePinError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLSourcePinError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLSourcePinError(f"{name} must be {expected!r}")

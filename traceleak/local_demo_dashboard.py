"""Combined local dashboard for metadata-only demo outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LOCAL_DEMO_DASHBOARD_FORMAT = "traceleak.local_demo_dashboard.v1"
LOCAL_DEMO_DASHBOARD_PHASE = "P90"
DEFAULT_DASHBOARD_FILES = {
    "metadata_summary": {
        "path": "openssl_metadata_demo/demo-summary.json",
        "role": "metadata demo JSON summary",
    },
    "metadata_markdown": {
        "path": "openssl_metadata_demo/demo-summary.md",
        "role": "metadata demo Markdown summary",
    },
    "metadata_metrics_json": {
        "path": "openssl_metadata_demo/demo-metrics.json",
        "role": "metadata demo compact metrics JSON",
    },
    "metadata_metrics_csv": {
        "path": "openssl_metadata_demo/demo-metrics.csv",
        "role": "metadata demo compact metrics CSV",
    },
    "metadata_index": {
        "path": "openssl_metadata_demo/artifact-index.json",
        "role": "metadata demo local file index",
    },
    "symbolic_summary": {
        "path": "symbolic_metadata_demo/symbolic-demo-summary.json",
        "role": "symbolic demo JSON summary",
    },
    "symbolic_report": {
        "path": "symbolic_metadata_demo/symbolic-demo-report.md",
        "role": "symbolic demo Markdown report",
    },
    "comparison_json": {
        "path": "demo-summary-comparison.json",
        "role": "metadata/symbolic comparison JSON",
    },
    "comparison_markdown": {
        "path": "demo-summary-comparison.md",
        "role": "metadata/symbolic comparison Markdown",
    },
}
REGENERATION_COMMANDS = [
    "traceleak-run-openssl-metadata-demo-chain --out-dir reports/local/openssl_metadata_demo --record-count 4 --epochs 20 --write-markdown-summary --include-ranking --write-metrics-json --write-metrics-csv --write-artifact-index-json --write-artifact-index-markdown --write-command-snippet",
    "traceleak-run-symbolic-metadata-demo-chain --out-dir reports/local/symbolic_metadata_demo --epochs 20 --write-report",
    "traceleak-compare-demo-summaries --metadata-summary reports/local/openssl_metadata_demo/demo-summary.json --symbolic-summary reports/local/symbolic_metadata_demo/symbolic-demo-summary.json --out reports/local/demo-summary-comparison.json --markdown-out reports/local/demo-summary-comparison.md",
]


class LocalDemoDashboardError(ValueError):
    """Raised when local demo dashboard inputs or outputs are invalid."""


def build_local_demo_dashboard(
    *,
    root_dir: Path = Path("reports/local"),
    expected_files: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a path-only dashboard over local metadata-only demo outputs."""

    files = expected_files or DEFAULT_DASHBOARD_FILES
    if not isinstance(files, dict) or not files:
        raise LocalDemoDashboardError("expected_files must be a non-empty object")
    entries = []
    for key, spec in sorted(files.items()):
        if not isinstance(spec, dict):
            raise LocalDemoDashboardError("expected file specs must be objects")
        path_text = _safe_relative_path(spec.get("path"), f"{key}.path")
        role = spec.get("role")
        if not isinstance(role, str) or not role:
            raise LocalDemoDashboardError(f"{key}.role must be a non-empty string")
        path = root_dir / path_text
        entries.append(
            {
                "key": str(key),
                "relative_path": path_text,
                "role": role,
                "exists": path.is_file(),
                "size_bytes": path.stat().st_size if path.is_file() else None,
            }
        )
    dashboard = {
        "format": LOCAL_DEMO_DASHBOARD_FORMAT,
        "phase": LOCAL_DEMO_DASHBOARD_PHASE,
        "root_dir": str(root_dir).replace("\\", "/"),
        "entry_count": len(entries),
        "present_count": sum(1 for item in entries if item["exists"]),
        "missing_count": sum(1 for item in entries if not item["exists"]),
        "entries": entries,
        "regeneration_commands": list(REGENERATION_COMMANDS),
        "payload_inspected": False,
        "flags": {
            "metadata_only": True,
            "public_safe": True,
            "openssl_leakage_claim": False,
        },
    }
    validate_local_demo_dashboard(dashboard)
    return dashboard


def render_local_demo_dashboard_markdown(dashboard: dict[str, Any]) -> str:
    """Render the local dashboard as Markdown."""

    validate_local_demo_dashboard(dashboard)
    lines = [
        "# Local Demo Dashboard",
        "",
        f"- Phase: `{dashboard['phase']}`",
        f"- Root: `{dashboard['root_dir']}`",
        f"- Present files: `{dashboard['present_count']}`",
        f"- Missing files: `{dashboard['missing_count']}`",
        "- Payload inspected: `False`",
        "",
        "| Key | Path | Role | Status | Size bytes |",
        "|---|---|---|---:|---:|",
    ]
    for item in dashboard["entries"]:
        status = "present" if item["exists"] else "missing"
        size = "" if item["size_bytes"] is None else str(item["size_bytes"])
        lines.append(
            f"| `{item['key']}` | `{item['relative_path']}` | {item['role']} | {status} | {size} |"
        )
    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```powershell",
            "cd C:\\Users\\junny\\Desktop\\traceLeak\\TraceLeak",
            *dashboard["regeneration_commands"],
            "```",
            "",
            "## Notes",
            "",
            "This dashboard lists local metadata-only demo output paths.",
            "It does not inspect file payloads and is not OpenSSL leakage evidence.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    validate_local_demo_dashboard_markdown(markdown)
    return markdown


def validate_local_demo_dashboard(dashboard: dict[str, Any]) -> None:
    """Validate local demo dashboard shape."""

    _eq(dashboard.get("format"), LOCAL_DEMO_DASHBOARD_FORMAT, "dashboard.format")
    _eq(dashboard.get("phase"), LOCAL_DEMO_DASHBOARD_PHASE, "dashboard.phase")
    if not isinstance(dashboard.get("root_dir"), str) or not dashboard["root_dir"]:
        raise LocalDemoDashboardError("dashboard.root_dir must be a non-empty string")
    entries = dashboard.get("entries")
    if not isinstance(entries, list) or not entries:
        raise LocalDemoDashboardError("dashboard.entries must be a non-empty list")
    present_count = 0
    missing_count = 0
    seen_keys: set[str] = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise LocalDemoDashboardError(f"dashboard.entries[{index}] must be an object")
        key = item.get("key")
        if not isinstance(key, str) or not key:
            raise LocalDemoDashboardError(f"dashboard.entries[{index}].key must be a non-empty string")
        if key in seen_keys:
            raise LocalDemoDashboardError("dashboard entry keys must be unique")
        seen_keys.add(key)
        _safe_relative_path(item.get("relative_path"), f"dashboard.entries[{index}].relative_path")
        if not isinstance(item.get("role"), str) or not item["role"]:
            raise LocalDemoDashboardError(f"dashboard.entries[{index}].role must be a non-empty string")
        if item.get("exists") is True:
            present_count += 1
            if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] < 0:
                raise LocalDemoDashboardError("present size_bytes must be non-negative")
        elif item.get("exists") is False:
            missing_count += 1
            if item.get("size_bytes") is not None:
                raise LocalDemoDashboardError("missing size_bytes must be null")
        else:
            raise LocalDemoDashboardError("dashboard entry exists must be boolean")
    _eq(dashboard.get("entry_count"), len(entries), "dashboard.entry_count")
    _eq(dashboard.get("present_count"), present_count, "dashboard.present_count")
    _eq(dashboard.get("missing_count"), missing_count, "dashboard.missing_count")
    commands = dashboard.get("regeneration_commands")
    if not isinstance(commands, list) or len(commands) != 3:
        raise LocalDemoDashboardError("dashboard.regeneration_commands must contain three commands")
    for index, command in enumerate(commands):
        if not isinstance(command, str) or not command:
            raise LocalDemoDashboardError(f"dashboard.regeneration_commands[{index}] must be non-empty")
    _eq(dashboard.get("payload_inspected"), False, "dashboard.payload_inspected")
    flags = dashboard.get("flags")
    if not isinstance(flags, dict):
        raise LocalDemoDashboardError("dashboard.flags must be an object")
    _eq(flags.get("metadata_only"), True, "dashboard.flags.metadata_only")
    _eq(flags.get("public_safe"), True, "dashboard.flags.public_safe")
    _eq(flags.get("openssl_leakage_claim"), False, "dashboard.flags.openssl_leakage_claim")


def validate_local_demo_dashboard_markdown(markdown: str) -> None:
    """Validate local demo dashboard Markdown shape."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise LocalDemoDashboardError("markdown must be a newline-terminated string")
    for text in [
        "# Local Demo Dashboard",
        "| Key | Path | Role | Status | Size bytes |",
        "## Regenerate",
        "traceleak-run-openssl-metadata-demo-chain",
        "traceleak-run-symbolic-metadata-demo-chain",
        "traceleak-compare-demo-summaries",
        "It does not inspect file payloads and is not OpenSSL leakage evidence.",
    ]:
        if text not in markdown:
            raise LocalDemoDashboardError(f"missing markdown text: {text}")


def write_local_demo_dashboard_json(path: Path, dashboard: dict[str, Any]) -> None:
    """Write local demo dashboard JSON."""

    validate_local_demo_dashboard(dashboard)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dashboard, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_local_demo_dashboard_markdown(path: Path, markdown: str) -> None:
    """Write local demo dashboard Markdown."""

    validate_local_demo_dashboard_markdown(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _safe_relative_path(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise LocalDemoDashboardError(f"{name} must be a non-empty string")
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise LocalDemoDashboardError(f"{name} must be a plain relative path")
    return normalized


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise LocalDemoDashboardError(f"{name} must be {expected!r}")

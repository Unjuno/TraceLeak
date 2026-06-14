"""One-command local report bundle generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.demo_summary_comparison import (
    build_demo_summary_comparison,
    render_demo_summary_comparison_markdown,
    write_demo_summary_comparison_json,
    write_demo_summary_comparison_markdown,
)
from traceleak.local_demo_dashboard import (
    build_local_demo_dashboard,
    render_local_demo_dashboard_markdown,
    write_local_demo_dashboard_json,
    write_local_demo_dashboard_markdown,
)
from traceleak.metadata_demo_artifact_index import (
    build_metadata_demo_artifact_index,
    render_metadata_demo_artifact_index_markdown,
    write_metadata_demo_artifact_index_json,
    write_metadata_demo_artifact_index_markdown,
)
from traceleak.metadata_demo_markdown_summary import (
    render_metadata_demo_markdown_summary_from_artifacts,
    write_metadata_demo_markdown_summary,
)
from traceleak.metadata_demo_metrics import (
    build_metadata_demo_metrics_from_artifacts,
    write_metadata_demo_metrics_csv,
    write_metadata_demo_metrics_json,
)
from traceleak.metadata_demo_readme_snippet import (
    render_metadata_demo_readme_snippet,
    write_metadata_demo_readme_snippet,
)
from traceleak.openssl_metadata_demo_chain import (
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_chain import (
    build_symbolic_metadata_demo_chain,
    write_symbolic_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_report import (
    render_symbolic_metadata_demo_report,
    write_symbolic_metadata_demo_report,
)

LOCAL_REPORT_BUNDLE_FORMAT = "traceleak.local_report_bundle.v1"
LOCAL_REPORT_BUNDLE_PHASE = "P93"


class LocalReportBundleError(ValueError):
    """Raised when local report bundle generation is invalid."""


def run_local_report_bundle(
    *,
    root_dir: Path = Path("reports/local"),
    record_count: int = 4,
    epochs: int = 20,
) -> dict[str, Any]:
    """Generate all local metadata-only demo report surfaces under root_dir."""

    if record_count < 4 or record_count % 2 != 0:
        raise LocalReportBundleError("record_count must be an even integer >= 4")
    if epochs <= 0:
        raise LocalReportBundleError("epochs must be positive")

    metadata_dir = root_dir / "openssl_metadata_demo"
    symbolic_dir = root_dir / "symbolic_metadata_demo"
    metadata_artifacts = build_openssl_metadata_demo_chain(
        record_count=record_count,
        epochs=epochs,
    )
    write_openssl_metadata_demo_chain(output_dir=metadata_dir, artifacts=metadata_artifacts)
    _write_metadata_extra_outputs(metadata_dir=metadata_dir, artifacts=metadata_artifacts)

    symbolic_artifacts = build_symbolic_metadata_demo_chain(epochs=epochs)
    write_symbolic_metadata_demo_chain(output_dir=symbolic_dir, artifacts=symbolic_artifacts)
    write_symbolic_metadata_demo_report(
        symbolic_dir / "symbolic-demo-report.md",
        render_symbolic_metadata_demo_report(symbolic_artifacts["demo_summary"]),
    )

    comparison = build_demo_summary_comparison(
        metadata_summary=metadata_artifacts["demo_summary"],
        symbolic_summary=symbolic_artifacts["demo_summary"],
    )
    write_demo_summary_comparison_json(root_dir / "demo-summary-comparison.json", comparison)
    write_demo_summary_comparison_markdown(
        root_dir / "demo-summary-comparison.md",
        render_demo_summary_comparison_markdown(comparison),
    )

    dashboard = build_local_demo_dashboard(root_dir=root_dir)
    write_local_demo_dashboard_json(root_dir / "local-demo-dashboard.json", dashboard)
    write_local_demo_dashboard_markdown(
        root_dir / "local-demo-dashboard.md",
        render_local_demo_dashboard_markdown(dashboard),
    )

    summary = build_local_report_bundle_summary(
        root_dir=root_dir,
        metadata_dir=metadata_dir,
        symbolic_dir=symbolic_dir,
        dashboard=dashboard,
        record_count=record_count,
        epochs=epochs,
    )
    write_local_report_bundle_summary(root_dir / "local-report-bundle-summary.json", summary)
    return summary


def build_local_report_bundle_summary(
    *,
    root_dir: Path,
    metadata_dir: Path,
    symbolic_dir: Path,
    dashboard: dict[str, Any],
    record_count: int,
    epochs: int,
) -> dict[str, Any]:
    """Build a compact bundle summary object."""

    summary = {
        "format": LOCAL_REPORT_BUNDLE_FORMAT,
        "phase": LOCAL_REPORT_BUNDLE_PHASE,
        "root_dir": _display_path(root_dir),
        "metadata_dir": _display_path(metadata_dir),
        "symbolic_dir": _display_path(symbolic_dir),
        "record_count": record_count,
        "epochs": epochs,
        "dashboard_format": dashboard["format"],
        "dashboard_present_count": dashboard["present_count"],
        "dashboard_missing_count": dashboard["missing_count"],
        "outputs": {
            "metadata_summary": _display_path(metadata_dir / "demo-summary.json"),
            "symbolic_summary": _display_path(symbolic_dir / "symbolic-demo-summary.json"),
            "comparison_summary": _display_path(root_dir / "demo-summary-comparison.json"),
            "dashboard": _display_path(root_dir / "local-demo-dashboard.json"),
        },
        "flags": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "payload_inspected": False,
            "openssl_leakage_claim": False,
        },
        "next_level": {
            "level": 6,
            "name": "openssl-derived metadata ingestion hardening",
            "ready_after_local_validation": True,
        },
    }
    validate_local_report_bundle_summary(summary)
    return summary


def validate_local_report_bundle_summary(summary: dict[str, Any]) -> None:
    """Validate local report bundle summary shape."""

    _eq(summary.get("format"), LOCAL_REPORT_BUNDLE_FORMAT, "summary.format")
    _eq(summary.get("phase"), LOCAL_REPORT_BUNDLE_PHASE, "summary.phase")
    for key in ["root_dir", "metadata_dir", "symbolic_dir"]:
        if not isinstance(summary.get(key), str) or not summary[key]:
            raise LocalReportBundleError(f"summary.{key} must be a non-empty string")
    if not isinstance(summary.get("record_count"), int) or summary["record_count"] < 4:
        raise LocalReportBundleError("summary.record_count must be at least four")
    if not isinstance(summary.get("epochs"), int) or summary["epochs"] <= 0:
        raise LocalReportBundleError("summary.epochs must be positive")
    _eq(summary.get("dashboard_format"), "traceleak.local_demo_dashboard.v1", "summary.dashboard_format")
    if not isinstance(summary.get("dashboard_present_count"), int):
        raise LocalReportBundleError("summary.dashboard_present_count must be an integer")
    if not isinstance(summary.get("dashboard_missing_count"), int):
        raise LocalReportBundleError("summary.dashboard_missing_count must be an integer")
    outputs = summary.get("outputs")
    if not isinstance(outputs, dict):
        raise LocalReportBundleError("summary.outputs must be an object")
    for key in ["metadata_summary", "symbolic_summary", "comparison_summary", "dashboard"]:
        if not isinstance(outputs.get(key), str) or not outputs[key]:
            raise LocalReportBundleError(f"summary.outputs.{key} must be a non-empty string")
    flags = summary.get("flags")
    if not isinstance(flags, dict):
        raise LocalReportBundleError("summary.flags must be an object")
    for key in ["metadata_only", "payload_free", "public_safe"]:
        _eq(flags.get(key), True, f"summary.flags.{key}")
    _eq(flags.get("payload_inspected"), False, "summary.flags.payload_inspected")
    _eq(flags.get("openssl_leakage_claim"), False, "summary.flags.openssl_leakage_claim")
    next_level = summary.get("next_level")
    if not isinstance(next_level, dict):
        raise LocalReportBundleError("summary.next_level must be an object")
    _eq(next_level.get("level"), 6, "summary.next_level.level")
    _eq(
        next_level.get("name"),
        "openssl-derived metadata ingestion hardening",
        "summary.next_level.name",
    )
    _eq(
        next_level.get("ready_after_local_validation"),
        True,
        "summary.next_level.ready_after_local_validation",
    )


def write_local_report_bundle_summary(path: Path, summary: dict[str, Any]) -> None:
    """Write local report bundle summary JSON."""

    validate_local_report_bundle_summary(summary)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_metadata_extra_outputs(*, metadata_dir: Path, artifacts: dict[str, Any]) -> None:
    write_metadata_demo_markdown_summary(
        metadata_dir / "demo-summary.md",
        render_metadata_demo_markdown_summary_from_artifacts(artifacts, include_ranking=True),
    )
    metrics = build_metadata_demo_metrics_from_artifacts(artifacts)
    write_metadata_demo_metrics_json(metadata_dir / "demo-metrics.json", metrics)
    write_metadata_demo_metrics_csv(metadata_dir / "demo-metrics.csv", metrics)
    index = build_metadata_demo_artifact_index(output_dir=metadata_dir)
    write_metadata_demo_artifact_index_json(metadata_dir / "artifact-index.json", index)
    write_metadata_demo_artifact_index_markdown(
        metadata_dir / "artifact-index.md",
        render_metadata_demo_artifact_index_markdown(index),
    )
    write_metadata_demo_readme_snippet(
        metadata_dir / "demo-commands.md",
        render_metadata_demo_readme_snippet(output_dir=metadata_dir),
    )


def _display_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise LocalReportBundleError(f"{name} must be {expected!r}")

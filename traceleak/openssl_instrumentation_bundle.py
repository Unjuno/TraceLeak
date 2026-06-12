"""Validate generated OpenSSL instrumentation dry-run output bundles.

The bundle validator re-reads artifacts produced by the review-only OpenSSL
instrumentation chain and checks that the saved outputs are internally
consistent and still pass the downstream redacted event/sample gates. It does
not build, run, instrument, patch, compile, or trace OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_event_emitter_artifact import validate_openssl_event_emitter_artifact
from traceleak.openssl_event_emitter_self_check import run_openssl_event_emitter_self_check
from traceleak.openssl_instrumentation_stub import validate_openssl_instrumentation_stub
from traceleak.openssl_source_edit_proposal import validate_openssl_source_edit_proposal
from traceleak.openssl_trace_acceptance import validate_openssl_trace_sample_acceptance
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, validate_openssl_trace_contract
from traceleak.openssl_trace_event_stream import validate_openssl_redacted_event_stream

REQUIRED_BUNDLE_FILES = {
    "summary": "openssl_instrumentation_chain_summary.json",
    "stub": "openssl_instrumentation_stub.json",
    "source_edit": "openssl_source_edit_proposal.json",
    "event_emitter": "openssl_event_emitter_artifact.json",
    "event_stream_report": "openssl_redacted_event_stream_report.json",
    "model_sequence_sample": "openssl_model_sequence_sample.json",
    "sample_acceptance_report": "openssl_trace_sample_acceptance_report.json",
}
SELF_CHECK_DIR = "openssl_event_emitter_self_check"
SELF_CHECK_STREAM = "openssl_event_emitter_self_check_events.jsonl"
SELF_CHECK_SAMPLE = "openssl_event_emitter_self_check_model_sequence_sample.json"


class OpenSSLInstrumentationBundleError(ValueError):
    """Raised when an OpenSSL instrumentation output bundle is invalid."""


def validate_openssl_instrumentation_bundle(
    *,
    contract: dict[str, Any],
    bundle_dir: str | Path,
) -> dict[str, Any]:
    """Validate an OpenSSL instrumentation dry-run output bundle."""

    try:
        validate_openssl_trace_contract(contract)
    except OpenSSLTraceContractError as exc:
        raise OpenSSLInstrumentationBundleError(str(exc)) from exc
    base_dir = Path(bundle_dir)
    if not base_dir.exists():
        raise OpenSSLInstrumentationBundleError(f"bundle directory not found: {base_dir}")
    artifacts = {name: _load_json(base_dir / filename) for name, filename in REQUIRED_BUNDLE_FILES.items()}
    _validate_bundle_artifacts(contract=contract, artifacts=artifacts, bundle_dir=base_dir)
    event_count = int(artifacts["event_stream_report"]["event_count"])
    record_count = int(artifacts["sample_acceptance_report"]["record_count"])
    self_check_report = run_openssl_event_emitter_self_check(
        contract=contract,
        emitter_artifact=artifacts["event_emitter"],
    )
    _validate_self_check_outputs(
        contract=contract,
        bundle_dir=base_dir,
        expected_report=self_check_report,
    )
    return {
        "report_type": "openssl_instrumentation_bundle_report",
        "status": "bundle_validated",
        "contract_id": contract["contract_id"],
        "target": contract["target"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_collection_mode": "redacted",
        "bundle_dir": str(base_dir),
        "required_file_count": len(REQUIRED_BUNDLE_FILES),
        "event_count": event_count,
        "record_count": record_count,
        "self_check_run_count": self_check_report["run_count"],
        "self_check_event_count": self_check_report["event_count"],
        "notes": [
            "Bundle validation re-reads saved dry-run outputs and revalidates downstream gates.",
            "A valid bundle is still review-only and is not proof of an actual OpenSSL run.",
        ],
    }


def write_openssl_instrumentation_bundle_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write bundle validation report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_instrumentation_bundle_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write bundle validation report as Markdown."""

    Path(path).write_text(openssl_instrumentation_bundle_markdown(report), encoding="utf-8")


def openssl_instrumentation_bundle_markdown(report: dict[str, Any]) -> str:
    """Render bundle validation report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Instrumentation Bundle Validation",
        "",
        f"- Status: `{report['status']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Target: `{report['target']}`",
        f"- Target version: `{report['target_version']}`",
        f"- Source pin: `{report['source_pin']}`",
        f"- Build ID: `{report['build_id']}`",
        f"- Bundle: `{report['bundle_dir']}`",
        f"- Execution allowed: `{str(report['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(report['source_mutation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(report['patch_application_allowed']).lower()}`",
        f"- Compile allowed: `{str(report['compile_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(report['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Counts",
        "",
        f"- Required files: `{report['required_file_count']}`",
        f"- Events: `{report['event_count']}`",
        f"- Records: `{report['record_count']}`",
        f"- Self-check runs: `{report['self_check_run_count']}`",
        f"- Self-check events: `{report['self_check_event_count']}`",
        "",
        "## Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in report["notes"])
    lines.append("")
    return "\n".join(lines)


def _validate_bundle_artifacts(
    *,
    contract: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    bundle_dir: Path,
) -> None:
    summary = artifacts["summary"]
    _require_equal(summary.get("status"), "dry_run_chain_ready_not_executed", "summary.status")
    _require_equal(summary.get("execution_allowed"), False, "summary.execution_allowed")
    _require_equal(summary.get("source_mutation_allowed"), False, "summary.source_mutation_allowed")
    _require_equal(summary.get("patch_application_allowed"), False, "summary.patch_application_allowed")
    _require_equal(summary.get("compile_allowed"), False, "summary.compile_allowed")
    _require_equal(summary.get("raw_secret_capture_allowed"), False, "summary.raw_secret_capture_allowed")
    _require_contract_identity(contract, summary, "summary")
    validate_openssl_instrumentation_stub(artifacts["stub"])
    validate_openssl_source_edit_proposal(artifacts["source_edit"])
    validate_openssl_event_emitter_artifact(artifacts["event_emitter"])
    _validate_report_status(
        artifacts["event_stream_report"],
        expected_status="accepted_redacted_openssl_event_stream",
        name="event_stream_report",
    )
    sample = artifacts["model_sequence_sample"]
    validate_openssl_trace_sample_acceptance(contract, sample)
    _validate_report_status(
        artifacts["sample_acceptance_report"],
        expected_status="accepted_redacted_model_sequence_sample",
        name="sample_acceptance_report",
    )
    _require_equal(
        summary.get("event_count"),
        artifacts["event_stream_report"].get("event_count"),
        "summary.event_count",
    )
    _require_equal(
        summary.get("record_count"),
        artifacts["sample_acceptance_report"].get("record_count"),
        "summary.record_count",
    )
    summary_md = bundle_dir / "openssl_instrumentation_chain_summary.md"
    if summary_md.exists() and "dry_run_chain_ready_not_executed" not in summary_md.read_text(encoding="utf-8"):
        raise OpenSSLInstrumentationBundleError("summary markdown does not contain dry-run status")


def _validate_self_check_outputs(
    *,
    contract: dict[str, Any],
    bundle_dir: Path,
    expected_report: dict[str, Any],
) -> None:
    self_check_dir = bundle_dir / SELF_CHECK_DIR
    if not self_check_dir.exists():
        raise OpenSSLInstrumentationBundleError(f"self-check directory not found: {self_check_dir}")
    stream_path = self_check_dir / SELF_CHECK_STREAM
    sample_path = self_check_dir / SELF_CHECK_SAMPLE
    if not stream_path.exists():
        raise OpenSSLInstrumentationBundleError(f"self-check JSONL not found: {stream_path}")
    if not sample_path.exists():
        raise OpenSSLInstrumentationBundleError(f"self-check model sequence sample not found: {sample_path}")
    runs = [_json_line(line, stream_path=stream_path, line_number=index) for index, line in _nonempty_lines(stream_path)]
    validate_openssl_redacted_event_stream(contract, runs)
    sample = _load_json(sample_path)
    validate_openssl_trace_sample_acceptance(contract, sample)
    _require_equal(len(runs), expected_report["run_count"], "self_check.run_count")
    _require_equal(
        sum(len(run["events"]) for run in runs),
        expected_report["event_count"],
        "self_check.event_count",
    )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise OpenSSLInstrumentationBundleError(f"required bundle file not found: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLInstrumentationBundleError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OpenSSLInstrumentationBundleError(f"{path} must contain a JSON object")
    return value


def _nonempty_lines(path: Path) -> list[tuple[int, str]]:
    return [
        (index, line.strip())
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if line.strip()
    ]


def _json_line(line: str, *, stream_path: Path, line_number: int) -> dict[str, Any]:
    try:
        value = json.loads(line)
    except json.JSONDecodeError as exc:
        raise OpenSSLInstrumentationBundleError(f"invalid JSONL in {stream_path}:{line_number}: {exc}") from exc
    if not isinstance(value, dict):
        raise OpenSSLInstrumentationBundleError(f"{stream_path}:{line_number} must contain a JSON object")
    return value


def _validate_report_status(report: dict[str, Any], *, expected_status: str, name: str) -> None:
    _require_equal(report.get("status"), expected_status, f"{name}.status")
    _require_equal(report.get("raw_secret_captured"), False, f"{name}.raw_secret_captured")
    _require_equal(report.get("public_safe"), True, f"{name}.public_safe")


def _require_contract_identity(contract: dict[str, Any], artifact: dict[str, Any], name: str) -> None:
    for field in ("target", "target_version", "source_pin", "build_id"):
        _require_equal(artifact.get(field), contract[field], f"{name}.{field}")


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLInstrumentationBundleError(f"{name} must be {expected!r}")

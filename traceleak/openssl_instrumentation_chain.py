"""Run the OpenSSL review-only instrumentation-to-sample dry-run chain.

The chain joins the existing review artifacts and redacted data gates:
instrumentation stub, source edit proposal, redacted event emitter artifact,
emitter self-check, redacted event stream validation, model_sequence.v1 sample
build, and sample acceptance. It does not build, run, instrument, patch,
compile, or trace OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_event_emitter_artifact import (
    build_openssl_event_emitter_artifact,
    openssl_event_emitter_artifact_markdown,
    write_openssl_event_emitter_artifact_files,
    write_openssl_event_emitter_artifact_json,
)
from traceleak.openssl_event_emitter_self_check import (
    openssl_event_emitter_self_check_markdown,
    run_openssl_event_emitter_self_check,
    write_openssl_event_emitter_self_check_outputs,
)
from traceleak.openssl_instrumentation_bundle_manifest import (
    build_openssl_instrumentation_bundle_manifest,
    write_openssl_instrumentation_bundle_manifest_json,
    write_openssl_instrumentation_bundle_manifest_markdown,
)
from traceleak.openssl_instrumentation_stub import (
    build_openssl_instrumentation_stub,
    instrumentation_stub_markdown,
    write_instrumentation_stub_json,
)
from traceleak.openssl_source_edit_proposal import (
    build_openssl_source_edit_proposal,
    source_edit_proposal_markdown,
    write_source_edit_proposal_json,
)
from traceleak.openssl_trace_acceptance import (
    openssl_trace_sample_acceptance_report_dict,
    openssl_trace_sample_acceptance_report_markdown,
)
from traceleak.openssl_trace_contract import load_openssl_trace_contract
from traceleak.openssl_trace_event_stream import (
    load_openssl_redacted_event_stream,
    openssl_redacted_event_stream_report_dict,
    openssl_redacted_event_stream_report_markdown,
)
from traceleak.openssl_trace_sample_builder import build_openssl_model_sequence_sample, write_model_sequence_sample


class OpenSSLInstrumentationChainError(ValueError):
    """Raised when the review-only OpenSSL instrumentation chain fails."""


def run_openssl_instrumentation_dry_run_chain(
    *,
    source_pin_path: str | Path,
    event_map_path: str | Path,
    contract_path: str | Path,
    event_stream_path: str | Path,
) -> dict[str, Any]:
    """Run the review-only OpenSSL instrumentation-to-sample chain in memory."""

    try:
        stub = build_openssl_instrumentation_stub(
            source_pin_path=source_pin_path,
            event_map_path=event_map_path,
        )
        source_edit = build_openssl_source_edit_proposal(
            source_pin_path=source_pin_path,
            event_map_path=event_map_path,
        )
        contract = load_openssl_trace_contract(contract_path)
        event_emitter = build_openssl_event_emitter_artifact(
            contract=contract,
            instrumentation_stub=stub,
        )
        emitter_self_check = run_openssl_event_emitter_self_check(
            contract=contract,
            emitter_artifact=event_emitter,
        )
        runs = load_openssl_redacted_event_stream(event_stream_path)
        event_stream_report = openssl_redacted_event_stream_report_dict(contract, runs)
        sample = build_openssl_model_sequence_sample(
            contract=contract,
            runs=runs,
            input_name=str(event_stream_path),
        )
        sample_acceptance_report = openssl_trace_sample_acceptance_report_dict(contract, sample)
    except ValueError as exc:
        raise OpenSSLInstrumentationChainError(str(exc)) from exc

    return {
        "report_type": "openssl_instrumentation_dry_run_chain_report",
        "status": "dry_run_chain_ready_not_executed",
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_collection_mode": "redacted",
        "stub_status": stub["status"],
        "source_edit_status": source_edit["status"],
        "event_emitter_status": event_emitter["status"],
        "emitter_self_check_status": emitter_self_check["status"],
        "event_stream_status": event_stream_report["status"],
        "sample_acceptance_status": sample_acceptance_report["status"],
        "experiment_id": stub["experiment_id"],
        "target": contract["target"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "planned_event_count": len(stub["planned_events"]),
        "proposal_count": len(source_edit["proposals"]),
        "emitter_file_count": len(event_emitter["files"]),
        "self_check_run_count": emitter_self_check["run_count"],
        "self_check_event_count": emitter_self_check["event_count"],
        "run_count": event_stream_report["run_count"],
        "event_count": event_stream_report["event_count"],
        "record_count": sample_acceptance_report["record_count"],
        "feature_count": sample_acceptance_report["feature_count"],
        "artifacts": {
            "trace_contract": contract,
            "instrumentation_stub": stub,
            "source_edit_proposal": source_edit,
            "event_emitter_artifact": event_emitter,
            "event_emitter_self_check": emitter_self_check,
            "event_stream_report": event_stream_report,
            "model_sequence_sample": sample,
            "sample_acceptance_report": sample_acceptance_report,
        },
        "notes": [
            "This is a review-only dry run chain.",
            "It does not build, run, instrument, patch, compile, or trace OpenSSL.",
            "The redacted event stream fixture is contract-compatible but is not proof of an actual OpenSSL run.",
        ],
    }


def write_openssl_instrumentation_chain_outputs(out_dir: str | Path, report: dict[str, Any]) -> dict[str, Path]:
    """Write the dry-run chain artifacts and return output paths."""

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = report["artifacts"]
    paths = {
        "summary_json": output_dir / "openssl_instrumentation_chain_summary.json",
        "summary_md": output_dir / "openssl_instrumentation_chain_summary.md",
        "stub_json": output_dir / "openssl_instrumentation_stub.json",
        "stub_md": output_dir / "openssl_instrumentation_stub.md",
        "source_edit_json": output_dir / "openssl_source_edit_proposal.json",
        "source_edit_md": output_dir / "openssl_source_edit_proposal.md",
        "event_emitter_json": output_dir / "openssl_event_emitter_artifact.json",
        "event_emitter_md": output_dir / "openssl_event_emitter_artifact.md",
        "event_emitter_dir": output_dir / "openssl_event_emitter_files",
        "event_emitter_self_check_dir": output_dir / "openssl_event_emitter_self_check",
        "event_emitter_self_check_md": output_dir / "openssl_event_emitter_self_check_summary.md",
        "event_stream_json": output_dir / "openssl_redacted_event_stream_report.json",
        "event_stream_md": output_dir / "openssl_redacted_event_stream_report.md",
        "model_sequence_sample_json": output_dir / "openssl_model_sequence_sample.json",
        "sample_acceptance_json": output_dir / "openssl_trace_sample_acceptance_report.json",
        "sample_acceptance_md": output_dir / "openssl_trace_sample_acceptance_report.md",
        "bundle_manifest_json": output_dir / "openssl_instrumentation_bundle_manifest.json",
        "bundle_manifest_md": output_dir / "openssl_instrumentation_bundle_manifest.md",
    }
    write_instrumentation_stub_json(paths["stub_json"], artifacts["instrumentation_stub"])
    paths["stub_md"].write_text(
        instrumentation_stub_markdown(artifacts["instrumentation_stub"]),
        encoding="utf-8",
    )
    write_source_edit_proposal_json(paths["source_edit_json"], artifacts["source_edit_proposal"])
    paths["source_edit_md"].write_text(
        source_edit_proposal_markdown(artifacts["source_edit_proposal"]),
        encoding="utf-8",
    )
    write_openssl_event_emitter_artifact_json(
        paths["event_emitter_json"], artifacts["event_emitter_artifact"]
    )
    paths["event_emitter_md"].write_text(
        openssl_event_emitter_artifact_markdown(artifacts["event_emitter_artifact"]),
        encoding="utf-8",
    )
    write_openssl_event_emitter_artifact_files(
        paths["event_emitter_dir"], artifacts["event_emitter_artifact"]
    )
    self_check_paths = write_openssl_event_emitter_self_check_outputs(
        paths["event_emitter_self_check_dir"], artifacts["event_emitter_self_check"]
    )
    paths["event_emitter_self_check_md"].write_text(
        openssl_event_emitter_self_check_markdown(artifacts["event_emitter_self_check"]),
        encoding="utf-8",
    )
    paths["event_stream_json"].write_text(
        json.dumps(artifacts["event_stream_report"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["event_stream_md"].write_text(
        openssl_redacted_event_stream_report_markdown(artifacts["event_stream_report"]),
        encoding="utf-8",
    )
    write_model_sequence_sample(paths["model_sequence_sample_json"], artifacts["model_sequence_sample"])
    paths["sample_acceptance_json"].write_text(
        json.dumps(artifacts["sample_acceptance_report"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["sample_acceptance_md"].write_text(
        openssl_trace_sample_acceptance_report_markdown(artifacts["sample_acceptance_report"]),
        encoding="utf-8",
    )
    paths["summary_json"].write_text(
        json.dumps(_summary_without_artifacts(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["summary_md"].write_text(openssl_instrumentation_chain_markdown(report), encoding="utf-8")
    bundle_manifest = build_openssl_instrumentation_bundle_manifest(
        contract=artifacts["trace_contract"],
        bundle_dir=output_dir,
    )
    write_openssl_instrumentation_bundle_manifest_json(paths["bundle_manifest_json"], bundle_manifest)
    write_openssl_instrumentation_bundle_manifest_markdown(paths["bundle_manifest_md"], bundle_manifest)
    return paths | {f"event_emitter_self_check_{key}": value for key, value in self_check_paths.items()}


def openssl_instrumentation_chain_markdown(report: dict[str, Any]) -> str:
    """Render the dry-run chain summary as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Instrumentation Dry-Run Chain",
        "",
        f"- Status: `{report['status']}`",
        f"- Experiment: `{report['experiment_id']}`",
        f"- Target: `{report['target']}`",
        f"- Target version: `{report['target_version']}`",
        f"- Source pin: `{report['source_pin']}`",
        f"- Build ID: `{report['build_id']}`",
        f"- Execution allowed: `{str(report['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(report['source_mutation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(report['patch_application_allowed']).lower()}`",
        f"- Compile allowed: `{str(report['compile_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(report['raw_secret_capture_allowed']).lower()}`",
        f"- Trace collection mode: `{report['trace_collection_mode']}`",
        "",
        "## Stage Status",
        "",
        f"- Instrumentation stub: `{report['stub_status']}`",
        f"- Source edit proposal: `{report['source_edit_status']}`",
        f"- Event emitter artifact: `{report['event_emitter_status']}`",
        f"- Event emitter self-check: `{report['emitter_self_check_status']}`",
        f"- Event stream: `{report['event_stream_status']}`",
        f"- Sample acceptance: `{report['sample_acceptance_status']}`",
        "",
        "## Counts",
        "",
        f"- Planned events: `{report['planned_event_count']}`",
        f"- Source edit proposals: `{report['proposal_count']}`",
        f"- Emitter files: `{report['emitter_file_count']}`",
        f"- Self-check runs: `{report['self_check_run_count']}`",
        f"- Self-check events: `{report['self_check_event_count']}`",
        f"- Runs: `{report['run_count']}`",
        f"- Events: `{report['event_count']}`",
        f"- Records: `{report['record_count']}`",
        f"- Features: `{report['feature_count']}`",
        "",
        "## Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in report["notes"])
    lines.append("")
    return "\n".join(lines)


def _summary_without_artifacts(report: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in report.items() if key != "artifacts"}

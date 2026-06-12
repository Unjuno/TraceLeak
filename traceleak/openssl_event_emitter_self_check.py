"""Self-check OpenSSL redacted event emitter artifacts against downstream gates.

The self-check generates a deterministic, public-safe JSONL stream from the
reviewed emitter artifact metadata, then validates the stream and resulting
model_sequence.v1 sample. It does not build, run, instrument, patch, compile, or
trace OpenSSL.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from traceleak.openssl_event_emitter_artifact import validate_openssl_event_emitter_artifact
from traceleak.openssl_trace_acceptance import (
    openssl_trace_sample_acceptance_report_dict,
    openssl_trace_sample_acceptance_report_markdown,
)
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, validate_openssl_trace_contract
from traceleak.openssl_trace_event_stream import (
    openssl_redacted_event_stream_report_dict,
    openssl_redacted_event_stream_report_markdown,
    validate_openssl_redacted_event_stream,
)
from traceleak.openssl_trace_sample_builder import build_openssl_model_sequence_sample, write_model_sequence_sample


class OpenSSLEventEmitterSelfCheckError(ValueError):
    """Raised when event emitter self-check generation or validation fails."""


def run_openssl_event_emitter_self_check(
    *,
    contract: dict[str, Any],
    emitter_artifact: dict[str, Any],
    run_count: int = 4,
) -> dict[str, Any]:
    """Generate and validate self-check outputs for a redacted emitter artifact."""

    try:
        validate_openssl_trace_contract(contract)
        validate_openssl_event_emitter_artifact(emitter_artifact)
    except (OpenSSLTraceContractError, ValueError) as exc:
        raise OpenSSLEventEmitterSelfCheckError(str(exc)) from exc
    if run_count <= 0:
        raise OpenSSLEventEmitterSelfCheckError("run_count must be positive")
    label_key = _single_allowed_label_key(contract)
    runs = _self_check_runs(
        contract=contract,
        emitter_artifact=emitter_artifact,
        label_key=label_key,
        run_count=run_count,
    )
    try:
        validate_openssl_redacted_event_stream(contract, runs)
        event_stream_report = openssl_redacted_event_stream_report_dict(contract, runs)
        sample = build_openssl_model_sequence_sample(
            contract=contract,
            runs=runs,
            input_name="openssl_event_emitter_self_check.jsonl",
        )
        sample_acceptance_report = openssl_trace_sample_acceptance_report_dict(contract, sample)
    except ValueError as exc:
        raise OpenSSLEventEmitterSelfCheckError(str(exc)) from exc
    return {
        "report_type": "openssl_event_emitter_self_check_report",
        "status": "emitter_self_check_passed",
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
        "emitter_status": emitter_artifact["status"],
        "event_stream_status": event_stream_report["status"],
        "sample_acceptance_status": sample_acceptance_report["status"],
        "run_count": event_stream_report["run_count"],
        "event_count": event_stream_report["event_count"],
        "record_count": sample_acceptance_report["record_count"],
        "feature_count": sample_acceptance_report["feature_count"],
        "artifacts": {
            "event_stream_runs": runs,
            "event_stream_report": event_stream_report,
            "model_sequence_sample": sample,
            "sample_acceptance_report": sample_acceptance_report,
        },
        "notes": [
            "Self-check data is generated from the reviewed emitter artifact metadata.",
            "It validates output shape only; it is not proof of an actual OpenSSL run.",
        ],
    }


def write_openssl_event_emitter_self_check_outputs(out_dir: str | Path, report: dict[str, Any]) -> dict[str, Path]:
    """Write self-check JSONL, reports, and model-sequence sample."""

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = report["artifacts"]
    paths = {
        "summary_json": output_dir / "openssl_event_emitter_self_check_summary.json",
        "summary_md": output_dir / "openssl_event_emitter_self_check_summary.md",
        "event_stream_jsonl": output_dir / "openssl_event_emitter_self_check_events.jsonl",
        "event_stream_json": output_dir / "openssl_event_emitter_self_check_event_stream_report.json",
        "event_stream_md": output_dir / "openssl_event_emitter_self_check_event_stream_report.md",
        "model_sequence_sample_json": output_dir / "openssl_event_emitter_self_check_model_sequence_sample.json",
        "sample_acceptance_json": output_dir / "openssl_event_emitter_self_check_acceptance_report.json",
        "sample_acceptance_md": output_dir / "openssl_event_emitter_self_check_acceptance_report.md",
    }
    paths["event_stream_jsonl"].write_text(_runs_jsonl(artifacts["event_stream_runs"]), encoding="utf-8")
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
    paths["summary_md"].write_text(openssl_event_emitter_self_check_markdown(report), encoding="utf-8")
    return paths


def openssl_event_emitter_self_check_markdown(report: dict[str, Any]) -> str:
    """Render an emitter self-check summary as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Event Emitter Self-Check",
        "",
        f"- Status: `{report['status']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Target: `{report['target']}`",
        f"- Target version: `{report['target_version']}`",
        f"- Source pin: `{report['source_pin']}`",
        f"- Build ID: `{report['build_id']}`",
        f"- Execution allowed: `{str(report['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(report['source_mutation_allowed']).lower()}`",
        f"- Compile allowed: `{str(report['compile_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(report['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Stage Status",
        "",
        f"- Emitter artifact: `{report['emitter_status']}`",
        f"- Event stream: `{report['event_stream_status']}`",
        f"- Sample acceptance: `{report['sample_acceptance_status']}`",
        "",
        "## Counts",
        "",
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


def _self_check_runs(
    *,
    contract: dict[str, Any],
    emitter_artifact: dict[str, Any],
    label_key: str,
    run_count: int,
) -> list[dict[str, Any]]:
    disallowed_fields = set(contract["safety"]["disallowed_fields"])
    payloads = emitter_artifact["planned_event_payloads"]
    runs: list[dict[str, Any]] = []
    for run_index in range(run_count):
        events = [
            _event_from_payload(
                payload=payload,
                step=step,
                run_index=run_index,
                disallowed_fields=disallowed_fields,
            )
            for step, payload in enumerate(payloads)
        ]
        runs.append(
            {
                "run_id": f"openssl_emitter_self_check_{run_index + 1:06d}",
                "target": contract["target"],
                "target_version": contract["target_version"],
                "view": "redacted",
                "labels_lab_only": {label_key: str(run_index % 2)},
                "metadata": {
                    "source_pin": contract["source_pin"],
                    "build_id": contract["build_id"],
                    "trace_collection_mode": "redacted",
                    "raw_secret_captured": False,
                    "public_safe": True,
                    "generated_by": "openssl_event_emitter_self_check",
                },
                "events": events,
            }
        )
    return runs


def _event_from_payload(
    *,
    payload: dict[str, Any],
    step: int,
    run_index: int,
    disallowed_fields: set[str],
) -> dict[str, Any]:
    safe_group = _safe_token(payload["group_id"], disallowed_fields)
    value_name = _safe_redacted_value_name(payload["redacted_values"][0], disallowed_fields)
    return {
        "step": step,
        "phase": safe_group,
        "function": payload["anchor_symbol"],
        "event_type": payload["event_type"],
        "name": f"{safe_group}_event",
        "file": payload["target_path"],
        "line": payload["anchor_line"],
        "metadata": {"event_group_id": payload["group_id"]},
        "value_redacted": {value_name: run_index + step + 1},
    }


def _safe_redacted_value_name(value_name: str, disallowed_fields: set[str]) -> str:
    safe = _safe_token(value_name, disallowed_fields)
    return safe if safe.endswith("_bucket") else f"{safe}_bucket"


def _safe_token(value: str, disallowed_fields: set[str]) -> str:
    lowered = re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")
    if not lowered:
        return "redacted_event"
    safe = lowered
    for field in sorted(disallowed_fields, key=len, reverse=True):
        field_lower = field.lower()
        if len(field_lower) <= 2:
            safe = re.sub(rf"(^|_){re.escape(field_lower)}($|_)", "_", safe)
        else:
            safe = safe.replace(field_lower, "redacted")
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "redacted_event"


def _runs_jsonl(runs: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(run, sort_keys=True) + "\n" for run in runs)


def _single_allowed_label_key(contract: dict[str, Any]) -> str:
    labels = contract["labels"]["allowed_label_keys"]
    if len(labels) != 1:
        raise OpenSSLEventEmitterSelfCheckError("self-check requires exactly one allowed label key")
    return str(labels[0])


def _summary_without_artifacts(report: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in report.items() if key != "artifacts"}

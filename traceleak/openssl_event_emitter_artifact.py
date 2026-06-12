"""Generate reviewable OpenSSL redacted event emitter artifacts.

The generated C header/source text defines a local JSONL emitter contract for
redacted TraceLeak events. The artifacts are review inputs only: this module does
not patch, build, run, instrument, or trace OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_instrumentation_stub import validate_openssl_instrumentation_stub
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, validate_openssl_trace_contract

EMITTER_ARTIFACT_FORMAT = "traceleak.openssl_event_emitter_artifact.v1"
HEADER_FILENAME = "traceleak_openssl_event.h"
SOURCE_FILENAME = "traceleak_openssl_event.c"
FORBIDDEN_SOURCE_TERMS = {
    "private_key",
    "raw_bignum",
    "prime_candidate",
    "rng_state",
    "value_raw",
}


class OpenSSLEventEmitterArtifactError(ValueError):
    """Raised when redacted emitter artifacts are invalid."""


def build_openssl_event_emitter_artifact(
    *,
    contract: dict[str, Any],
    instrumentation_stub: dict[str, Any],
) -> dict[str, Any]:
    """Build reviewable C emitter artifacts from an OpenSSL trace contract and stub spec."""

    try:
        validate_openssl_trace_contract(contract)
    except OpenSSLTraceContractError as exc:
        raise OpenSSLEventEmitterArtifactError(str(exc)) from exc
    validate_openssl_instrumentation_stub(instrumentation_stub)
    planned_payloads = [_planned_payload(event) for event in instrumentation_stub["planned_events"]]
    artifact = {
        "format": EMITTER_ARTIFACT_FORMAT,
        "status": "emitter_artifact_ready_not_applied",
        "contract_id": contract["contract_id"],
        "target": contract["target"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_collection_mode": "redacted",
        "public_safe": True,
        "emitter_api": {
            "function": "traceleak_event",
            "header": HEADER_FILENAME,
            "source": SOURCE_FILENAME,
            "payload_kind": "jsonl_redacted_trace_event",
            "value_field": "value_redacted",
            "raw_value_field_allowed": False,
        },
        "planned_event_groups": [payload["group_id"] for payload in planned_payloads],
        "planned_event_payloads": planned_payloads,
        "files": {
            HEADER_FILENAME: _header_text(),
            SOURCE_FILENAME: _source_text(),
        },
        "notes": [
            "Artifacts are review-only and are not applied to an OpenSSL worktree by this generator.",
            "The emitter writes redacted JSONL events and has no raw value parameter.",
            "Caller code must pass only bucketed/redacted values such as count_bucket names.",
        ],
    }
    validate_openssl_event_emitter_artifact(artifact)
    return artifact


def validate_openssl_event_emitter_artifact(artifact: dict[str, Any]) -> None:
    """Validate generated redacted event emitter artifacts."""

    _require_equal(artifact.get("format"), EMITTER_ARTIFACT_FORMAT, "format")
    _require_equal(artifact.get("status"), "emitter_artifact_ready_not_applied", "status")
    _require_equal(artifact.get("execution_allowed"), False, "execution_allowed")
    _require_equal(artifact.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(artifact.get("compile_allowed"), False, "compile_allowed")
    _require_equal(artifact.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(artifact.get("trace_collection_mode"), "redacted", "trace_collection_mode")
    _require_equal(artifact.get("public_safe"), True, "public_safe")
    _require_string(artifact.get("contract_id"), "contract_id")
    _require_string(artifact.get("target"), "target")
    _require_string(artifact.get("source_pin"), "source_pin")
    _validate_emitter_api(_require_object(artifact.get("emitter_api"), "emitter_api"))
    files = _require_object(artifact.get("files"), "files")
    header = _require_string(files.get(HEADER_FILENAME), f"files.{HEADER_FILENAME}")
    source = _require_string(files.get(SOURCE_FILENAME), f"files.{SOURCE_FILENAME}")
    groups = _validate_string_list(artifact.get("planned_event_groups"), "planned_event_groups", min_items=1)
    payloads = _require_list(artifact.get("planned_event_payloads"), "planned_event_payloads", min_items=1)
    if len(payloads) != len(groups):
        raise OpenSSLEventEmitterArtifactError("planned_event_payloads length must match planned_event_groups")
    for index, payload in enumerate(payloads):
        _validate_planned_payload(payload, index=index)
        if payload["group_id"] != groups[index]:
            raise OpenSSLEventEmitterArtifactError("planned_event_payloads order must match planned_event_groups")
    _reject_forbidden_source_terms(header, name=HEADER_FILENAME)
    _reject_forbidden_source_terms(source, name=SOURCE_FILENAME)
    if "value_raw" in header or "value_raw" in source:
        raise OpenSSLEventEmitterArtifactError("emitter artifacts must not mention value_raw")
    if "value_redacted" not in header or "value_redacted" not in source:
        raise OpenSSLEventEmitterArtifactError("emitter artifacts must include value_redacted")
    if "traceleak_event" not in header or "traceleak_event" not in source:
        raise OpenSSLEventEmitterArtifactError("emitter artifacts must define traceleak_event")
    if "tl_write_json_string" not in source:
        raise OpenSSLEventEmitterArtifactError("emitter source must define tl_write_json_string")
    if "%s" in source:
        raise OpenSSLEventEmitterArtifactError("emitter source must not interpolate JSON strings with %s")


def write_openssl_event_emitter_artifact_json(path: str | Path, artifact: dict[str, Any]) -> None:
    """Write the combined emitter artifact JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_event_emitter_artifact_files(directory: str | Path, artifact: dict[str, Any]) -> None:
    """Write generated C header/source files into a review directory."""

    validate_openssl_event_emitter_artifact(artifact)
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in artifact["files"].items():
        (output_dir / filename).write_text(content, encoding="utf-8")


def openssl_event_emitter_artifact_markdown(artifact: dict[str, Any]) -> str:
    """Render a redacted event emitter artifact report."""

    validate_openssl_event_emitter_artifact(artifact)
    lines = [
        "# TraceLeak OpenSSL Redacted Event Emitter Artifact",
        "",
        f"- Status: `{artifact['status']}`",
        f"- Contract: `{artifact['contract_id']}`",
        f"- Target: `{artifact['target']}`",
        f"- Target version: `{artifact['target_version']}`",
        f"- Source pin: `{artifact['source_pin']}`",
        f"- Build ID: `{artifact['build_id']}`",
        f"- Execution allowed: `{str(artifact['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(artifact['source_mutation_allowed']).lower()}`",
        f"- Compile allowed: `{str(artifact['compile_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(artifact['raw_secret_capture_allowed']).lower()}`",
        f"- Emitter: `{artifact['emitter_api']['function']}`",
        f"- Header: `{artifact['emitter_api']['header']}`",
        f"- Source: `{artifact['emitter_api']['source']}`",
        "",
        "## Planned Event Groups",
        "",
    ]
    lines.extend(f"- `{group}`" for group in artifact["planned_event_groups"])
    lines.extend(["", "## Planned Event Payloads", ""])
    lines.extend(
        "- `{group}` -> `{event_type}` `{target_path}:{anchor_line}`".format(
            group=payload["group_id"],
            event_type=payload["event_type"],
            target_path=payload["target_path"],
            anchor_line=payload["anchor_line"],
        )
        for payload in artifact["planned_event_payloads"]
    )
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in artifact["notes"])
    lines.append("")
    return "\n".join(lines)


def write_openssl_event_emitter_artifact_markdown(path: str | Path, artifact: dict[str, Any]) -> None:
    """Write a redacted event emitter artifact report."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(openssl_event_emitter_artifact_markdown(artifact), encoding="utf-8")


def _planned_payload(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "group_id": event["group_id"],
        "target_path": event["target_path"],
        "anchor_symbol": event["anchor_symbol"],
        "anchor_line": event["anchor_line"],
        "event_type": event["event_type"],
        "redacted_values": list(event["redacted_values"]),
        "manual_review_required": True,
    }


def _header_text() -> str:
    return """#ifndef TRACELEAK_OPENSSL_EVENT_H
#define TRACELEAK_OPENSSL_EVENT_H

#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * TraceLeak redacted event emitter.
 * Review-only contract: callers must pass only public metadata and bucketed
 * value_redacted names. Raw values and key material are not parameters.
 */
void traceleak_event(FILE *out,
                     const char *run_id,
                     const char *target,
                     const char *target_version,
                     const char *source_pin,
                     const char *build_id,
                     int step,
                     const char *phase,
                     const char *function_name,
                     const char *event_type,
                     const char *name,
                     const char *file_name,
                     int line,
                     const char *value_redacted_key,
                     int value_redacted_bucket,
                     const char *label_key,
                     const char *label_value);

#ifdef __cplusplus
}
#endif

#endif /* TRACELEAK_OPENSSL_EVENT_H */
"""


def _source_text() -> str:
    return r"""#include "traceleak_openssl_event.h"

#include <stdio.h>

static const char *tl_safe(const char *value)
{
    return value == NULL ? "" : value;
}

static void tl_write_json_string(FILE *out, const char *value)
{
    const unsigned char *cursor = (const unsigned char *)tl_safe(value);

    fputc('"', out);
    while (*cursor != '\0') {
        switch (*cursor) {
        case '"':
            fputs("\\\"", out);
            break;
        case '\\':
            fputs("\\\\", out);
            break;
        case '\b':
            fputs("\\b", out);
            break;
        case '\f':
            fputs("\\f", out);
            break;
        case '\n':
            fputs("\\n", out);
            break;
        case '\r':
            fputs("\\r", out);
            break;
        case '\t':
            fputs("\\t", out);
            break;
        default:
            if (*cursor < 0x20)
                fprintf(out, "\\u%04x", (unsigned int)*cursor);
            else
                fputc((int)*cursor, out);
            break;
        }
        cursor++;
    }
    fputc('"', out);
}

void traceleak_event(FILE *out,
                     const char *run_id,
                     const char *target,
                     const char *target_version,
                     const char *source_pin,
                     const char *build_id,
                     int step,
                     const char *phase,
                     const char *function_name,
                     const char *event_type,
                     const char *name,
                     const char *file_name,
                     int line,
                     const char *value_redacted_key,
                     int value_redacted_bucket,
                     const char *label_key,
                     const char *label_value)
{
    if (out == NULL)
        return;

    fputs("{\"run_id\":", out);
    tl_write_json_string(out, run_id);
    fputs(",\"target\":", out);
    tl_write_json_string(out, target);
    fputs(",\"target_version\":", out);
    tl_write_json_string(out, target_version);
    fputs(",\"view\":\"redacted\",", out);
    fputs("\"metadata\":{\"source_pin\":", out);
    tl_write_json_string(out, source_pin);
    fputs(",\"build_id\":", out);
    tl_write_json_string(out, build_id);
    fputs(",\"trace_collection_mode\":\"redacted\",", out);
    fputs("\"raw_secret_captured\":false,\"public_safe\":true},", out);
    fputs("\"labels_lab_only\":{", out);
    tl_write_json_string(out, label_key);
    fputc(':', out);
    tl_write_json_string(out, label_value);
    fputs("},\"events\":[{\"step\":", out);
    fprintf(out, "%d", step);
    fputs(",\"phase\":", out);
    tl_write_json_string(out, phase);
    fputs(",\"function\":", out);
    tl_write_json_string(out, function_name);
    fputs(",\"event_type\":", out);
    tl_write_json_string(out, event_type);
    fputs(",\"name\":", out);
    tl_write_json_string(out, name);
    fputs(",\"file\":", out);
    tl_write_json_string(out, file_name);
    fputs(",\"line\":", out);
    fprintf(out, "%d", line);
    fputs(",\"value_redacted\":{", out);
    tl_write_json_string(out, value_redacted_key);
    fputc(':', out);
    fprintf(out, "%d", value_redacted_bucket);
    fputs("}}]}\n", out);
}
"""


def _validate_emitter_api(api: dict[str, Any]) -> None:
    _require_equal(api.get("function"), "traceleak_event", "emitter_api.function")
    _require_equal(api.get("header"), HEADER_FILENAME, "emitter_api.header")
    _require_equal(api.get("source"), SOURCE_FILENAME, "emitter_api.source")
    _require_equal(api.get("payload_kind"), "jsonl_redacted_trace_event", "emitter_api.payload_kind")
    _require_equal(api.get("value_field"), "value_redacted", "emitter_api.value_field")
    _require_equal(api.get("raw_value_field_allowed"), False, "emitter_api.raw_value_field_allowed")


def _validate_planned_payload(payload: Any, *, index: int) -> None:
    if not isinstance(payload, dict):
        raise OpenSSLEventEmitterArtifactError(f"planned_event_payloads[{index}] must be an object")
    _require_string(payload.get("group_id"), f"planned_event_payloads[{index}].group_id")
    _require_string(payload.get("target_path"), f"planned_event_payloads[{index}].target_path")
    _require_string(payload.get("anchor_symbol"), f"planned_event_payloads[{index}].anchor_symbol")
    anchor_line = payload.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLEventEmitterArtifactError(
            f"planned_event_payloads[{index}].anchor_line must be a positive integer"
        )
    _require_string(payload.get("event_type"), f"planned_event_payloads[{index}].event_type")
    _validate_string_list(
        payload.get("redacted_values"),
        f"planned_event_payloads[{index}].redacted_values",
        min_items=1,
    )
    _require_equal(
        payload.get("manual_review_required"),
        True,
        f"planned_event_payloads[{index}].manual_review_required",
    )


def _reject_forbidden_source_terms(content: str, *, name: str) -> None:
    lowered = content.lower()
    for term in FORBIDDEN_SOURCE_TERMS:
        if term in lowered:
            raise OpenSSLEventEmitterArtifactError(f"{name} contains forbidden source term: {term}")


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLEventEmitterArtifactError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLEventEmitterArtifactError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLEventEmitterArtifactError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLEventEmitterArtifactError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLEventEmitterArtifactError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLEventEmitterArtifactError(f"{name} must be {expected!r}")

"""Validate the review gate before OpenSSL patch materialization.

This module validates a human approval record for review-only OpenSSL source edit
slots and emits a preflight gate report. Passing this gate permits preparing patch
material for review, but it still does not permit source mutation, patch application,
compilation, execution, tracing, or raw secret capture.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from traceleak.openssl_human_review_checklist import REQUIRED_CHECK_IDS
from traceleak.openssl_instrumentation_bundle_manifest import BUNDLE_MANIFEST_FORMAT
from traceleak.openssl_source_edit_proposal import validate_openssl_source_edit_proposal

OPENSSL_REVIEW_APPROVAL_RECORD_FORMAT = "traceleak.openssl_review_approval_record.v1"
OPENSSL_PATCH_MATERIALIZATION_PREFLIGHT_GATE_FORMAT = (
    "traceleak.openssl_patch_materialization_preflight_gate.v1"
)
REQUIRED_APPROVAL_GATES = [
    "source_pin_validated",
    "event_map_validated",
    "layout_inspected",
    "patch_plan_reviewed",
    "stub_spec_reviewed",
    "source_edit_proposal_reviewed",
    "bundle_manifest_validated",
    "artifact_digests_matched",
    "all_event_slots_approved",
    "patch_materialization_only",
    "no_source_mutation",
    "no_patch_application",
    "no_compilation",
    "no_execution",
    "no_raw_secret_capture",
]
DISALLOWED_APPROVAL_KEYS = {
    "diff",
    "patch",
    "source_text",
    "insert_text",
    "replacement_text",
    "raw_value",
    "raw_secret_value",
    "private_key_material",
    "bignum_material",
}


class OpenSSLPatchMaterializationGateError(ValueError):
    """Raised when the OpenSSL patch-materialization preflight gate fails."""


def validate_openssl_review_approval_record(
    *,
    source_edit_proposal: dict[str, Any],
    bundle_manifest: dict[str, Any],
    approval_record: dict[str, Any],
) -> None:
    """Validate a completed human approval record for patch materialization only."""

    try:
        validate_openssl_source_edit_proposal(source_edit_proposal)
    except ValueError as exc:
        raise OpenSSLPatchMaterializationGateError(str(exc)) from exc
    _validate_bundle_manifest_static(bundle_manifest)
    _reject_disallowed_keys(approval_record, path="approval_record")
    _require_equal(approval_record.get("format"), OPENSSL_REVIEW_APPROVAL_RECORD_FORMAT, "format")
    _require_equal(approval_record.get("report_type"), "openssl_review_approval_record", "report_type")
    _require_equal(approval_record.get("status"), "review_approved", "status")
    _require_equal(approval_record.get("decision"), "approved", "decision")
    _require_equal(approval_record.get("approval_scope"), "patch_materialization_only", "approval_scope")
    _require_equal(approval_record.get("approval_recorded"), True, "approval_recorded")
    _require_equal(approval_record.get("completed_review_recorded"), True, "completed_review_recorded")
    _require_equal(approval_record.get("patch_materialization_allowed"), True, "patch_materialization_allowed")
    _require_equal(approval_record.get("execution_allowed"), False, "execution_allowed")
    _require_equal(approval_record.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(approval_record.get("diff_generation_allowed"), False, "diff_generation_allowed")
    _require_equal(approval_record.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(approval_record.get("compile_allowed"), False, "compile_allowed")
    _require_equal(approval_record.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(approval_record.get("trace_view"), "redacted", "trace_view")
    _require_equal(approval_record.get("contract_id"), bundle_manifest["contract_id"], "contract_id")
    _require_equal(approval_record.get("source_pin"), bundle_manifest["source_pin"], "source_pin")
    _require_equal(
        approval_record.get("exact_commit_sha"),
        source_edit_proposal["exact_commit_sha"],
        "exact_commit_sha",
    )
    _require_equal(approval_record.get("bundle_sha256"), bundle_manifest["bundle_sha256"], "bundle_sha256")
    _require_equal(
        approval_record.get("artifact_digests"),
        expected_openssl_patch_materialization_artifact_digests(
            source_edit_proposal=source_edit_proposal,
            bundle_manifest=bundle_manifest,
        ),
        "artifact_digests",
    )
    _require_string(approval_record.get("reviewer"), "reviewer")
    _require_iso8601_timestamp(approval_record.get("reviewed_at"), "reviewed_at")
    _validate_approved_proposals(
        source_edit_proposal=source_edit_proposal,
        approval_record=approval_record,
    )
    gates = set(
        _validate_string_list(
            approval_record.get("gates"),
            "gates",
            min_items=len(REQUIRED_APPROVAL_GATES),
        )
    )
    missing_gates = sorted(set(REQUIRED_APPROVAL_GATES) - gates)
    if missing_gates:
        raise OpenSSLPatchMaterializationGateError(f"gates missing: {', '.join(missing_gates)}")


def build_openssl_patch_materialization_preflight_gate(
    *,
    source_edit_proposal: dict[str, Any],
    bundle_manifest: dict[str, Any],
    approval_record: dict[str, Any],
) -> dict[str, Any]:
    """Build a pass report for the OpenSSL patch-materialization preflight gate."""

    validate_openssl_review_approval_record(
        source_edit_proposal=source_edit_proposal,
        bundle_manifest=bundle_manifest,
        approval_record=approval_record,
    )
    gate = {
        "format": OPENSSL_PATCH_MATERIALIZATION_PREFLIGHT_GATE_FORMAT,
        "report_type": "openssl_patch_materialization_preflight_gate",
        "status": "patch_materialization_preflight_passed",
        "decision": "passed",
        "approval_scope": "patch_materialization_only",
        "contract_id": bundle_manifest["contract_id"],
        "source_pin": bundle_manifest["source_pin"],
        "exact_commit_sha": source_edit_proposal["exact_commit_sha"],
        "bundle_sha256": bundle_manifest["bundle_sha256"],
        "artifact_digests": expected_openssl_patch_materialization_artifact_digests(
            source_edit_proposal=source_edit_proposal,
            bundle_manifest=bundle_manifest,
        ),
        "reviewer": approval_record["reviewer"],
        "reviewed_at": approval_record["reviewed_at"],
        "approval_recorded": True,
        "completed_review_recorded": True,
        "approved_proposal_count": len(approval_record["approved_proposals"]),
        "patch_materialization_allowed": True,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "gates": list(REQUIRED_APPROVAL_GATES),
        "notes": [
            "This gate permits patch materialization preparation only after a completed approval record.",
            "It still does not permit source mutation, patch application, compilation, execution, tracing, or raw secret capture.",
        ],
    }
    validate_openssl_patch_materialization_preflight_gate(
        gate=gate,
        source_edit_proposal=source_edit_proposal,
        bundle_manifest=bundle_manifest,
        approval_record=approval_record,
    )
    return gate


def validate_openssl_patch_materialization_preflight_gate(
    *,
    gate: dict[str, Any],
    source_edit_proposal: dict[str, Any],
    bundle_manifest: dict[str, Any],
    approval_record: dict[str, Any],
) -> None:
    """Validate a patch-materialization preflight gate report."""

    validate_openssl_review_approval_record(
        source_edit_proposal=source_edit_proposal,
        bundle_manifest=bundle_manifest,
        approval_record=approval_record,
    )
    _reject_disallowed_keys(gate, path="gate")
    _require_equal(gate.get("format"), OPENSSL_PATCH_MATERIALIZATION_PREFLIGHT_GATE_FORMAT, "format")
    _require_equal(
        gate.get("report_type"),
        "openssl_patch_materialization_preflight_gate",
        "report_type",
    )
    _require_equal(gate.get("status"), "patch_materialization_preflight_passed", "status")
    _require_equal(gate.get("decision"), "passed", "decision")
    _require_equal(gate.get("approval_scope"), "patch_materialization_only", "approval_scope")
    _require_equal(gate.get("contract_id"), bundle_manifest["contract_id"], "contract_id")
    _require_equal(gate.get("source_pin"), bundle_manifest["source_pin"], "source_pin")
    _require_equal(gate.get("exact_commit_sha"), source_edit_proposal["exact_commit_sha"], "exact_commit_sha")
    _require_equal(gate.get("bundle_sha256"), bundle_manifest["bundle_sha256"], "bundle_sha256")
    _require_equal(
        gate.get("artifact_digests"),
        expected_openssl_patch_materialization_artifact_digests(
            source_edit_proposal=source_edit_proposal,
            bundle_manifest=bundle_manifest,
        ),
        "artifact_digests",
    )
    _require_equal(gate.get("reviewer"), approval_record["reviewer"], "reviewer")
    _require_equal(gate.get("reviewed_at"), approval_record["reviewed_at"], "reviewed_at")
    _require_equal(gate.get("approval_recorded"), True, "approval_recorded")
    _require_equal(gate.get("completed_review_recorded"), True, "completed_review_recorded")
    _require_equal(
        gate.get("approved_proposal_count"),
        len(source_edit_proposal["proposals"]),
        "approved_proposal_count",
    )
    _require_equal(gate.get("patch_materialization_allowed"), True, "patch_materialization_allowed")
    _require_equal(gate.get("execution_allowed"), False, "execution_allowed")
    _require_equal(gate.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(gate.get("diff_generation_allowed"), False, "diff_generation_allowed")
    _require_equal(gate.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(gate.get("compile_allowed"), False, "compile_allowed")
    _require_equal(gate.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(gate.get("trace_view"), "redacted", "trace_view")
    gates = set(_validate_string_list(gate.get("gates"), "gates", min_items=len(REQUIRED_APPROVAL_GATES)))
    missing_gates = sorted(set(REQUIRED_APPROVAL_GATES) - gates)
    if missing_gates:
        raise OpenSSLPatchMaterializationGateError(f"gates missing: {', '.join(missing_gates)}")


def expected_openssl_patch_materialization_artifact_digests(
    *,
    source_edit_proposal: dict[str, Any],
    bundle_manifest: dict[str, Any],
) -> dict[str, str]:
    """Return deterministic digests that a valid approval record must bind."""

    return {
        "source_edit_proposal_sha256": _canonical_sha256(source_edit_proposal),
        "bundle_manifest_sha256": _canonical_sha256(bundle_manifest),
        "bundle_sha256": bundle_manifest["bundle_sha256"],
    }


def load_openssl_review_approval_record(path: str | Path) -> dict[str, Any]:
    """Load an OpenSSL review approval record from JSON."""

    return _load_json_object(path, artifact_name="OpenSSL review approval record")


def load_openssl_source_edit_proposal_json(path: str | Path) -> dict[str, Any]:
    """Load an OpenSSL source edit proposal from JSON."""

    return _load_json_object(path, artifact_name="OpenSSL source edit proposal")


def load_openssl_bundle_manifest_json(path: str | Path) -> dict[str, Any]:
    """Load an OpenSSL bundle manifest from JSON."""

    return _load_json_object(path, artifact_name="OpenSSL bundle manifest")


def write_openssl_patch_materialization_preflight_gate_json(
    path: str | Path,
    gate: dict[str, Any],
) -> None:
    """Write a patch-materialization preflight gate JSON report."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_patch_materialization_preflight_gate_markdown(
    path: str | Path,
    gate: dict[str, Any],
) -> None:
    """Write a patch-materialization preflight gate Markdown report."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(openssl_patch_materialization_preflight_gate_markdown(gate), encoding="utf-8")


def openssl_patch_materialization_preflight_gate_markdown(gate: dict[str, Any]) -> str:
    """Render a patch-materialization preflight gate as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Patch Materialization Preflight Gate",
        "",
        f"- Status: `{gate['status']}`",
        f"- Decision: `{gate['decision']}`",
        f"- Approval scope: `{gate['approval_scope']}`",
        f"- Contract: `{gate['contract_id']}`",
        f"- Source pin: `{gate['source_pin']}`",
        f"- Commit: `{gate['exact_commit_sha']}`",
        f"- Bundle SHA-256: `{gate['bundle_sha256']}`",
        f"- Reviewer: `{gate['reviewer']}`",
        f"- Reviewed at: `{gate['reviewed_at']}`",
        f"- Approved proposals: `{gate['approved_proposal_count']}`",
        f"- Patch materialization allowed: `{str(gate['patch_materialization_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(gate['source_mutation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(gate['patch_application_allowed']).lower()}`",
        f"- Compile allowed: `{str(gate['compile_allowed']).lower()}`",
        f"- Execution allowed: `{str(gate['execution_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(gate['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Artifact Digests",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in gate["artifact_digests"].items())
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{item}`" for item in gate["gates"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in gate.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def _validate_bundle_manifest_static(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest, dict):
        raise OpenSSLPatchMaterializationGateError("bundle_manifest must be a JSON object")
    _require_equal(manifest.get("format"), BUNDLE_MANIFEST_FORMAT, "bundle_manifest.format")
    _require_equal(manifest.get("status"), "bundle_manifest_ready", "bundle_manifest.status")
    _require_equal(manifest.get("validation_status"), "bundle_validated", "bundle_manifest.validation_status")
    _require_string(manifest.get("contract_id"), "bundle_manifest.contract_id")
    _require_string(manifest.get("source_pin"), "bundle_manifest.source_pin")
    bundle_sha256 = _require_string(manifest.get("bundle_sha256"), "bundle_manifest.bundle_sha256")
    if len(bundle_sha256) != 64 or any(char not in "0123456789abcdef" for char in bundle_sha256):
        raise OpenSSLPatchMaterializationGateError(
            "bundle_manifest.bundle_sha256 must be a lowercase SHA-256 hex digest"
        )
    _require_equal(manifest.get("execution_allowed"), False, "bundle_manifest.execution_allowed")
    _require_equal(
        manifest.get("source_mutation_allowed"),
        False,
        "bundle_manifest.source_mutation_allowed",
    )
    _require_equal(
        manifest.get("patch_application_allowed"),
        False,
        "bundle_manifest.patch_application_allowed",
    )
    _require_equal(manifest.get("compile_allowed"), False, "bundle_manifest.compile_allowed")
    _require_equal(
        manifest.get("raw_secret_capture_allowed"),
        False,
        "bundle_manifest.raw_secret_capture_allowed",
    )
    _require_equal(manifest.get("trace_collection_mode"), "redacted", "bundle_manifest.trace_collection_mode")


def _validate_approved_proposals(
    *,
    source_edit_proposal: dict[str, Any],
    approval_record: dict[str, Any],
) -> None:
    approved = _require_list(
        approval_record.get("approved_proposals"),
        "approved_proposals",
        min_items=len(source_edit_proposal["proposals"]),
    )
    expected_by_id = {item["proposal_id"]: item for item in source_edit_proposal["proposals"]}
    seen_ids: set[str] = set()
    for index, item in enumerate(approved):
        if not isinstance(item, dict):
            raise OpenSSLPatchMaterializationGateError(
                f"approved_proposals[{index}] must be an object"
            )
        _reject_disallowed_keys(item, path=f"approved_proposals[{index}]")
        proposal_id = _require_string(item.get("proposal_id"), f"approved_proposals[{index}].proposal_id")
        if proposal_id in seen_ids:
            raise OpenSSLPatchMaterializationGateError(f"duplicate approved proposal_id: {proposal_id}")
        seen_ids.add(proposal_id)
        expected = expected_by_id.get(proposal_id)
        if expected is None:
            raise OpenSSLPatchMaterializationGateError(f"unexpected approved proposal_id: {proposal_id}")
        _require_equal(item.get("group_id"), expected["group_id"], f"approved_proposals[{index}].group_id")
        _require_equal(
            item.get("target_path"),
            expected["target_path"],
            f"approved_proposals[{index}].target_path",
        )
        _require_equal(
            item.get("anchor_symbol"),
            expected["anchor_symbol"],
            f"approved_proposals[{index}].anchor_symbol",
        )
        _require_equal(
            item.get("anchor_line"),
            expected["anchor_line"],
            f"approved_proposals[{index}].anchor_line",
        )
        _require_equal(item.get("review_status"), "reviewed", f"approved_proposals[{index}].review_status")
        _require_equal(item.get("decision"), "approved", f"approved_proposals[{index}].decision")
        _validate_check_results(item.get("check_results"), proposal_index=index)
    missing = sorted(set(expected_by_id) - seen_ids)
    extra = sorted(seen_ids - set(expected_by_id))
    if missing:
        raise OpenSSLPatchMaterializationGateError(
            f"approved_proposals missing proposal_id(s): {', '.join(missing)}"
        )
    if extra:
        raise OpenSSLPatchMaterializationGateError(
            f"approved_proposals contain unexpected proposal_id(s): {', '.join(extra)}"
        )


def _validate_check_results(value: Any, *, proposal_index: int) -> None:
    checks = _require_list(
        value,
        f"approved_proposals[{proposal_index}].check_results",
        min_items=len(REQUIRED_CHECK_IDS),
    )
    seen_ids: set[str] = set()
    for check_index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise OpenSSLPatchMaterializationGateError(
                f"approved_proposals[{proposal_index}].check_results[{check_index}] must be an object"
            )
        _reject_disallowed_keys(
            check,
            path=f"approved_proposals[{proposal_index}].check_results[{check_index}]",
        )
        check_id = _require_string(
            check.get("check_id"),
            f"approved_proposals[{proposal_index}].check_results[{check_index}].check_id",
        )
        if check_id in seen_ids:
            raise OpenSSLPatchMaterializationGateError(f"duplicate check_id: {check_id}")
        seen_ids.add(check_id)
        _require_equal(
            check.get("status"),
            "passed",
            f"approved_proposals[{proposal_index}].check_results[{check_index}].status",
        )
        _require_string(
            check.get("comment"),
            f"approved_proposals[{proposal_index}].check_results[{check_index}].comment",
        )
    missing = sorted(set(REQUIRED_CHECK_IDS) - seen_ids)
    if missing:
        raise OpenSSLPatchMaterializationGateError(
            f"approved_proposals[{proposal_index}].check_results missing: {', '.join(missing)}"
        )


def _load_json_object(path: str | Path, *, artifact_name: str) -> dict[str, Any]:
    input_path = Path(path)
    try:
        value = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OpenSSLPatchMaterializationGateError(f"{artifact_name} not found: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise OpenSSLPatchMaterializationGateError(f"invalid JSON in {input_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OpenSSLPatchMaterializationGateError(f"{artifact_name} must be a JSON object")
    return value


def _canonical_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _reject_disallowed_keys(value: Any, *, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(DISALLOWED_APPROVAL_KEYS & set(value))
        if forbidden:
            raise OpenSSLPatchMaterializationGateError(
                f"{path} contains materialized source fields: {', '.join(forbidden)}"
            )
        for key, child in value.items():
            _reject_disallowed_keys(child, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_disallowed_keys(child, path=f"{path}[{index}]")


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLPatchMaterializationGateError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLPatchMaterializationGateError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLPatchMaterializationGateError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLPatchMaterializationGateError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLPatchMaterializationGateError(f"{name} must be {expected!r}")


def _require_iso8601_timestamp(value: Any, name: str) -> None:
    text = _require_string(value, name)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise OpenSSLPatchMaterializationGateError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OpenSSLPatchMaterializationGateError(f"{name} must include a timezone offset")

"""Build a pending approval template for OpenSSL patch materialization.

The template binds the source edit proposal and bundle manifest digests into a
human-review skeleton. It records no approval and does not permit patch
materialization, source mutation, patch application, compilation, execution,
tracing, or raw secret capture.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_human_review_checklist import REQUIRED_CHECK_IDS
from traceleak.openssl_patch_materialization_gate import (
    DISALLOWED_APPROVAL_KEYS,
    OPENSSL_REVIEW_APPROVAL_RECORD_FORMAT,
    REQUIRED_APPROVAL_GATES,
    OpenSSLPatchMaterializationGateError,
    expected_openssl_patch_materialization_artifact_digests,
    load_openssl_bundle_manifest_json,
    load_openssl_source_edit_proposal_json,
)
from traceleak.openssl_source_edit_proposal import validate_openssl_source_edit_proposal

OPENSSL_PATCH_MATERIALIZATION_APPROVAL_TEMPLATE_FORMAT = (
    "traceleak.openssl_patch_materialization_approval_template.v1"
)
REQUIRED_TEMPLATE_GATES = [
    "source_edit_proposal_loaded",
    "bundle_manifest_loaded",
    "artifact_digests_bound",
    "approval_record_skeleton_created",
    "reviewer_left_blank",
    "reviewed_at_left_blank",
    "no_approval_recorded",
    "patch_materialization_not_allowed",
    "no_source_mutation",
    "no_patch_application",
    "no_compilation",
    "no_execution",
    "no_raw_secret_capture",
]


class OpenSSLPatchMaterializationApprovalTemplateError(ValueError):
    """Raised when an OpenSSL patch-materialization approval template is invalid."""


def build_openssl_patch_materialization_approval_template(
    *,
    source_edit_proposal: dict[str, Any],
    bundle_manifest: dict[str, Any],
) -> dict[str, Any]:
    """Build a pending human approval template for patch materialization."""

    _validate_inputs(source_edit_proposal=source_edit_proposal, bundle_manifest=bundle_manifest)
    skeleton = _approval_record_skeleton(
        source_edit_proposal=source_edit_proposal,
        bundle_manifest=bundle_manifest,
    )
    template = {
        "format": OPENSSL_PATCH_MATERIALIZATION_APPROVAL_TEMPLATE_FORMAT,
        "report_type": "openssl_patch_materialization_approval_template",
        "status": "approval_template_ready",
        "decision": "pending",
        "approval_scope": "patch_materialization_only",
        "contract_id": bundle_manifest["contract_id"],
        "source_pin": bundle_manifest["source_pin"],
        "exact_commit_sha": source_edit_proposal["exact_commit_sha"],
        "bundle_sha256": bundle_manifest["bundle_sha256"],
        "artifact_digests": expected_openssl_patch_materialization_artifact_digests(
            source_edit_proposal=source_edit_proposal,
            bundle_manifest=bundle_manifest,
        ),
        "reviewer": "",
        "reviewed_at": "",
        "approval_recorded": False,
        "completed_review_recorded": False,
        "patch_materialization_allowed": False,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "approval_record_skeleton": skeleton,
        "gates": list(REQUIRED_TEMPLATE_GATES),
        "instructions": [
            "This is a pending template, not an approval record.",
            "A reviewer must copy approval_record_skeleton into a separate approval record file before editing it.",
            "Only after human review may status, decision, reviewer, reviewed_at, proposal decisions, and check statuses be changed.",
            "Even a completed approval record may only allow patch materialization; patch application and OpenSSL execution remain forbidden.",
        ],
    }
    validate_openssl_patch_materialization_approval_template(template)
    return template


def build_openssl_patch_materialization_approval_template_from_paths(
    *,
    source_edit_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Load inputs from JSON paths and build a pending approval template."""

    return build_openssl_patch_materialization_approval_template(
        source_edit_proposal=load_openssl_source_edit_proposal_json(source_edit_path),
        bundle_manifest=load_openssl_bundle_manifest_json(manifest_path),
    )


def validate_openssl_patch_materialization_approval_template(template: dict[str, Any]) -> None:
    """Validate that a patch-materialization approval template is still pending."""

    _reject_disallowed_keys(template, path="template")
    _require_equal(
        template.get("format"),
        OPENSSL_PATCH_MATERIALIZATION_APPROVAL_TEMPLATE_FORMAT,
        "format",
    )
    _require_equal(
        template.get("report_type"),
        "openssl_patch_materialization_approval_template",
        "report_type",
    )
    _require_equal(template.get("status"), "approval_template_ready", "status")
    _require_equal(template.get("decision"), "pending", "decision")
    _require_equal(template.get("approval_scope"), "patch_materialization_only", "approval_scope")
    _require_string(template.get("contract_id"), "contract_id")
    _require_string(template.get("source_pin"), "source_pin")
    _require_string(template.get("exact_commit_sha"), "exact_commit_sha")
    _require_sha256(template.get("bundle_sha256"), "bundle_sha256")
    _validate_artifact_digests(template.get("artifact_digests"), bundle_sha256=template["bundle_sha256"])
    _require_equal(template.get("reviewer"), "", "reviewer")
    _require_equal(template.get("reviewed_at"), "", "reviewed_at")
    _require_equal(template.get("approval_recorded"), False, "approval_recorded")
    _require_equal(template.get("completed_review_recorded"), False, "completed_review_recorded")
    _require_equal(
        template.get("patch_materialization_allowed"),
        False,
        "patch_materialization_allowed",
    )
    _require_equal(template.get("execution_allowed"), False, "execution_allowed")
    _require_equal(template.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(template.get("diff_generation_allowed"), False, "diff_generation_allowed")
    _require_equal(template.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(template.get("compile_allowed"), False, "compile_allowed")
    _require_equal(template.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(template.get("trace_view"), "redacted", "trace_view")
    skeleton = _require_dict(template.get("approval_record_skeleton"), "approval_record_skeleton")
    _validate_pending_approval_record_skeleton(
        skeleton,
        parent=template,
    )
    gates = set(_validate_string_list(template.get("gates"), "gates", min_items=len(REQUIRED_TEMPLATE_GATES)))
    missing_gates = sorted(set(REQUIRED_TEMPLATE_GATES) - gates)
    if missing_gates:
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"gates missing: {', '.join(missing_gates)}"
        )


def openssl_patch_materialization_approval_template_markdown(template: dict[str, Any]) -> str:
    """Render a pending patch-materialization approval template as Markdown."""

    validate_openssl_patch_materialization_approval_template(template)
    skeleton = template["approval_record_skeleton"]
    lines = [
        "# TraceLeak OpenSSL Patch Materialization Approval Template",
        "",
        f"- Status: `{template['status']}`",
        f"- Decision: `{template['decision']}`",
        f"- Approval scope: `{template['approval_scope']}`",
        f"- Contract: `{template['contract_id']}`",
        f"- Source pin: `{template['source_pin']}`",
        f"- Commit: `{template['exact_commit_sha']}`",
        f"- Bundle SHA-256: `{template['bundle_sha256']}`",
        f"- Reviewer: `{template['reviewer']}`",
        f"- Reviewed at: `{template['reviewed_at']}`",
        f"- Approval recorded: `{str(template['approval_recorded']).lower()}`",
        f"- Patch materialization allowed: `{str(template['patch_materialization_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(template['source_mutation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(template['patch_application_allowed']).lower()}`",
        f"- Compile allowed: `{str(template['compile_allowed']).lower()}`",
        f"- Execution allowed: `{str(template['execution_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(template['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Artifact Digests",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in template["artifact_digests"].items())
    lines.extend(["", "## Approval Record Skeleton", ""])
    lines.extend(
        [
            f"- Skeleton format: `{skeleton['format']}`",
            f"- Skeleton status: `{skeleton['status']}`",
            f"- Skeleton decision: `{skeleton['decision']}`",
            f"- Skeleton proposal count: `{len(skeleton['approved_proposals'])}`",
            "",
        ]
    )
    for item in skeleton["approved_proposals"]:
        lines.extend(
            [
                f"### `{item['proposal_id']}` / `{item['group_id']}`",
                "",
                f"- Path: `{item['target_path']}`",
                f"- Anchor: `{item['anchor_symbol']}` line `{item['anchor_line']}`",
                f"- Review status: `{item['review_status']}`",
                f"- Decision: `{item['decision']}`",
                "",
            ]
        )
        lines.extend(
            f"- [ ] `{check['check_id']}` — status `{check['status']}`"
            for check in item["check_results"]
        )
        lines.append("")
    lines.extend(["## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in template["gates"])
    lines.extend(["", "## Instructions", ""])
    lines.extend(f"- {instruction}" for instruction in template["instructions"])
    lines.append("")
    return "\n".join(lines)


def write_openssl_patch_materialization_approval_template_json(
    path: str | Path,
    template: dict[str, Any],
) -> None:
    """Write a patch-materialization approval template JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_patch_materialization_approval_template_markdown(
    path: str | Path,
    template: dict[str, Any],
) -> None:
    """Write a patch-materialization approval template Markdown file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        openssl_patch_materialization_approval_template_markdown(template),
        encoding="utf-8",
    )


def _approval_record_skeleton(
    *,
    source_edit_proposal: dict[str, Any],
    bundle_manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "format": OPENSSL_REVIEW_APPROVAL_RECORD_FORMAT,
        "report_type": "openssl_review_approval_record",
        "status": "pending_review",
        "decision": "pending",
        "approval_scope": "patch_materialization_only",
        "contract_id": bundle_manifest["contract_id"],
        "source_pin": bundle_manifest["source_pin"],
        "exact_commit_sha": source_edit_proposal["exact_commit_sha"],
        "bundle_sha256": bundle_manifest["bundle_sha256"],
        "artifact_digests": expected_openssl_patch_materialization_artifact_digests(
            source_edit_proposal=source_edit_proposal,
            bundle_manifest=bundle_manifest,
        ),
        "reviewer": "",
        "reviewed_at": "",
        "approval_recorded": False,
        "completed_review_recorded": False,
        "patch_materialization_allowed": False,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "approved_proposals": [
            _pending_approved_proposal_skeleton(item) for item in source_edit_proposal["proposals"]
        ],
        "gates": list(REQUIRED_APPROVAL_GATES),
        "notes": "Pending skeleton only. Do not treat this object as an approval record until a human reviewer edits and signs it.",
    }


def _pending_approved_proposal_skeleton(proposal: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": proposal["proposal_id"],
        "group_id": proposal["group_id"],
        "target_path": proposal["target_path"],
        "anchor_symbol": proposal["anchor_symbol"],
        "anchor_line": proposal["anchor_line"],
        "review_status": "pending",
        "decision": "pending",
        "check_results": [
            {"check_id": check_id, "status": "pending", "comment": ""}
            for check_id in REQUIRED_CHECK_IDS
        ],
    }


def _validate_inputs(*, source_edit_proposal: dict[str, Any], bundle_manifest: dict[str, Any]) -> None:
    try:
        validate_openssl_source_edit_proposal(source_edit_proposal)
    except ValueError as exc:
        raise OpenSSLPatchMaterializationApprovalTemplateError(str(exc)) from exc
    if not isinstance(bundle_manifest, dict):
        raise OpenSSLPatchMaterializationApprovalTemplateError("bundle_manifest must be a JSON object")
    _require_string(bundle_manifest.get("contract_id"), "bundle_manifest.contract_id")
    _require_string(bundle_manifest.get("source_pin"), "bundle_manifest.source_pin")
    _require_sha256(bundle_manifest.get("bundle_sha256"), "bundle_manifest.bundle_sha256")
    _require_equal(bundle_manifest.get("status"), "bundle_manifest_ready", "bundle_manifest.status")
    _require_equal(
        bundle_manifest.get("validation_status"),
        "bundle_validated",
        "bundle_manifest.validation_status",
    )
    _require_equal(bundle_manifest.get("execution_allowed"), False, "bundle_manifest.execution_allowed")
    _require_equal(
        bundle_manifest.get("patch_application_allowed"),
        False,
        "bundle_manifest.patch_application_allowed",
    )
    _require_equal(
        bundle_manifest.get("raw_secret_capture_allowed"),
        False,
        "bundle_manifest.raw_secret_capture_allowed",
    )


def _validate_pending_approval_record_skeleton(skeleton: dict[str, Any], *, parent: dict[str, Any]) -> None:
    _require_equal(skeleton.get("format"), OPENSSL_REVIEW_APPROVAL_RECORD_FORMAT, "approval_record_skeleton.format")
    _require_equal(
        skeleton.get("report_type"),
        "openssl_review_approval_record",
        "approval_record_skeleton.report_type",
    )
    _require_equal(skeleton.get("status"), "pending_review", "approval_record_skeleton.status")
    _require_equal(skeleton.get("decision"), "pending", "approval_record_skeleton.decision")
    _require_equal(
        skeleton.get("approval_scope"),
        "patch_materialization_only",
        "approval_record_skeleton.approval_scope",
    )
    for field in ["contract_id", "source_pin", "exact_commit_sha", "bundle_sha256", "artifact_digests"]:
        _require_equal(skeleton.get(field), parent[field], f"approval_record_skeleton.{field}")
    _require_equal(skeleton.get("reviewer"), "", "approval_record_skeleton.reviewer")
    _require_equal(skeleton.get("reviewed_at"), "", "approval_record_skeleton.reviewed_at")
    _require_equal(
        skeleton.get("approval_recorded"),
        False,
        "approval_record_skeleton.approval_recorded",
    )
    _require_equal(
        skeleton.get("completed_review_recorded"),
        False,
        "approval_record_skeleton.completed_review_recorded",
    )
    _require_equal(
        skeleton.get("patch_materialization_allowed"),
        False,
        "approval_record_skeleton.patch_materialization_allowed",
    )
    _require_equal(skeleton.get("execution_allowed"), False, "approval_record_skeleton.execution_allowed")
    _require_equal(
        skeleton.get("source_mutation_allowed"),
        False,
        "approval_record_skeleton.source_mutation_allowed",
    )
    _require_equal(
        skeleton.get("diff_generation_allowed"),
        False,
        "approval_record_skeleton.diff_generation_allowed",
    )
    _require_equal(
        skeleton.get("patch_application_allowed"),
        False,
        "approval_record_skeleton.patch_application_allowed",
    )
    _require_equal(skeleton.get("compile_allowed"), False, "approval_record_skeleton.compile_allowed")
    _require_equal(
        skeleton.get("raw_secret_capture_allowed"),
        False,
        "approval_record_skeleton.raw_secret_capture_allowed",
    )
    _require_equal(skeleton.get("trace_view"), "redacted", "approval_record_skeleton.trace_view")
    items = _require_list(skeleton.get("approved_proposals"), "approval_record_skeleton.approved_proposals", min_items=1)
    for index, item in enumerate(items):
        _validate_pending_proposal_skeleton(item, index=index)
    gates = set(
        _validate_string_list(
            skeleton.get("gates"),
            "approval_record_skeleton.gates",
            min_items=len(REQUIRED_APPROVAL_GATES),
        )
    )
    missing_gates = sorted(set(REQUIRED_APPROVAL_GATES) - gates)
    if missing_gates:
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"approval_record_skeleton.gates missing: {', '.join(missing_gates)}"
        )


def _validate_pending_proposal_skeleton(item: Any, *, index: int) -> None:
    record = _require_dict(item, f"approval_record_skeleton.approved_proposals[{index}]")
    _require_string(record.get("proposal_id"), f"approval_record_skeleton.approved_proposals[{index}].proposal_id")
    _require_string(record.get("group_id"), f"approval_record_skeleton.approved_proposals[{index}].group_id")
    _require_string(record.get("target_path"), f"approval_record_skeleton.approved_proposals[{index}].target_path")
    _require_string(record.get("anchor_symbol"), f"approval_record_skeleton.approved_proposals[{index}].anchor_symbol")
    anchor_line = record.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"approval_record_skeleton.approved_proposals[{index}].anchor_line must be a positive integer"
        )
    _require_equal(
        record.get("review_status"),
        "pending",
        f"approval_record_skeleton.approved_proposals[{index}].review_status",
    )
    _require_equal(
        record.get("decision"),
        "pending",
        f"approval_record_skeleton.approved_proposals[{index}].decision",
    )
    checks = _require_list(
        record.get("check_results"),
        f"approval_record_skeleton.approved_proposals[{index}].check_results",
        min_items=len(REQUIRED_CHECK_IDS),
    )
    seen_ids = set()
    for check_index, check in enumerate(checks):
        check_record = _require_dict(
            check,
            f"approval_record_skeleton.approved_proposals[{index}].check_results[{check_index}]",
        )
        check_id = _require_string(
            check_record.get("check_id"),
            f"approval_record_skeleton.approved_proposals[{index}].check_results[{check_index}].check_id",
        )
        seen_ids.add(check_id)
        _require_equal(
            check_record.get("status"),
            "pending",
            f"approval_record_skeleton.approved_proposals[{index}].check_results[{check_index}].status",
        )
        _require_equal(
            check_record.get("comment"),
            "",
            f"approval_record_skeleton.approved_proposals[{index}].check_results[{check_index}].comment",
        )
    missing = sorted(set(REQUIRED_CHECK_IDS) - seen_ids)
    if missing:
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"approval_record_skeleton.approved_proposals[{index}].check_results missing: {', '.join(missing)}"
        )


def _validate_artifact_digests(value: Any, *, bundle_sha256: str) -> None:
    digests = _require_dict(value, "artifact_digests")
    _require_sha256(digests.get("source_edit_proposal_sha256"), "artifact_digests.source_edit_proposal_sha256")
    _require_sha256(digests.get("bundle_manifest_sha256"), "artifact_digests.bundle_manifest_sha256")
    _require_equal(digests.get("bundle_sha256"), bundle_sha256, "artifact_digests.bundle_sha256")


def _reject_disallowed_keys(value: Any, *, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(DISALLOWED_APPROVAL_KEYS & set(value))
        if forbidden:
            raise OpenSSLPatchMaterializationApprovalTemplateError(
                f"{path} contains materialized source fields: {', '.join(forbidden)}"
            )
        for key, child in value.items():
            _reject_disallowed_keys(child, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_disallowed_keys(child, path=f"{path}[{index}]")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLPatchMaterializationApprovalTemplateError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLPatchMaterializationApprovalTemplateError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"{name} must contain at least {min_items} item(s)"
        )
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"{name} must contain only non-empty strings"
        )
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLPatchMaterializationApprovalTemplateError(f"{name} must be a non-empty string")
    return value


def _require_sha256(value: Any, name: str) -> str:
    text = _require_string(value, name)
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise OpenSSLPatchMaterializationApprovalTemplateError(
            f"{name} must be a lowercase SHA-256 hex digest"
        )
    return text


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLPatchMaterializationApprovalTemplateError(f"{name} must be {expected!r}")

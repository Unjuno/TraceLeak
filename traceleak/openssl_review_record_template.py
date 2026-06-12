"""Build a pending human-review record template for OpenSSL event slots.

The record template is empty by design. It records no approval, no completed
review, no source text, no diffs, no source mutation, no compilation, and no
execution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_human_review_checklist import build_openssl_human_review_checklist

OPENSSL_REVIEW_RECORD_TEMPLATE_FORMAT = "traceleak.openssl_review_record_template.v1"
REQUIRED_RECORD_FIELDS = [
    "proposal_id",
    "group_id",
    "review_status",
    "reviewer",
    "reviewed_at",
    "decision",
    "notes",
]
REQUIRED_GATES = [
    "source_pin_validated",
    "event_map_validated",
    "layout_inspected",
    "patch_plan_reviewed",
    "stub_spec_reviewed",
    "event_slot_reviewed",
    "human_review_checklist_created",
    "review_record_pending",
    "no_approval_recorded",
    "no_source_text_generated",
    "no_raw_secret_capture",
]


class OpenSSLReviewRecordTemplateError(ValueError):
    """Raised when a review-record template is invalid."""


def build_openssl_review_record_template(
    *,
    source_pin_path: str | Path,
    event_map_path: str | Path,
) -> dict[str, Any]:
    """Build a pending human-review record template."""

    checklist = build_openssl_human_review_checklist(
        source_pin_path=source_pin_path,
        event_map_path=event_map_path,
    )
    records = []
    for item in checklist["review_items"]:
        records.append(
            {
                "proposal_id": item["proposal_id"],
                "group_id": item["group_id"],
                "target_path": item["target_path"],
                "anchor_symbol": item["anchor_symbol"],
                "anchor_line": item["anchor_line"],
                "review_status": "pending",
                "reviewer": "",
                "reviewed_at": "",
                "decision": "pending",
                "notes": "",
                "check_results": [
                    {"check_id": check["check_id"], "status": "pending", "comment": ""}
                    for check in item["checks"]
                ],
            }
        )
    template = {
        "format": OPENSSL_REVIEW_RECORD_TEMPLATE_FORMAT,
        "report_type": "openssl_review_record_template",
        "status": "review_record_template_ready",
        "experiment_id": checklist["experiment_id"],
        "target_family": checklist["target_family"],
        "exact_commit_sha": checklist["exact_commit_sha"],
        "worktree_path": checklist["worktree_path"],
        "dirty": checklist["dirty"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "compile_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "raw_secret_capture_allowed": False,
        "approval_recorded": False,
        "completed_review_recorded": False,
        "trace_view": "redacted",
        "records": records,
        "gates": list(REQUIRED_GATES),
        "notes": [
            "This artifact is an empty review-record template only.",
            "All records start with decision=pending and review_status=pending.",
            "A completed review must be recorded in a separate artifact after human review.",
        ],
    }
    validate_openssl_review_record_template(template)
    return template


def validate_openssl_review_record_template(template: dict[str, Any]) -> None:
    """Validate a pending human-review record template."""

    _require_equal(template.get("format"), OPENSSL_REVIEW_RECORD_TEMPLATE_FORMAT, "format")
    _require_equal(template.get("report_type"), "openssl_review_record_template", "report_type")
    _require_equal(template.get("status"), "review_record_template_ready", "status")
    _require_equal(template.get("execution_allowed"), False, "execution_allowed")
    _require_equal(template.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(template.get("compile_allowed"), False, "compile_allowed")
    _require_equal(template.get("diff_generation_allowed"), False, "diff_generation_allowed")
    _require_equal(template.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(template.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(template.get("approval_recorded"), False, "approval_recorded")
    _require_equal(template.get("completed_review_recorded"), False, "completed_review_recorded")
    _require_string(template.get("experiment_id"), "experiment_id")
    _require_string(template.get("exact_commit_sha"), "exact_commit_sha")
    records = _require_list(template.get("records"), "records", min_items=1)
    for index, record in enumerate(records):
        _validate_record(record, index=index)
    gates = set(_validate_string_list(template.get("gates"), "gates", min_items=len(REQUIRED_GATES)))
    missing_gates = sorted(set(REQUIRED_GATES) - gates)
    if missing_gates:
        raise OpenSSLReviewRecordTemplateError(f"gates missing: {', '.join(missing_gates)}")


def review_record_template_markdown(template: dict[str, Any]) -> str:
    """Render a pending human-review record template as Markdown."""

    validate_openssl_review_record_template(template)
    lines = [
        "# TraceLeak OpenSSL Review Record Template",
        "",
        f"- Experiment: `{template['experiment_id']}`",
        f"- Target family: `{template['target_family']}`",
        f"- Commit: `{template['exact_commit_sha']}`",
        f"- Worktree: `{template['worktree_path']}`",
        f"- Dirty: `{str(template['dirty']).lower()}`",
        f"- Execution allowed: `{str(template['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(template['source_mutation_allowed']).lower()}`",
        f"- Diff generation allowed: `{str(template['diff_generation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(template['patch_application_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(template['raw_secret_capture_allowed']).lower()}`",
        f"- Approval recorded: `{str(template['approval_recorded']).lower()}`",
        f"- Completed review recorded: `{str(template['completed_review_recorded']).lower()}`",
        "",
        "## Pending Review Records",
        "",
    ]
    for record in template["records"]:
        lines.extend(
            [
                f"### `{record['proposal_id']}` / `{record['group_id']}`",
                "",
                f"- Path: `{record['target_path']}`",
                f"- Anchor: `{record['anchor_symbol']}` line `{record['anchor_line']}`",
                f"- Review status: `{record['review_status']}`",
                f"- Decision: `{record['decision']}`",
                f"- Reviewer: `{record['reviewer']}`",
                f"- Reviewed at: `{record['reviewed_at']}`",
                f"- Notes: `{record['notes']}`",
                "",
            ]
        )
        lines.extend(
            f"- [ ] `{check['check_id']}` — status `{check['status']}`"
            for check in record["check_results"]
        )
        lines.append("")
    lines.extend(["## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in template["gates"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in template.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def write_review_record_template_json(path: str | Path, template: dict[str, Any]) -> None:
    """Write review-record template JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_review_record_template_markdown(path: str | Path, template: dict[str, Any]) -> None:
    """Write review-record template Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(review_record_template_markdown(template), encoding="utf-8")


def _validate_record(record: Any, *, index: int) -> None:
    if not isinstance(record, dict):
        raise OpenSSLReviewRecordTemplateError(f"records[{index}] must be an object")
    missing_fields = sorted(set(REQUIRED_RECORD_FIELDS) - set(record))
    if missing_fields:
        raise OpenSSLReviewRecordTemplateError(
            f"records[{index}] missing fields: {', '.join(missing_fields)}"
        )
    _require_string(record.get("proposal_id"), f"records[{index}].proposal_id")
    _require_string(record.get("group_id"), f"records[{index}].group_id")
    _require_string(record.get("target_path"), f"records[{index}].target_path")
    _require_string(record.get("anchor_symbol"), f"records[{index}].anchor_symbol")
    anchor_line = record.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLReviewRecordTemplateError(
            f"records[{index}].anchor_line must be a positive integer"
        )
    _require_equal(record.get("review_status"), "pending", f"records[{index}].review_status")
    _require_equal(record.get("decision"), "pending", f"records[{index}].decision")
    _require_equal(record.get("reviewer"), "", f"records[{index}].reviewer")
    _require_equal(record.get("reviewed_at"), "", f"records[{index}].reviewed_at")
    _require_equal(record.get("notes"), "", f"records[{index}].notes")
    checks = _require_list(record.get("check_results"), f"records[{index}].check_results", min_items=1)
    for check_index, check in enumerate(checks):
        _validate_check_result(check, record_index=index, check_index=check_index)


def _validate_check_result(check: Any, *, record_index: int, check_index: int) -> None:
    if not isinstance(check, dict):
        raise OpenSSLReviewRecordTemplateError(
            f"records[{record_index}].check_results[{check_index}] must be an object"
        )
    _require_string(check.get("check_id"), f"records[{record_index}].check_results[{check_index}].check_id")
    _require_equal(
        check.get("status"),
        "pending",
        f"records[{record_index}].check_results[{check_index}].status",
    )
    _require_equal(
        check.get("comment"),
        "",
        f"records[{record_index}].check_results[{check_index}].comment",
    )


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLReviewRecordTemplateError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLReviewRecordTemplateError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLReviewRecordTemplateError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLReviewRecordTemplateError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLReviewRecordTemplateError(f"{name} must be {expected!r}")

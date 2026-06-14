"""Review gate before moving beyond Level 6 metadata-profile work."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_derived_metadata_profile_demo_chain import (
    OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT,
    validate_openssl_derived_metadata_profile_demo_summary,
)

LEVEL7_REVIEW_GATE_FORMAT = "traceleak.level7_review_gate.v1"
LEVEL7_REVIEW_GATE_PHASE = "P106"
LEVEL7_PLANNING_CONTRACT_FORMAT = "traceleak.level7_planning_contract.v1"
LEVEL7_PLANNING_CONTRACT_PHASE = "P107"
LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT = "traceleak.level7_artifact_boundary_plan.v1"
LEVEL7_ARTIFACT_BOUNDARY_PLAN_PHASE = "P108"
LEVEL7_REVIEW_CHECKLIST_FORMAT = "traceleak.level7_review_checklist.v1"
LEVEL7_REVIEW_CHECKLIST_PHASE = "P109"
LEVEL7_READINESS_REPORT_PHASE = "P110"
ALLOWED_LEVEL7_REVIEW_DECISIONS = {
    "defer",
    "approve_planning_only",
}
ALLOWED_LEVEL7_PLANNING_TASKS = {
    "metadata_ingress_review",
    "artifact_shape_review",
    "field_allowlist_review",
    "validation_command_review",
    "report_surface_review",
}
FORBIDDEN_LEVEL7_PLANNING_TASKS = {
    "external_build",
    "external_run",
    "source_mutation",
    "patch_materialization",
    "raw_capture_collection",
    "payload_collection",
    "claim_making",
}
ACCEPTED_LEVEL7_ARTIFACT_CLASSES = {
    "profile_json",
    "adapter_input_json",
    "model_sequence_json",
    "baseline_result_json",
    "nn_result_json",
    "summary_json",
    "markdown_report",
}
REJECTED_LEVEL7_ARTIFACT_CLASSES = {
    "source_text",
    "command_transcript",
    "build_log",
    "execution_log",
    "raw_trace_bytes",
    "payload_dump",
    "private_material",
}
REQUIRED_LEVEL7_CHECKLIST_ITEMS = {
    "level6_summary_exists",
    "review_gate_exists",
    "planning_only_decision_explicit",
    "direct_action_disabled",
    "source_mutation_disabled",
    "payload_collection_disabled",
    "claim_disabled",
    "accepted_artifacts_metadata_or_report_only",
    "rejected_artifacts_include_raw_or_sensitive_classes",
    "full_suite_passed_before_next_level",
}


class Level7ReviewGateError(ValueError):
    """Raised when a Level 7 review gate is invalid."""


def build_level7_review_gate(
    *,
    profile_demo_summary: dict[str, Any],
    reviewer: str,
    reviewed_at: str,
    decision: str = "defer",
    rationale: str = "Level 7 requires explicit review before any broader proximity work.",
) -> dict[str, Any]:
    """Build a conservative review gate from a validated Level 6 summary."""

    validate_openssl_derived_metadata_profile_demo_summary(profile_demo_summary)
    _non_empty(reviewer, "reviewer")
    _non_empty(reviewed_at, "reviewed_at")
    _non_empty(rationale, "rationale")
    if decision not in ALLOWED_LEVEL7_REVIEW_DECISIONS:
        raise Level7ReviewGateError("decision is not allowed")
    flags = profile_demo_summary["flags"]
    gate = {
        "format": LEVEL7_REVIEW_GATE_FORMAT,
        "phase": LEVEL7_REVIEW_GATE_PHASE,
        "source_summary_format": profile_demo_summary["format"],
        "source_summary_phase": profile_demo_summary["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "decision": decision,
        "rationale": rationale,
        "level6_status": {
            "profile_to_adapter": profile_demo_summary["bridge_summary"]["profile_to_adapter"],
            "adapter_to_model_sequence": profile_demo_summary["bridge_summary"]["adapter_to_model_sequence"],
            "baseline_generated": profile_demo_summary["bridge_summary"]["baseline_generated"],
            "nn_generated": profile_demo_summary["bridge_summary"]["nn_generated"],
        },
        "safety_flags": {
            "metadata_only": flags["metadata_only"],
            "payload_free": flags["payload_free"],
            "public_safe": flags["public_safe"],
            "payload_inspected": flags["payload_inspected"],
            "openssl_leakage_claim": flags["openssl_leakage_claim"],
        },
        "allowances": {
            "planning_only": decision == "approve_planning_only",
            "direct_action_enabled": False,
            "source_change_enabled": False,
            "payload_collection_enabled": False,
            "claim_enabled": False,
        },
        "requirements_before_next_step": [
            "Preserve metadata-only ingress.",
            "Keep payload collection disabled.",
            "Keep source-change actions disabled.",
            "Keep claims disabled until independently reviewed evidence exists.",
        ],
    }
    validate_level7_review_gate(gate)
    return gate


def build_level7_planning_contract(
    *,
    review_gate: dict[str, Any],
    plan_id: str = "level7-planning-contract",
    tasks: list[str] | None = None,
) -> dict[str, Any]:
    """Build a planning-only contract from an approved Level 7 review gate."""

    validate_level7_review_gate(review_gate)
    _non_empty(plan_id, "plan_id")
    if review_gate["decision"] != "approve_planning_only":
        raise Level7ReviewGateError("review gate must approve planning only")
    if review_gate["allowances"]["planning_only"] is not True:
        raise Level7ReviewGateError("review gate must enable planning_only")
    selected_tasks = tasks or sorted(ALLOWED_LEVEL7_PLANNING_TASKS)
    _validate_level7_planning_tasks(selected_tasks)
    contract = {
        "format": LEVEL7_PLANNING_CONTRACT_FORMAT,
        "phase": LEVEL7_PLANNING_CONTRACT_PHASE,
        "plan_id": plan_id,
        "review_gate_format": review_gate["format"],
        "review_gate_phase": review_gate["phase"],
        "review_decision": review_gate["decision"],
        "tasks": list(selected_tasks),
        "allowed_task_set": sorted(ALLOWED_LEVEL7_PLANNING_TASKS),
        "forbidden_task_set": sorted(FORBIDDEN_LEVEL7_PLANNING_TASKS),
        "allowances": {
            "planning_only": True,
            "direct_action_enabled": False,
            "source_change_enabled": False,
            "payload_collection_enabled": False,
            "claim_enabled": False,
        },
        "notes": [
            "This contract authorizes planning artifact generation only.",
            "It does not authorize broader direct action, source changes, collection, or claims.",
        ],
    }
    validate_level7_planning_contract(contract)
    return contract


def build_level7_artifact_boundary_plan(
    *,
    planning_contract: dict[str, Any],
    output_root: str = "reports/local",
) -> dict[str, Any]:
    """Build a path-only artifact boundary plan from a planning-only contract."""

    validate_level7_planning_contract(planning_contract)
    _relative_report_path(output_root, "output_root")
    plan = {
        "format": LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT,
        "phase": LEVEL7_ARTIFACT_BOUNDARY_PLAN_PHASE,
        "planning_contract_format": planning_contract["format"],
        "planning_contract_phase": planning_contract["phase"],
        "output_root": output_root,
        "accepted_artifact_classes": sorted(ACCEPTED_LEVEL7_ARTIFACT_CLASSES),
        "rejected_artifact_classes": sorted(REJECTED_LEVEL7_ARTIFACT_CLASSES),
        "path_constraints": {
            "must_be_under": output_root,
            "absolute_paths_allowed": False,
            "parent_traversal_allowed": False,
        },
        "content_rules": {
            "path_only_indexing_allowed": True,
            "payload_reading_allowed": False,
            "claim_generation_allowed": False,
        },
        "notes": [
            "This boundary plan is for planning artifacts only.",
            "It allows metadata/report artifact classes and rejects raw or sensitive artifact classes.",
        ],
    }
    validate_level7_artifact_boundary_plan(plan)
    return plan


def build_level7_review_checklist(
    *,
    artifact_boundary_plan: dict[str, Any],
    full_suite_passed: bool = True,
) -> dict[str, Any]:
    """Build a Level 7 local review checklist."""

    validate_level7_artifact_boundary_plan(artifact_boundary_plan)
    checklist = {
        "format": LEVEL7_REVIEW_CHECKLIST_FORMAT,
        "phase": LEVEL7_REVIEW_CHECKLIST_PHASE,
        "artifact_boundary_format": artifact_boundary_plan["format"],
        "items": {
            "level6_summary_exists": True,
            "review_gate_exists": True,
            "planning_only_decision_explicit": True,
            "direct_action_disabled": True,
            "source_mutation_disabled": True,
            "payload_collection_disabled": True,
            "claim_disabled": True,
            "accepted_artifacts_metadata_or_report_only": True,
            "rejected_artifacts_include_raw_or_sensitive_classes": True,
            "full_suite_passed_before_next_level": full_suite_passed,
        },
        "notes": [
            "All checklist items must be true before Level 8 planning begins.",
            "This checklist does not authorize direct action or claims.",
        ],
    }
    validate_level7_review_checklist(checklist)
    return checklist


def render_level7_readiness_report(
    *,
    review_gate: dict[str, Any],
    planning_contract: dict[str, Any],
    artifact_boundary_plan: dict[str, Any],
    checklist: dict[str, Any],
) -> str:
    """Render a Level 7 readiness Markdown report."""

    validate_level7_review_gate(review_gate)
    validate_level7_planning_contract(planning_contract)
    validate_level7_artifact_boundary_plan(artifact_boundary_plan)
    validate_level7_review_checklist(checklist)
    lines = [
        "# Level 7 Readiness Report",
        "",
        f"- Phase: `{LEVEL7_READINESS_REPORT_PHASE}`",
        f"- Review decision: `{review_gate['decision']}`",
        f"- Planning contract: `{planning_contract['format']}`",
        f"- Artifact boundary: `{artifact_boundary_plan['format']}`",
        "",
        "## Level 6 baseline status",
        "",
        "- Profile to adapter: `True`",
        "- Adapter to model-sequence: `True`",
        "- Baseline generated: `True`",
        "- NN generated: `True`",
        "",
        "## Review gate status",
        "",
        f"- planning_only: `{review_gate['allowances']['planning_only']}`",
        f"- direct_action_enabled: `{review_gate['allowances']['direct_action_enabled']}`",
        f"- source_change_enabled: `{review_gate['allowances']['source_change_enabled']}`",
        f"- payload_collection_enabled: `{review_gate['allowances']['payload_collection_enabled']}`",
        f"- claim_enabled: `{review_gate['allowances']['claim_enabled']}`",
        "",
        "## Artifact boundary",
        "",
        f"- Output root: `{artifact_boundary_plan['output_root']}`",
        f"- Path-only indexing allowed: `{artifact_boundary_plan['content_rules']['path_only_indexing_allowed']}`",
        f"- Payload reading allowed: `{artifact_boundary_plan['content_rules']['payload_reading_allowed']}`",
        f"- Claim generation allowed: `{artifact_boundary_plan['content_rules']['claim_generation_allowed']}`",
        "",
        "## Rejected artifact classes",
        "",
    ]
    for artifact_class in artifact_boundary_plan["rejected_artifact_classes"]:
        lines.append(f"- `{artifact_class}`")
    lines.extend(
        [
            "",
            "## Local validation commands",
            "",
            "```powershell",
            "pytest tests/test_level7_review_gate.py",
            "pytest tests/test_level7_planning_contract.py",
            "pytest tests/test_level7_artifact_boundary_plan.py",
            "ruff check .",
            "pytest",
            "```",
            "",
            "## Next-level preconditions",
            "",
        ]
    )
    for key, value in sorted(checklist["items"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "No external execution is authorized.",
            "No source mutation is authorized.",
            "No payload collection is authorized.",
            "No claim is authorized.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    validate_level7_readiness_report(markdown)
    return markdown


def validate_level7_review_gate(gate: dict[str, Any]) -> None:
    """Validate Level 7 review gate shape."""

    if not isinstance(gate, dict):
        raise Level7ReviewGateError("gate must be an object")
    _eq(gate.get("format"), LEVEL7_REVIEW_GATE_FORMAT, "gate.format")
    _eq(gate.get("phase"), LEVEL7_REVIEW_GATE_PHASE, "gate.phase")
    _eq(
        gate.get("source_summary_format"),
        OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT,
        "gate.source_summary_format",
    )
    _eq(gate.get("source_summary_phase"), "P99", "gate.source_summary_phase")
    _non_empty(gate.get("reviewer"), "gate.reviewer")
    _non_empty(gate.get("reviewed_at"), "gate.reviewed_at")
    if gate.get("decision") not in ALLOWED_LEVEL7_REVIEW_DECISIONS:
        raise Level7ReviewGateError("gate.decision is not allowed")
    _non_empty(gate.get("rationale"), "gate.rationale")
    level6_status = gate.get("level6_status")
    if not isinstance(level6_status, dict):
        raise Level7ReviewGateError("gate.level6_status must be an object")
    for key in ["profile_to_adapter", "adapter_to_model_sequence", "baseline_generated", "nn_generated"]:
        _eq(level6_status.get(key), True, f"gate.level6_status.{key}")
    safety_flags = gate.get("safety_flags")
    if not isinstance(safety_flags, dict):
        raise Level7ReviewGateError("gate.safety_flags must be an object")
    for key in ["metadata_only", "payload_free", "public_safe"]:
        _eq(safety_flags.get(key), True, f"gate.safety_flags.{key}")
    _eq(safety_flags.get("payload_inspected"), False, "gate.safety_flags.payload_inspected")
    _eq(safety_flags.get("openssl_leakage_claim"), False, "gate.safety_flags.openssl_leakage_claim")
    allowances = gate.get("allowances")
    if not isinstance(allowances, dict):
        raise Level7ReviewGateError("gate.allowances must be an object")
    if allowances.get("planning_only") not in {True, False}:
        raise Level7ReviewGateError("gate.allowances.planning_only must be boolean")
    for key in [
        "direct_action_enabled",
        "source_change_enabled",
        "payload_collection_enabled",
        "claim_enabled",
    ]:
        _eq(allowances.get(key), False, f"gate.allowances.{key}")
    requirements = gate.get("requirements_before_next_step")
    if not isinstance(requirements, list) or len(requirements) < 4:
        raise Level7ReviewGateError("gate.requirements_before_next_step must list requirements")
    for index, item in enumerate(requirements):
        _non_empty(item, f"gate.requirements_before_next_step[{index}]")


def validate_level7_planning_contract(contract: dict[str, Any]) -> None:
    """Validate a Level 7 planning-only contract."""

    if not isinstance(contract, dict):
        raise Level7ReviewGateError("contract must be an object")
    _eq(contract.get("format"), LEVEL7_PLANNING_CONTRACT_FORMAT, "contract.format")
    _eq(contract.get("phase"), LEVEL7_PLANNING_CONTRACT_PHASE, "contract.phase")
    _non_empty(contract.get("plan_id"), "contract.plan_id")
    _eq(contract.get("review_gate_format"), LEVEL7_REVIEW_GATE_FORMAT, "contract.review_gate_format")
    _eq(contract.get("review_gate_phase"), LEVEL7_REVIEW_GATE_PHASE, "contract.review_gate_phase")
    _eq(contract.get("review_decision"), "approve_planning_only", "contract.review_decision")
    _validate_level7_planning_tasks(contract.get("tasks"))
    _eq(contract.get("allowed_task_set"), sorted(ALLOWED_LEVEL7_PLANNING_TASKS), "contract.allowed_task_set")
    _eq(
        contract.get("forbidden_task_set"),
        sorted(FORBIDDEN_LEVEL7_PLANNING_TASKS),
        "contract.forbidden_task_set",
    )
    allowances = contract.get("allowances")
    if not isinstance(allowances, dict):
        raise Level7ReviewGateError("contract.allowances must be an object")
    _eq(allowances.get("planning_only"), True, "contract.allowances.planning_only")
    for key in [
        "direct_action_enabled",
        "source_change_enabled",
        "payload_collection_enabled",
        "claim_enabled",
    ]:
        _eq(allowances.get(key), False, f"contract.allowances.{key}")
    notes = contract.get("notes")
    if not isinstance(notes, list) or len(notes) < 2:
        raise Level7ReviewGateError("contract.notes must contain at least two notes")
    for index, note in enumerate(notes):
        _non_empty(note, f"contract.notes[{index}]")


def validate_level7_artifact_boundary_plan(plan: dict[str, Any]) -> None:
    """Validate a Level 7 artifact boundary plan."""

    if not isinstance(plan, dict):
        raise Level7ReviewGateError("plan must be an object")
    _eq(plan.get("format"), LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT, "plan.format")
    _eq(plan.get("phase"), LEVEL7_ARTIFACT_BOUNDARY_PLAN_PHASE, "plan.phase")
    _eq(plan.get("planning_contract_format"), LEVEL7_PLANNING_CONTRACT_FORMAT, "plan.planning_contract_format")
    _eq(plan.get("planning_contract_phase"), LEVEL7_PLANNING_CONTRACT_PHASE, "plan.planning_contract_phase")
    _relative_report_path(plan.get("output_root"), "plan.output_root")
    _eq(
        plan.get("accepted_artifact_classes"),
        sorted(ACCEPTED_LEVEL7_ARTIFACT_CLASSES),
        "plan.accepted_artifact_classes",
    )
    _eq(
        plan.get("rejected_artifact_classes"),
        sorted(REJECTED_LEVEL7_ARTIFACT_CLASSES),
        "plan.rejected_artifact_classes",
    )
    constraints = plan.get("path_constraints")
    if not isinstance(constraints, dict):
        raise Level7ReviewGateError("plan.path_constraints must be an object")
    _eq(constraints.get("must_be_under"), plan["output_root"], "plan.path_constraints.must_be_under")
    _eq(constraints.get("absolute_paths_allowed"), False, "plan.path_constraints.absolute_paths_allowed")
    _eq(
        constraints.get("parent_traversal_allowed"),
        False,
        "plan.path_constraints.parent_traversal_allowed",
    )
    content_rules = plan.get("content_rules")
    if not isinstance(content_rules, dict):
        raise Level7ReviewGateError("plan.content_rules must be an object")
    _eq(content_rules.get("path_only_indexing_allowed"), True, "plan.content_rules.path_only_indexing_allowed")
    _eq(content_rules.get("payload_reading_allowed"), False, "plan.content_rules.payload_reading_allowed")
    _eq(content_rules.get("claim_generation_allowed"), False, "plan.content_rules.claim_generation_allowed")


def validate_level7_review_checklist(checklist: dict[str, Any]) -> None:
    """Validate a Level 7 local review checklist."""

    if not isinstance(checklist, dict):
        raise Level7ReviewGateError("checklist must be an object")
    _eq(checklist.get("format"), LEVEL7_REVIEW_CHECKLIST_FORMAT, "checklist.format")
    _eq(checklist.get("phase"), LEVEL7_REVIEW_CHECKLIST_PHASE, "checklist.phase")
    _eq(
        checklist.get("artifact_boundary_format"),
        LEVEL7_ARTIFACT_BOUNDARY_PLAN_FORMAT,
        "checklist.artifact_boundary_format",
    )
    items = checklist.get("items")
    if not isinstance(items, dict):
        raise Level7ReviewGateError("checklist.items must be an object")
    missing = REQUIRED_LEVEL7_CHECKLIST_ITEMS - set(items)
    if missing:
        raise Level7ReviewGateError(f"checklist missing items: {sorted(missing)}")
    for key in sorted(REQUIRED_LEVEL7_CHECKLIST_ITEMS):
        _eq(items.get(key), True, f"checklist.items.{key}")


def validate_level7_readiness_report(markdown: str) -> None:
    """Validate Level 7 readiness Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level7ReviewGateError("markdown must be a newline-terminated string")
    for text in [
        "# Level 7 Readiness Report",
        "## Level 6 baseline status",
        "## Review gate status",
        "## Artifact boundary",
        "## Rejected artifact classes",
        "## Local validation commands",
        "## Next-level preconditions",
        "No external execution is authorized.",
        "No source mutation is authorized.",
        "No payload collection is authorized.",
        "No claim is authorized.",
    ]:
        if text not in markdown:
            raise Level7ReviewGateError(f"missing markdown text: {text}")


def write_level7_review_gate(path: Path, gate: dict[str, Any]) -> None:
    """Write Level 7 review gate JSON."""

    validate_level7_review_gate(gate)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level7_planning_contract(path: Path, contract: dict[str, Any]) -> None:
    """Write Level 7 planning contract JSON."""

    validate_level7_planning_contract(contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level7_artifact_boundary_plan(path: Path, plan: dict[str, Any]) -> None:
    """Write Level 7 artifact boundary plan JSON."""

    validate_level7_artifact_boundary_plan(plan)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level7_review_checklist(path: Path, checklist: dict[str, Any]) -> None:
    """Write Level 7 review checklist JSON."""

    validate_level7_review_checklist(checklist)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checklist, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level7_readiness_report(path: Path, markdown: str) -> None:
    """Write Level 7 readiness Markdown report."""

    validate_level7_readiness_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _validate_level7_planning_tasks(tasks: Any) -> None:
    if not isinstance(tasks, list) or not tasks:
        raise Level7ReviewGateError("tasks must be a non-empty list")
    for task in tasks:
        if task in FORBIDDEN_LEVEL7_PLANNING_TASKS:
            raise Level7ReviewGateError(f"task is forbidden: {task}")
        if task not in ALLOWED_LEVEL7_PLANNING_TASKS:
            raise Level7ReviewGateError(f"task is not allowed: {task}")


def _relative_report_path(value: Any, name: str) -> str:
    text = _non_empty(value, name)
    path = Path(text.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise Level7ReviewGateError(f"{name} must be a safe relative path")
    if path.parts[:2] != ("reports", "local"):
        raise Level7ReviewGateError(f"{name} must be under reports/local")
    return text


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level7ReviewGateError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level7ReviewGateError(f"{name} must be {expected!r}")

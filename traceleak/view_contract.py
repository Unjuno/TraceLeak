"""Input view contract schema v1 for controlled model-view changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from traceleak.program_event_schema import FORBIDDEN_PUBLIC_FIELD_KEYS

VIEW_CONTRACT_FORMAT = "traceleak.view_contract.v1"

ALLOWED_VIEW_LEVELS: set[str] = {
    "event",
    "graph_edge",
    "graph_node",
    "time_step",
    "token",
    "variable",
}

ALLOWED_VIEW_ACTIONS: set[str] = {
    "drop",
    "keep_only",
    "replace_with_bucket",
    "zero",
}

ALLOWED_INPUT_VIEWS: set[str] = {
    "dependency_graph",
    "program_events",
    "variable_state_sequence",
}

VIEW_LEVEL_INPUT_VIEWS: dict[str, set[str]] = {
    "event": {"program_events"},
    "graph_edge": {"dependency_graph"},
    "graph_node": {"dependency_graph"},
    "time_step": {"dependency_graph", "program_events", "variable_state_sequence"},
    "token": {"program_events", "variable_state_sequence"},
    "variable": {"variable_state_sequence"},
}

VIEW_LEVEL_ACTIONS: dict[str, set[str]] = {
    "event": {"drop", "keep_only", "replace_with_bucket", "zero"},
    "graph_edge": {"drop", "keep_only"},
    "graph_node": {"drop", "keep_only", "zero"},
    "time_step": {"drop", "keep_only", "zero"},
    "token": {"drop", "keep_only", "replace_with_bucket", "zero"},
    "variable": {"drop", "keep_only", "replace_with_bucket", "zero"},
}

REQUIRED_VIEW_CONTRACT_FIELDS: tuple[str, ...] = (
    "sample_id",
    "contract_id",
    "view_level",
    "entity_ids",
    "view_action",
    "expected_input_views",
    "metadata",
)


class ViewContractError(ValueError):
    """Raised when an input view contract is invalid."""


@dataclass(frozen=True)
class ViewContract:
    """Validated description of a controlled model input view change."""

    sample_id: str
    contract_id: str
    view_level: str
    entity_ids: list[str]
    view_action: str
    expected_input_views: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "sample_id": self.sample_id,
            "contract_id": self.contract_id,
            "view_level": self.view_level,
            "entity_ids": list(self.entity_ids),
            "view_action": self.view_action,
            "expected_input_views": list(self.expected_input_views),
            "metadata": dict(self.metadata),
        }


def view_contract_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> ViewContract:
    """Validate and convert a dictionary into a ViewContract."""

    validate_view_contract(data, public_safe=public_safe)
    return ViewContract(
        sample_id=data["sample_id"],
        contract_id=data["contract_id"],
        view_level=data["view_level"],
        entity_ids=list(data["entity_ids"]),
        view_action=data["view_action"],
        expected_input_views=list(data["expected_input_views"]),
        metadata=dict(data["metadata"]),
    )


def validate_view_contract(contract: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate one input view contract record."""

    if not isinstance(contract, dict):
        raise ViewContractError("view contract must be an object")
    for field_name in REQUIRED_VIEW_CONTRACT_FIELDS:
        if field_name not in contract:
            raise ViewContractError(f"missing required view contract field: {field_name}")

    _require_non_empty_string(contract["sample_id"], "sample_id")
    _require_non_empty_string(contract["contract_id"], "contract_id")
    view_level = _validate_enum(contract["view_level"], "view_level", ALLOWED_VIEW_LEVELS)
    entity_ids = _require_non_empty_string_list(contract["entity_ids"], "entity_ids")
    view_action = _validate_enum(contract["view_action"], "view_action", ALLOWED_VIEW_ACTIONS)
    if view_action not in VIEW_LEVEL_ACTIONS[view_level]:
        raise ViewContractError(
            _allowed_error(f"view_action for {view_level}", view_action, VIEW_LEVEL_ACTIONS[view_level])
        )

    input_views = _require_non_empty_string_list(contract["expected_input_views"], "expected_input_views")
    for input_view in input_views:
        if input_view not in ALLOWED_INPUT_VIEWS:
            raise ViewContractError(_allowed_error("expected_input_view", input_view, ALLOWED_INPUT_VIEWS))
    required_views = VIEW_LEVEL_INPUT_VIEWS[view_level]
    if not required_views.intersection(input_views):
        raise ViewContractError(
            f"view_level={view_level} requires one of input views: {', '.join(sorted(required_views))}"
        )

    _validate_entity_ids_for_level(view_level, entity_ids)
    _require_object(contract["metadata"], "metadata")
    if public_safe:
        _reject_reserved_public_fields(contract, "contract")


def validate_view_contracts(contracts: list[dict[str, Any]], *, public_safe: bool = True) -> None:
    """Validate a non-empty list of input view contracts."""

    if not isinstance(contracts, list) or not contracts:
        raise ViewContractError("view contracts must be a non-empty list")
    seen_ids: set[str] = set()
    for index, contract in enumerate(contracts):
        try:
            validate_view_contract(contract, public_safe=public_safe)
        except ViewContractError as exc:
            raise ViewContractError(f"contracts[{index}]: {exc}") from exc
        contract_id = str(contract["contract_id"])
        if contract_id in seen_ids:
            raise ViewContractError(f"duplicate contract_id: {contract_id}")
        seen_ids.add(contract_id)


def sort_view_contracts(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return contracts in deterministic order."""

    validate_view_contracts(contracts)
    return sorted(
        contracts,
        key=lambda contract: (
            str(contract["sample_id"]),
            _view_level_sort_rank(str(contract["view_level"])),
            str(contract["contract_id"]),
        ),
    )


def view_contract(
    *,
    sample_id: str,
    contract_id: str,
    view_level: str,
    entity_ids: list[str],
    view_action: str,
    expected_input_views: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one validated input view contract."""

    level = _validate_enum(view_level, "view_level", ALLOWED_VIEW_LEVELS)
    views = sorted(VIEW_LEVEL_INPUT_VIEWS[level]) if expected_input_views is None else list(expected_input_views)
    contract = {
        "sample_id": sample_id,
        "contract_id": contract_id,
        "view_level": level,
        "entity_ids": list(entity_ids),
        "view_action": view_action,
        "expected_input_views": views,
        "metadata": {
            "schema_kind": "view_contract",
            "claim_scope": "local_model_input_change",
            **(metadata or {}),
        },
    }
    validate_view_contract(contract)
    return contract


def _validate_entity_ids_for_level(view_level: str, entity_ids: list[str]) -> None:
    if view_level == "time_step":
        for entity_id in entity_ids:
            if not entity_id.isdigit():
                raise ViewContractError("time_step entity_ids must be non-negative integer strings")
    if view_level == "graph_edge":
        for entity_id in entity_ids:
            if not entity_id.startswith("edge:"):
                raise ViewContractError("graph_edge entity_ids must start with 'edge:'")


def _view_level_sort_rank(view_level: str) -> int:
    order = {
        "token": 0,
        "event": 1,
        "variable": 2,
        "graph_node": 3,
        "graph_edge": 4,
        "time_step": 5,
    }
    return order.get(view_level, len(order))


def _validate_enum(value: Any, name: str, allowed: set[str]) -> str:
    text = _require_non_empty_string(value, name)
    if text not in allowed:
        raise ViewContractError(_allowed_error(name, text, allowed))
    return text


def _require_non_empty_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ViewContractError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ViewContractError(f"{name} must contain only non-empty strings")
    return list(value)


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ViewContractError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ViewContractError(f"{name} must be a non-empty string")
    return value


def _reject_reserved_public_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PUBLIC_FIELD_KEYS:
                raise ViewContractError(f"public-safe view contract contains reserved field: {path}.{key_text}")
            _reject_reserved_public_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_reserved_public_fields(child, f"{path}[{index}]")


def _allowed_error(name: str, value: str, allowed: set[str]) -> str:
    return f"invalid {name}: {value!r}; allowed: {', '.join(sorted(allowed))}"

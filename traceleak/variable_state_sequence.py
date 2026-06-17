"""Variable State Sequence Schema v1 for Deep Program Representation.

This module represents variable reads, writes, and coarse state updates as an
ordered sequence that can later be joined with ProgramEvent records and
DependencyGraph edges.  It is stricter than ProgramEvent about observed values:
public-safe records must not expose observed values for redacted or
secret-derived state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from traceleak.program_event_schema import (
    FORBIDDEN_PUBLIC_FIELD_KEYS,
    ProgramEventSchemaError,
    sort_program_events,
)

VARIABLE_STATE_SEQUENCE_FORMAT = "traceleak.variable_state_sequence.v1"

ALLOWED_STATE_CLASSES: set[str] = {
    "control",
    "metadata",
    "observe",
    "read",
    "unknown",
    "update",
    "write",
}

ALLOWED_TAINT_CLASSES: set[str] = {
    "metadata",
    "observable",
    "public",
    "redacted",
    "secret_derived",
    "unknown",
}

OBSERVED_VALUE_SAFE_TAINT_CLASSES: set[str] = {
    "metadata",
    "observable",
    "public",
}


class VariableStateSequenceError(ValueError):
    """Raised when a variable state record or sequence is invalid."""


@dataclass(frozen=True)
class VariableStateRecord:
    """Normalized state record for one variable at one program timestep."""

    sequence_id: str
    time_step: int
    variable_id: str
    scope: str
    state_class: str
    value_observed: Any = None
    value_bucket: str | None = None
    source_event_id: str = "unknown"
    depends_on: list[str] = field(default_factory=list)
    taint_class: str = "unknown"
    is_secret_derived: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic dictionary representation."""

        return {
            "sequence_id": self.sequence_id,
            "time_step": self.time_step,
            "variable_id": self.variable_id,
            "scope": self.scope,
            "state_class": self.state_class,
            "value_observed": self.value_observed,
            "value_bucket": self.value_bucket,
            "source_event_id": self.source_event_id,
            "depends_on": list(self.depends_on),
            "taint_class": self.taint_class,
            "is_secret_derived": self.is_secret_derived,
            "metadata": dict(self.metadata),
        }


REQUIRED_VARIABLE_STATE_FIELDS: tuple[str, ...] = (
    "sequence_id",
    "time_step",
    "variable_id",
    "scope",
    "state_class",
    "value_observed",
    "value_bucket",
    "source_event_id",
    "depends_on",
    "taint_class",
    "is_secret_derived",
    "metadata",
)


def variable_state_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> VariableStateRecord:
    """Validate and convert a dictionary into a VariableStateRecord dataclass."""

    validate_variable_state_record(data, public_safe=public_safe)
    return VariableStateRecord(
        sequence_id=data["sequence_id"],
        time_step=data["time_step"],
        variable_id=data["variable_id"],
        scope=data["scope"],
        state_class=data["state_class"],
        value_observed=data["value_observed"],
        value_bucket=data["value_bucket"],
        source_event_id=data["source_event_id"],
        depends_on=list(data["depends_on"]),
        taint_class=data["taint_class"],
        is_secret_derived=data["is_secret_derived"],
        metadata=dict(data["metadata"]),
    )


def validate_variable_state_record(record: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate one Variable State Sequence v1 record."""

    if not isinstance(record, dict):
        raise VariableStateSequenceError("variable state record must be an object")
    for field_name in REQUIRED_VARIABLE_STATE_FIELDS:
        if field_name not in record:
            raise VariableStateSequenceError(f"missing required variable state field: {field_name}")

    _require_non_empty_string(record["sequence_id"], "sequence_id")
    if not isinstance(record["time_step"], int) or record["time_step"] < 0:
        raise VariableStateSequenceError("time_step must be a non-negative integer")
    _require_non_empty_string(record["variable_id"], "variable_id")
    _require_non_empty_string(record["scope"], "scope")

    state_class = _require_non_empty_string(record["state_class"], "state_class")
    if state_class not in ALLOWED_STATE_CLASSES:
        raise VariableStateSequenceError(_allowed_error("state_class", state_class, ALLOWED_STATE_CLASSES))

    _validate_observed_value(record["value_observed"])
    if record["value_bucket"] is not None:
        _require_non_empty_string(record["value_bucket"], "value_bucket")
    _require_non_empty_string(record["source_event_id"], "source_event_id")
    _validate_string_list(record["depends_on"], "depends_on")

    taint_class = _require_non_empty_string(record["taint_class"], "taint_class")
    if taint_class not in ALLOWED_TAINT_CLASSES:
        raise VariableStateSequenceError(_allowed_error("taint_class", taint_class, ALLOWED_TAINT_CLASSES))
    if not isinstance(record["is_secret_derived"], bool):
        raise VariableStateSequenceError("is_secret_derived must be a boolean")
    if record["is_secret_derived"] and taint_class != "secret_derived":
        raise VariableStateSequenceError("secret-derived records must use taint_class=secret_derived")
    _validate_object(record["metadata"], "metadata")

    if public_safe:
        _reject_forbidden_public_fields(record, "record")
        _validate_public_safe_value(record)


def validate_variable_state_sequence(
    records: list[dict[str, Any]], *, public_safe: bool = True
) -> None:
    """Validate a non-empty variable state sequence."""

    if not isinstance(records, list) or not records:
        raise VariableStateSequenceError("variable state sequence must be a non-empty list")
    seen_keys: set[tuple[str, int, str, str, str]] = set()
    for index, record in enumerate(records):
        try:
            validate_variable_state_record(record, public_safe=public_safe)
        except VariableStateSequenceError as exc:
            raise VariableStateSequenceError(f"records[{index}]: {exc}") from exc
        key = (
            str(record["sequence_id"]),
            int(record["time_step"]),
            str(record["variable_id"]),
            str(record["state_class"]),
            str(record["source_event_id"]),
        )
        if key in seen_keys:
            raise VariableStateSequenceError("duplicate variable state record key")
        seen_keys.add(key)


def sort_variable_state_sequence(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return state records sorted by sequence/time/variable/state/source event."""

    validate_variable_state_sequence(records)
    return sorted(
        records,
        key=lambda record: (
            str(record["sequence_id"]),
            int(record["time_step"]),
            str(record["variable_id"]),
            str(record["state_class"]),
            str(record["source_event_id"]),
        ),
    )


def variable_state_records_from_program_events(
    events: list[dict[str, Any]],
    *,
    sequence_id: str = "program_event_variable_state_sequence",
) -> list[dict[str, Any]]:
    """Derive coarse read/write state records from ProgramEvent records.

    The helper only uses explicit `variable_reads` and `variable_writes` fields.
    It does not invent hidden dependencies.  For write records, explicit reads
    in the same event are recorded as a coarse local `depends_on` list.
    """

    _require_non_empty_string(sequence_id, "sequence_id")
    state_records: list[dict[str, Any]] = []
    for event in sort_program_events(events):
        try:
            reads = _validate_event_string_list(event.get("variable_reads"), "variable_reads")
            writes = _validate_event_string_list(event.get("variable_writes"), "variable_writes")
        except ProgramEventSchemaError as exc:
            raise VariableStateSequenceError(str(exc)) from exc
        for variable_id in reads:
            state_records.append(
                _record_from_event_variable(
                    event,
                    sequence_id=sequence_id,
                    variable_id=variable_id,
                    state_class="read",
                    depends_on=[],
                )
            )
        for variable_id in writes:
            state_records.append(
                _record_from_event_variable(
                    event,
                    sequence_id=sequence_id,
                    variable_id=variable_id,
                    state_class="write",
                    depends_on=reads,
                )
            )
    if not state_records:
        raise VariableStateSequenceError("program events did not contain variable reads or writes")
    validate_variable_state_sequence(state_records)
    return sort_variable_state_sequence(state_records)


def _record_from_event_variable(
    event: dict[str, Any],
    *,
    sequence_id: str,
    variable_id: str,
    state_class: str,
    depends_on: list[str],
) -> dict[str, Any]:
    taint_class = _taint_class_from_event(event)
    is_secret_derived = taint_class == "secret_derived"
    value_bucket = _value_bucket_from_event(event)
    record = {
        "sequence_id": sequence_id,
        "time_step": event["time_step"],
        "variable_id": variable_id,
        "scope": event["function"],
        "state_class": state_class,
        "value_observed": None,
        "value_bucket": value_bucket,
        "source_event_id": event["event_id"],
        "depends_on": list(depends_on),
        "taint_class": taint_class,
        "is_secret_derived": is_secret_derived,
        "metadata": {
            "derived_from_program_event": True,
            "event_type": event["event_type"],
            "operation": event["operation"],
            "dependency_tags": list(event.get("dependency_tags", [])),
            "value_class": event["value_class"],
        },
    }
    validate_variable_state_record(record)
    return record


def _taint_class_from_event(event: dict[str, Any]) -> str:
    tags = {str(tag).lower() for tag in event.get("dependency_tags", [])}
    value_class = str(event.get("value_class", "unknown"))
    if value_class == "secret_derived" or any("secret" in tag for tag in tags):
        return "secret_derived"
    if value_class in {"redacted", "bucket"}:
        return "redacted"
    if value_class == "metadata":
        return "metadata"
    if value_class == "observable":
        return "observable"
    if value_class == "public":
        return "public"
    return "unknown"


def _value_bucket_from_event(event: dict[str, Any]) -> str | None:
    metadata = event.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("value_bucket"), str):
        return metadata["value_bucket"]
    control_context = event.get("control_context")
    if isinstance(control_context, dict) and isinstance(control_context.get("value_bucket"), str):
        return control_context["value_bucket"]
    return None


def _validate_public_safe_value(record: dict[str, Any]) -> None:
    value_observed = record["value_observed"]
    if value_observed is None:
        return
    taint_class = str(record["taint_class"])
    if taint_class not in OBSERVED_VALUE_SAFE_TAINT_CLASSES:
        raise VariableStateSequenceError(
            "public-safe variable state must not expose observed values for "
            f"taint_class={taint_class}"
        )


def _validate_observed_value(value: Any) -> None:
    if value is None or isinstance(value, bool | int | float | str):
        return
    raise VariableStateSequenceError("value_observed must be null, bool, int, float, or string")


def _validate_string_list(value: Any, name: str) -> None:
    if not isinstance(value, list):
        raise VariableStateSequenceError(f"{name} must be a list")
    if not all(isinstance(item, str) and item for item in value):
        raise VariableStateSequenceError(f"{name} must contain only non-empty strings")


def _validate_event_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list):
        raise ProgramEventSchemaError(f"{name} must be a list")
    if not all(isinstance(item, str) and item for item in value):
        raise ProgramEventSchemaError(f"{name} must contain only non-empty strings")
    return list(value)


def _validate_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VariableStateSequenceError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise VariableStateSequenceError(f"{name} must be a non-empty string")
    return value


def _reject_forbidden_public_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PUBLIC_FIELD_KEYS:
                raise VariableStateSequenceError(
                    f"public-safe variable state must not contain raw field: {path}.{key_text}"
                )
            _reject_forbidden_public_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_public_fields(child, f"{path}[{index}]")


def _allowed_error(name: str, value: str, allowed: set[str]) -> str:
    return f"invalid {name}: {value!r}; allowed: {', '.join(sorted(allowed))}"

"""Program Event Schema v1 for Deep Program Representation.

This module normalizes program execution events before they are converted into
sequence, graph, or hybrid deep-model datasets.  It is intentionally strict
about public-safe event payloads: raw secret-equivalent values and raw capture
fields are rejected by default.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

PROGRAM_EVENT_SCHEMA_FORMAT = "traceleak.program_event.v1"

ALLOWED_EVENT_TYPES: set[str] = {
    "assign",
    "branch",
    "call",
    "compare",
    "counter",
    "crypto",
    "loop",
    "memory",
    "metadata",
    "observable",
    "phase",
    "return",
    "timing",
    "unknown",
}

ALLOWED_OPERATIONS: set[str] = {
    "arithmetic",
    "assign",
    "branch",
    "call",
    "compare",
    "counter",
    "crypto_step",
    "load",
    "loop",
    "memory_access",
    "metadata",
    "observe",
    "phase",
    "return",
    "store",
    "timing_observation",
    "unknown",
}

ALLOWED_VALUE_CLASSES: set[str] = {
    "bucket",
    "metadata",
    "none",
    "observable",
    "public",
    "redacted",
    "secret_derived",
    "unknown",
}

FORBIDDEN_PUBLIC_FIELD_KEYS: set[str] = {
    "build_output",
    "candidate_value",
    "command_text",
    "d",
    "diff_text",
    "dp",
    "dq",
    "drbg_state",
    "execution_output",
    "iqmp",
    "p",
    "payload",
    "prime_candidate",
    "private_key",
    "q",
    "raw_bignum",
    "raw_capture",
    "raw_prime_candidate",
    "raw_secret",
    "rng_output",
    "rng_state",
    "seed",
    "source_text",
    "value_raw",
}


class ProgramEventSchemaError(ValueError):
    """Raised when a program event does not satisfy Program Event Schema v1."""


@dataclass(frozen=True)
class ProgramEvent:
    """Normalized event record consumed by sequence/graph dataset builders."""

    event_id: str
    time_step: int
    event_type: str
    operation: str
    function: str
    source_location: dict[str, Any]
    variable_reads: list[str] = field(default_factory=list)
    variable_writes: list[str] = field(default_factory=list)
    value_class: str = "none"
    dependency_tags: list[str] = field(default_factory=list)
    control_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic dictionary representation."""

        return {
            "event_id": self.event_id,
            "time_step": self.time_step,
            "event_type": self.event_type,
            "operation": self.operation,
            "function": self.function,
            "source_location": dict(self.source_location),
            "variable_reads": list(self.variable_reads),
            "variable_writes": list(self.variable_writes),
            "value_class": self.value_class,
            "dependency_tags": list(self.dependency_tags),
            "control_context": dict(self.control_context),
            "metadata": dict(self.metadata),
        }


REQUIRED_PROGRAM_EVENT_FIELDS: tuple[str, ...] = (
    "event_id",
    "time_step",
    "event_type",
    "operation",
    "function",
    "source_location",
    "variable_reads",
    "variable_writes",
    "value_class",
    "dependency_tags",
    "control_context",
    "metadata",
)


def program_event_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> ProgramEvent:
    """Validate and convert a dictionary into a ProgramEvent dataclass."""

    validate_program_event(data, public_safe=public_safe)
    return ProgramEvent(
        event_id=data["event_id"],
        time_step=data["time_step"],
        event_type=data["event_type"],
        operation=data["operation"],
        function=data["function"],
        source_location=dict(data["source_location"]),
        variable_reads=list(data["variable_reads"]),
        variable_writes=list(data["variable_writes"]),
        value_class=data["value_class"],
        dependency_tags=list(data["dependency_tags"]),
        control_context=dict(data["control_context"]),
        metadata=dict(data["metadata"]),
    )


def validate_program_event(event: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate one Program Event Schema v1 dictionary."""

    if not isinstance(event, dict):
        raise ProgramEventSchemaError("program event must be an object")
    for field_name in REQUIRED_PROGRAM_EVENT_FIELDS:
        if field_name not in event:
            raise ProgramEventSchemaError(f"missing required program event field: {field_name}")

    _require_non_empty_string(event["event_id"], "event_id")
    if not isinstance(event["time_step"], int) or event["time_step"] < 0:
        raise ProgramEventSchemaError("time_step must be a non-negative integer")

    event_type = _require_non_empty_string(event["event_type"], "event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ProgramEventSchemaError(_allowed_error("event_type", event_type, ALLOWED_EVENT_TYPES))

    operation = _require_non_empty_string(event["operation"], "operation")
    if operation not in ALLOWED_OPERATIONS:
        raise ProgramEventSchemaError(_allowed_error("operation", operation, ALLOWED_OPERATIONS))

    _require_non_empty_string(event["function"], "function")
    _validate_source_location(event["source_location"])
    _validate_string_list(event["variable_reads"], "variable_reads")
    _validate_string_list(event["variable_writes"], "variable_writes")

    value_class = _require_non_empty_string(event["value_class"], "value_class")
    if value_class not in ALLOWED_VALUE_CLASSES:
        raise ProgramEventSchemaError(_allowed_error("value_class", value_class, ALLOWED_VALUE_CLASSES))

    _validate_string_list(event["dependency_tags"], "dependency_tags")
    _validate_object(event["control_context"], "control_context")
    _validate_object(event["metadata"], "metadata")

    if public_safe:
        _reject_forbidden_public_fields(event, "event")


def validate_program_events(events: list[dict[str, Any]], *, public_safe: bool = True) -> None:
    """Validate a non-empty list of program events."""

    if not isinstance(events, list) or not events:
        raise ProgramEventSchemaError("program events must be a non-empty list")
    seen_event_ids: set[str] = set()
    for index, event in enumerate(events):
        try:
            validate_program_event(event, public_safe=public_safe)
        except ProgramEventSchemaError as exc:
            raise ProgramEventSchemaError(f"events[{index}]: {exc}") from exc
        event_id = str(event["event_id"])
        if event_id in seen_event_ids:
            raise ProgramEventSchemaError(f"duplicate event_id: {event_id}")
        seen_event_ids.add(event_id)


def sort_program_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return events sorted by `(time_step, event_id)` after validation."""

    validate_program_events(events)
    return sorted(events, key=lambda event: (int(event["time_step"]), str(event["event_id"])))


def program_event_from_legacy_model_step(
    step: dict[str, Any],
    *,
    event_id_prefix: str = "legacy_model_step",
    position: int | None = None,
) -> dict[str, Any]:
    """Convert a legacy `model_features.py` model step into Program Event v1.

    The adapter preserves every legacy token in metadata, but it does not invent
    reads/writes or dependencies that are absent from the legacy step.
    """

    if not isinstance(step, dict):
        raise ProgramEventSchemaError("legacy model step must be an object")
    event_type = str(step.get("event_type", "unknown"))
    phase = str(step.get("phase", "unknown"))
    source_token = str(step.get("source_token", ""))
    parsed_source = _parse_legacy_source_token(source_token)
    function = str(step.get("function") or parsed_source.get("function") or "unknown")
    time_step = _legacy_time_step(step, position=position)
    event_token = str(step.get("event_token") or f"{event_type}:{phase}:{function}:unknown")
    redacted_tokens = _optional_string_list(step.get("redacted_value_tokens"), "redacted_value_tokens")
    value_class = _legacy_value_class(event_type=event_type, redacted_tokens=redacted_tokens)
    source_location = {
        "file": step.get("file", parsed_source.get("file")),
        "line": step.get("line", parsed_source.get("line")),
    }
    metadata = {
        "legacy_model_step": True,
        "legacy_event_token": event_token,
        "legacy_source_token": source_token,
        "legacy_context_token": step.get("context_token"),
        "legacy_name": step.get("name", parsed_source.get("name")),
        "legacy_phase": phase,
        "target": step.get("target"),
        "view": step.get("view"),
        "redacted_value_tokens": redacted_tokens,
    }
    event = {
        "event_id": _stable_legacy_event_id(event_id_prefix, time_step, event_token),
        "time_step": time_step,
        "event_type": event_type if event_type in ALLOWED_EVENT_TYPES else "unknown",
        "operation": _operation_from_legacy_event_type(event_type),
        "function": function,
        "source_location": source_location,
        "variable_reads": _optional_string_list(step.get("variable_reads"), "variable_reads"),
        "variable_writes": _optional_string_list(step.get("variable_writes"), "variable_writes"),
        "value_class": value_class,
        "dependency_tags": _optional_string_list(step.get("dependency_tags"), "dependency_tags"),
        "control_context": {
            "phase": phase,
            "context_token": step.get("context_token"),
        },
        "metadata": {key: value for key, value in metadata.items() if value is not None},
    }
    validate_program_event(event)
    return event


def program_events_from_legacy_model_sequence(sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert an ordered legacy model sequence into Program Event records."""

    if not isinstance(sequence, list) or not sequence:
        raise ProgramEventSchemaError("legacy model sequence must be a non-empty list")
    events = [
        program_event_from_legacy_model_step(step, position=index)
        for index, step in enumerate(sequence, start=1)
    ]
    validate_program_events(events)
    return sort_program_events(events)


def _validate_source_location(value: Any) -> None:
    location = _validate_object(value, "source_location")
    for key in ("file", "function"):
        if key in location and location[key] is not None and not isinstance(location[key], str):
            raise ProgramEventSchemaError(f"source_location.{key} must be a string or null")
    for key in ("line", "column"):
        if (
            key in location
            and location[key] is not None
            and (not isinstance(location[key], int) or location[key] <= 0)
        ):
            raise ProgramEventSchemaError(
                f"source_location.{key} must be a positive integer or null"
            )


def _validate_string_list(value: Any, name: str) -> None:
    if not isinstance(value, list):
        raise ProgramEventSchemaError(f"{name} must be a list")
    if not all(isinstance(item, str) and item for item in value):
        raise ProgramEventSchemaError(f"{name} must contain only non-empty strings")


def _optional_string_list(value: Any, name: str) -> list[str]:
    if value is None:
        return []
    _validate_string_list(value, name)
    return list(value)


def _validate_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProgramEventSchemaError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProgramEventSchemaError(f"{name} must be a non-empty string")
    return value


def _reject_forbidden_public_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PUBLIC_FIELD_KEYS:
                raise ProgramEventSchemaError(
                    f"public-safe program event must not contain raw field: {path}.{key_text}"
                )
            _reject_forbidden_public_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_public_fields(child, f"{path}[{index}]")


def _legacy_time_step(step: dict[str, Any], *, position: int | None) -> int:
    candidate = step.get("step", step.get("position", position))
    if not isinstance(candidate, int) or candidate < 0:
        raise ProgramEventSchemaError("legacy step must contain a non-negative step/position")
    return candidate


def _operation_from_legacy_event_type(event_type: str) -> str:
    mapping = {
        "assign": "assign",
        "branch": "branch",
        "call": "call",
        "compare": "compare",
        "counter": "counter",
        "crypto": "crypto_step",
        "loop": "loop",
        "memory": "memory_access",
        "metadata": "metadata",
        "observable": "observe",
        "phase": "phase",
        "return": "return",
        "timing": "timing_observation",
    }
    return mapping.get(event_type, "unknown")


def _legacy_value_class(*, event_type: str, redacted_tokens: list[str]) -> str:
    if redacted_tokens:
        return "redacted"
    if event_type == "metadata":
        return "metadata"
    if event_type == "observable":
        return "observable"
    return "none"


def _parse_legacy_source_token(source_token: str) -> dict[str, Any]:
    parts = source_token.split(":")
    if len(parts) < 4:
        return {}
    line_text = parts[-3]
    line = int(line_text) if line_text.isdigit() else None
    file_name = ":".join(parts[:-3]) or None
    if file_name == "<unknown>":
        file_name = None
    return {
        "file": file_name,
        "line": line,
        "function": parts[-2] or None,
        "name": parts[-1] or None,
    }


def _stable_legacy_event_id(prefix: str, time_step: int, event_token: str) -> str:
    return f"{_slug(prefix)}:{time_step:06d}:{_slug(event_token)}"


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "unknown"


def _allowed_error(name: str, value: str, allowed: set[str]) -> str:
    return f"invalid {name}: {value!r}; allowed: {', '.join(sorted(allowed))}"

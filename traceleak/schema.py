"""Trace schema primitives and validation.

This module intentionally avoids heavy dependencies. It validates the core
TraceLeak JSON structure before later feature extraction or modeling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

TraceView = Literal["meta", "path", "redacted", "observable", "raw", "cheat"]
EventType = Literal["assign", "branch", "loop", "phase", "memory", "timing"]

ALLOWED_VIEWS: set[str] = {"meta", "path", "redacted", "observable", "raw", "cheat"}
ALLOWED_EVENT_TYPES: set[str] = {"assign", "branch", "loop", "phase", "memory", "timing"}
SECRET_EQUIVALENT_KEYS: set[str] = {
    "p",
    "q",
    "d",
    "private_key",
    "rng_output",
    "drbg_state",
    "raw_prime_candidate",
    "value_raw",
}
PUBLIC_SAFE_VIEWS: set[str] = {"meta", "path", "redacted", "observable"}


class TraceSchemaError(ValueError):
    """Raised when a trace object does not match the TraceLeak schema."""


@dataclass(frozen=True)
class TraceEvent:
    """A single source-level trace event."""

    step: int
    phase: str
    function: str
    event_type: EventType
    name: str
    file: str | None = None
    line: int | None = None
    value_type: str | None = None
    value_raw: Any | None = None
    value_redacted: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceRun:
    """A complete trace run."""

    run_id: str
    target: str
    target_version: str
    view: TraceView
    events: list[TraceEvent]
    labels_lab_only: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


def validate_event(event: dict[str, Any]) -> None:
    """Validate one event dictionary.

    The function raises TraceSchemaError on the first detected issue.
    """

    required = ["step", "phase", "function", "event_type", "name"]
    for key in required:
        if key not in event:
            raise TraceSchemaError(f"missing required event field: {key}")

    if not isinstance(event["step"], int) or event["step"] < 0:
        raise TraceSchemaError("event.step must be a non-negative integer")

    if event["event_type"] not in ALLOWED_EVENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_EVENT_TYPES))
        raise TraceSchemaError(f"invalid event_type: {event['event_type']!r}; allowed: {allowed}")

    if "line" in event and event["line"] is not None:
        if not isinstance(event["line"], int) or event["line"] <= 0:
            raise TraceSchemaError("event.line must be a positive integer when present")


def validate_run(run: dict[str, Any], *, public_export: bool = False) -> None:
    """Validate a TraceLeak run dictionary.

    Args:
        run: Parsed JSON object representing a run.
        public_export: If true, reject raw/cheat views and obvious secret-equivalent fields.
    """

    required = ["run_id", "target", "target_version", "view", "events"]
    for key in required:
        if key not in run:
            raise TraceSchemaError(f"missing required run field: {key}")

    if run["view"] not in ALLOWED_VIEWS:
        allowed = ", ".join(sorted(ALLOWED_VIEWS))
        raise TraceSchemaError(f"invalid view: {run['view']!r}; allowed: {allowed}")

    if not isinstance(run["events"], list):
        raise TraceSchemaError("run.events must be a list")

    if public_export and run["view"] not in PUBLIC_SAFE_VIEWS:
        raise TraceSchemaError(f"view {run['view']!r} is not allowed for public export")

    for event in run["events"]:
        if not isinstance(event, dict):
            raise TraceSchemaError("each event must be an object")
        validate_event(event)
        if public_export:
            _reject_secret_equivalent_fields(event, location="event")

    if public_export:
        _reject_secret_equivalent_fields(run.get("labels_lab_only", {}), location="labels_lab_only")
        _reject_secret_equivalent_fields(run.get("meta", {}), location="meta")


def _reject_secret_equivalent_fields(obj: Any, *, location: str) -> None:
    """Reject obvious secret-equivalent keys recursively."""

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in SECRET_EQUIVALENT_KEYS:
                raise TraceSchemaError(f"secret-equivalent field {key!r} found in {location}")
            _reject_secret_equivalent_fields(value, location=f"{location}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _reject_secret_equivalent_fields(value, location=f"{location}[{index}]")

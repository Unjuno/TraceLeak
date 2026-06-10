"""Trace view transformation helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

from traceleak.schema import TraceSchemaError, validate_run

TargetView = Literal["meta", "path", "redacted"]


def to_view(run: dict[str, Any], view: TargetView) -> dict[str, Any]:
    """Convert a run into a safer view.

    This function is intentionally conservative. It strips lab labels for public-safe
    views and removes raw values unless explicitly operating on the raw input outside
    this helper.
    """

    validate_run(run)
    converted = deepcopy(run)
    converted["view"] = view
    converted.pop("labels_lab_only", None)

    if view == "meta":
        converted["events"] = []
        return converted

    events = []
    for event in converted["events"]:
        if view == "path":
            events.append(_path_event(event))
        elif view == "redacted":
            events.append(_redacted_event(event))
        else:  # pragma: no cover - Literal typing should prevent this.
            raise TraceSchemaError(f"unsupported target view: {view}")

    converted["events"] = events
    validate_run(converted, public_export=True)
    return converted


def _path_event(event: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "step",
        "phase",
        "function",
        "file",
        "line",
        "event_type",
        "name",
    }
    return {key: value for key, value in event.items() if key in keep and value is not None}


def _redacted_event(event: dict[str, Any]) -> dict[str, Any]:
    redacted = _path_event(event)
    if "value_type" in event:
        redacted["value_type"] = event["value_type"]
    if "value_redacted" in event:
        redacted["value_redacted"] = event["value_redacted"]
    return redacted

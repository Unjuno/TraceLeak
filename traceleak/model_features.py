"""Model feature helpers for variable/control-flow dynamics.

This module does not train a neural network. It converts validated TraceLeak
runs into public-safe ordered sequence records that local models can consume.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from traceleak.schema import TraceSchemaError, validate_run

ModelStep = dict[str, Any]
ModelSequence = list[ModelStep]


class ModelFeatureError(ValueError):
    """Raised when model feature extraction input is invalid."""


def trace_to_model_sequence(
    run: dict[str, Any],
    *,
    allow_raw: bool = False,
    include_redacted_values: bool = True,
) -> ModelSequence:
    """Convert one TraceLeak run into ordered model steps.

    The sequence preserves program-order evidence and source-level identities,
    while rejecting raw/cheat views unless explicitly allowed.
    """

    validate_run(run)
    view = run["view"]
    if not allow_raw and view in {"raw", "cheat"}:
        raise ModelFeatureError(f"refusing to encode {view!r} view without allow_raw=True")

    sequence: ModelSequence = []
    for position, event in enumerate(sorted(run["events"], key=lambda item: item["step"]), start=1):
        sequence.append(
            event_to_model_step(
                event,
                position=position,
                target=run["target"],
                view=view,
                include_redacted_values=include_redacted_values,
            )
        )
    return sequence


def event_to_model_step(
    event: dict[str, Any],
    *,
    position: int,
    target: str,
    view: str,
    include_redacted_values: bool = True,
) -> ModelStep:
    """Convert one event dictionary into a source-level model step."""

    event_type = event["event_type"]
    phase = event["phase"]
    function = event["function"]
    name = event["name"]
    file_name = event.get("file") or "<unknown>"
    line = event.get("line")

    step: ModelStep = {
        "position": position,
        "step": event["step"],
        "target": target,
        "view": view,
        "event_type": event_type,
        "phase": phase,
        "function": function,
        "name": name,
        "event_token": event_token(event),
        "source_token": source_token(event),
        "context_token": f"{phase}:{function}",
    }
    if file_name != "<unknown>":
        step["file"] = file_name
    if line is not None:
        step["line"] = line

    if include_redacted_values:
        step["redacted_value_tokens"] = redacted_value_tokens(event)
    return step


def event_token(event: dict[str, Any]) -> str:
    """Return an event identity token."""

    return "{event_type}:{phase}:{function}:{name}".format(
        event_type=event["event_type"],
        phase=event["phase"],
        function=event["function"],
        name=event["name"],
    )


def source_token(event: dict[str, Any]) -> str:
    """Return a source-level identity token."""

    file_name = event.get("file") or "<unknown>"
    line = event.get("line")
    line_token = "?" if line is None else str(line)
    return f"{file_name}:{line_token}:{event['function']}:{event['name']}"


def redacted_value_tokens(event: dict[str, Any]) -> list[str]:
    """Return encoded redacted value tokens for one event."""

    redacted = event.get("value_redacted")
    if redacted is None:
        return []
    if not isinstance(redacted, dict):
        raise TraceSchemaError("event.value_redacted must be an object when present")
    return [f"{key}={_encode_value(value)}" for key, value in _flatten_value("value_redacted", redacted)]


def model_sequence_vocabulary(sequences: Iterable[ModelSequence]) -> list[str]:
    """Build a deterministic token vocabulary from model sequences."""

    tokens: set[str] = set()
    for sequence in sequences:
        for step in sequence:
            tokens.add(step["event_token"])
            tokens.add(step["source_token"])
            tokens.add(step["context_token"])
            tokens.update(step.get("redacted_value_tokens", []))
    return sorted(tokens)


def sequence_token_counts(sequence: ModelSequence) -> dict[str, float]:
    """Collapse a sequence into token counts for lightweight baselines."""

    counts: dict[str, float] = {}
    for step in sequence:
        _add(counts, f"event_token={step['event_token']}")
        _add(counts, f"source_token={step['source_token']}")
        _add(counts, f"context_token={step['context_token']}")
        _add(counts, f"event_type={step['event_type']}")
        _add(counts, f"phase={step['phase']}")
        for token in step.get("redacted_value_tokens", []):
            _add(counts, f"redacted_value={token}")
    return counts


def _flatten_value(prefix: str, value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _flatten_value(f"{prefix}.{key}", child)
    else:
        yield prefix, value


def _encode_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int | float | str):
        return str(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _add(counts: dict[str, float], key: str) -> None:
    counts[key] = counts.get(key, 0.0) + 1.0

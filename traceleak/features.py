"""Lightweight feature extraction for TraceLeak runs.

This module converts validated TraceLeak run dictionaries into sparse numeric
feature vectors. It intentionally avoids NumPy/Pandas/ML dependencies so the
repository remains lightweight. Local NN experiments can consume these vectors
or replace this module with a heavier featurizer.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from traceleak.schema import TraceSchemaError, validate_run

FeatureVector = dict[str, float]


class FeatureExtractionError(ValueError):
    """Raised when feature extraction input is invalid."""


def extract_feature_vector(
    run: dict[str, Any],
    *,
    allow_raw: bool = False,
    include_locations: bool = True,
) -> FeatureVector:
    """Extract a sparse numeric feature vector from one TraceLeak run.

    Args:
        run: TraceLeak run dictionary.
        allow_raw: If false, reject raw and cheat views.
        include_locations: Include source file/line tokens when present.

    Returns:
        Sparse numeric feature vector.
    """

    validate_run(run)
    view = run["view"]
    if not allow_raw and view in {"raw", "cheat"}:
        raise FeatureExtractionError(f"refusing to featurize {view!r} view without allow_raw=True")

    features: FeatureVector = {}
    _add(features, f"run.view={view}", 1.0)
    _add(features, f"run.target={run['target']}", 1.0)
    _add(features, f"run.target_version={run['target_version']}", 1.0)

    for event in run["events"]:
        _add_event_features(features, event, include_locations=include_locations)

    return features


def build_feature_matrix(runs: Iterable[dict[str, Any]], *, allow_raw: bool = False) -> tuple[list[str], list[list[float]]]:
    """Build a dense feature matrix from sparse vectors.

    This helper is intended for small tests and baseline models. Heavy local
    experiments may prefer a sparse matrix implementation.
    """

    vectors = [extract_feature_vector(run, allow_raw=allow_raw) for run in runs]
    if not vectors:
        raise FeatureExtractionError("runs must not be empty")

    feature_names = sorted({name for vector in vectors for name in vector})
    matrix = [[vector.get(name, 0.0) for name in feature_names] for vector in vectors]
    return feature_names, matrix


def _add_event_features(features: FeatureVector, event: dict[str, Any], *, include_locations: bool) -> None:
    event_type = event["event_type"]
    phase = event["phase"]
    function = event["function"]
    name = event["name"]

    _add(features, f"event_type={event_type}", 1.0)
    _add(features, f"phase={phase}", 1.0)
    _add(features, f"function={function}", 1.0)
    _add(features, f"event={event_type}:{phase}:{function}:{name}", 1.0)

    if include_locations:
        file_name = event.get("file")
        line = event.get("line")
        if file_name:
            _add(features, f"file={file_name}", 1.0)
            if line is not None:
                _add(features, f"location={file_name}:{line}", 1.0)

    redacted = event.get("value_redacted")
    if redacted is not None:
        if not isinstance(redacted, dict):
            raise TraceSchemaError("event.value_redacted must be an object when present")
        for key, value in _flatten_value("value_redacted", redacted):
            _add_encoded_value(features, event, key, value)


def _flatten_value(prefix: str, value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _flatten_value(f"{prefix}.{key}", child)
    else:
        yield prefix, value


def _add_encoded_value(features: FeatureVector, event: dict[str, Any], key: str, value: Any) -> None:
    base = "event_value:{event_type}:{phase}:{function}:{name}:{key}".format(
        event_type=event["event_type"],
        phase=event["phase"],
        function=event["function"],
        name=event["name"],
        key=key,
    )

    if isinstance(value, bool):
        _add(features, base, 1.0 if value else 0.0)
    elif isinstance(value, int | float):
        _add(features, base, float(value))
    elif value is None:
        _add(features, f"{base}=null", 1.0)
    elif isinstance(value, str):
        _add(features, f"{base}={value}", 1.0)
    else:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
        _add(features, f"{base}={encoded}", 1.0)


def _add(features: FeatureVector, key: str, amount: float) -> None:
    features[key] = features.get(key, 0.0) + amount

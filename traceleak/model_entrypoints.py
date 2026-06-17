"""Model entrypoint contracts for sequence, graph, and hybrid consumers."""

from __future__ import annotations

MODEL_ENTRYPOINT_FORMAT = "traceleak.model_entrypoint.v1"

ALLOWED_MODEL_ENTRYPOINTS: tuple[str, ...] = (
    "sequence",
    "graph",
    "hybrid",
)


def model_entrypoint_names() -> list[str]:
    """Return supported model entrypoint names."""

    return list(ALLOWED_MODEL_ENTRYPOINTS)

"""Consumer view helpers."""

from __future__ import annotations

CONSUMER_VIEW_FORMAT = "traceleak.consumer_view.v1"

CONSUMER_NAMES: tuple[str, ...] = (
    "sequence",
    "graph",
    "hybrid",
)

CONSUMER_VIEWS: dict[str, tuple[str, ...]] = {
    "sequence": ("program_events", "variable_state_sequence"),
    "graph": ("dependency_graph",),
    "hybrid": ("program_events", "variable_state_sequence", "dependency_graph"),
}


def consumer_names() -> list[str]:
    """Return supported consumer names."""

    return list(CONSUMER_NAMES)


def required_views_for_consumer(name: str) -> list[str]:
    """Return required representation views for a consumer."""

    return list(CONSUMER_VIEWS[name])

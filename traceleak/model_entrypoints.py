"""Model entrypoint contracts for sequence, graph, and hybrid consumers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MODEL_ENTRYPOINT_FORMAT = "traceleak.model_entrypoint.v1"

ALLOWED_MODEL_ENTRYPOINTS: tuple[str, ...] = (
    "sequence",
    "graph",
    "hybrid",
)

ENTRYPOINT_REQUIRED_VIEWS: dict[str, tuple[str, ...]] = {
    "sequence": ("program_events", "variable_state_sequence"),
    "graph": ("dependency_graph",),
    "hybrid": ("program_events", "variable_state_sequence", "dependency_graph"),
}


class ModelEntrypointError(ValueError):
    """Raised when a model entrypoint spec is invalid."""


@dataclass(frozen=True)
class ModelEntrypointSpec:
    """Schema-level model entrypoint description."""

    entrypoint_name: str
    required_views: list[str]
    tensor_contract_format: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "format": MODEL_ENTRYPOINT_FORMAT,
            "entrypoint_name": self.entrypoint_name,
            "required_views": list(self.required_views),
            "tensor_contract_format": self.tensor_contract_format,
            "metadata": dict(self.metadata),
        }


def model_entrypoint_names() -> list[str]:
    """Return supported model entrypoint names."""

    return list(ALLOWED_MODEL_ENTRYPOINTS)


def model_entrypoint_spec(entrypoint_name: str) -> dict[str, Any]:
    """Build a model entrypoint spec dictionary."""

    if entrypoint_name not in ALLOWED_MODEL_ENTRYPOINTS:
        raise ModelEntrypointError(f"invalid entrypoint_name: {entrypoint_name!r}")
    return {
        "format": MODEL_ENTRYPOINT_FORMAT,
        "entrypoint_name": entrypoint_name,
        "required_views": list(ENTRYPOINT_REQUIRED_VIEWS[entrypoint_name]),
        "tensor_contract_format": "traceleak.tensor_contract.v1",
        "metadata": {
            "schema_kind": "model_entrypoint",
            "claim_scope": "schema_only",
        },
    }

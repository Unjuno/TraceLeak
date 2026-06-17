"""Build DeepProgramSample records from OpenSSL path manifests."""

from __future__ import annotations

from typing import Any

from traceleak.deep_program_dataset import deep_program_sample_from_components
from traceleak.dependency_graph_schema import dependency_graph_from_program_events_and_variable_states
from traceleak.openssl_path_events import OPENSSL_PATH_EVENT_FORMAT, openssl_path_records_to_program_events
from traceleak.variable_state_sequence import variable_state_records_from_program_events

OPENSSL_PATH_DEEP_SAMPLE_FORMAT = "traceleak.openssl_path_deep_sample.v1"


def build_openssl_path_deep_program_sample(
    *,
    sample_id: str,
    path_records: list[dict[str, Any]],
    label: str = "openssl_path_sample",
) -> dict[str, Any]:
    """Build a DeepProgramSample from OpenSSL path manifest records."""

    program_events = openssl_path_records_to_program_events(path_records)
    variable_states = variable_state_records_from_program_events(
        program_events,
        sequence_id=f"{sample_id}:openssl_path_variables",
    )
    dependency_graph = dependency_graph_from_program_events_and_variable_states(
        program_events,
        variable_states,
        graph_id=f"{sample_id}:openssl_path_graph",
    )
    return deep_program_sample_from_components(
        sample_id=sample_id,
        program_events=program_events,
        variable_state_sequence=variable_states,
        dependency_graph=dependency_graph,
        labels={
            "training_target": {"class": label},
            "lab_only": True,
            "public_model_input": False,
        },
        consumer_modes=("sequence", "graph", "hybrid"),
        metadata={
            "source": "openssl_path_deep_program_sample",
            "format": OPENSSL_PATH_DEEP_SAMPLE_FORMAT,
            "path_event_format": OPENSSL_PATH_EVENT_FORMAT,
            "path_record_count": len(path_records),
            "runtime_action_enabled": False,
        },
    )

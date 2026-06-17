"""Build DeepProgramSample records from static ProgramEvent extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from traceleak.c_static_events import c_paths_to_program_events
from traceleak.deep_program_dataset import deep_program_sample_from_components
from traceleak.dependency_graph_schema import dependency_graph_from_program_events_and_variable_states
from traceleak.variable_state_sequence import variable_state_records_from_program_events

STATIC_PROGRAM_SAMPLE_FORMAT = "traceleak.static_program_sample.v1"


def build_static_program_deep_sample(
    *,
    root: Path,
    relative_paths: list[str],
    sample_id: str,
    label: str = "static_program_sample",
    max_lines_per_file: int = 400,
) -> dict[str, Any]:
    """Build a DeepProgramSample from selected C/H files."""

    events = c_paths_to_program_events(
        root=root,
        relative_paths=relative_paths,
        max_lines_per_file=max_lines_per_file,
    )
    states = variable_state_records_from_program_events(
        events,
        sequence_id=f"{sample_id}:static_variables",
    )
    graph = dependency_graph_from_program_events_and_variable_states(
        events,
        states,
        graph_id=f"{sample_id}:static_graph",
    )
    return deep_program_sample_from_components(
        sample_id=sample_id,
        program_events=events,
        variable_state_sequence=states,
        dependency_graph=graph,
        labels={
            "training_target": {"class": label},
            "lab_only": True,
            "public_model_input": False,
        },
        consumer_modes=("sequence", "graph", "hybrid"),
        metadata={
            "format": STATIC_PROGRAM_SAMPLE_FORMAT,
            "event_count": len(events),
            "state_count": len(states),
        },
    )

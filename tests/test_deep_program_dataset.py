import pytest

from traceleak.deep_program_dataset import (
    DEEP_PROGRAM_DATASET_FORMAT,
    DeepProgramDatasetError,
    DeepProgramSample,
    deep_program_sample_from_components,
    deep_program_sample_from_dict,
    masks_for_consumer_modes,
    validate_deep_program_sample,
)
from traceleak.dependency_graph_schema import dependency_graph_from_program_events_and_variable_states
from traceleak.variable_state_sequence import variable_state_records_from_program_events


def sample_program_event() -> dict:
    return {
        "event_id": "evt_000001",
        "time_step": 1,
        "event_type": "branch",
        "operation": "branch",
        "function": "synthetic_keygen",
        "source_location": {
            "file": "examples/synthetic/target.c",
            "line": 21,
        },
        "variable_reads": ["candidate_bucket", "branch_guard"],
        "variable_writes": ["branch_taken"],
        "value_class": "redacted",
        "dependency_tags": ["control_flow", "secret_derived_path"],
        "control_context": {
            "phase": "synthetic_leak",
            "value_bucket": "taken",
        },
        "metadata": {
            "target": "synthetic-leak",
            "view": "redacted",
            "public_safe": True,
        },
    }


def sample_labels() -> dict:
    return {
        "training_target": {
            "class": "metadata_even",
        },
        "lab_only": True,
        "public_model_input": False,
    }


def sample_deep_program_sample(*, consumer_modes: tuple[str, ...] = ("sequence", "graph", "hybrid")) -> dict:
    event = sample_program_event()
    states = variable_state_records_from_program_events([event], sequence_id="seq_000001")
    graph = dependency_graph_from_program_events_and_variable_states(
        [event],
        states,
        graph_id="graph_000001",
    )
    return deep_program_sample_from_components(
        sample_id="sample_000001",
        program_events=[event],
        variable_state_sequence=states,
        dependency_graph=graph,
        labels=sample_labels(),
        consumer_modes=consumer_modes,
        metadata={"public_safe": True},
    )


def test_validate_deep_program_sample_accepts_full_sample() -> None:
    sample = sample_deep_program_sample()
    validate_deep_program_sample(sample)
    parsed = deep_program_sample_from_dict(sample)
    assert isinstance(parsed, DeepProgramSample)
    assert parsed.to_dict() == sample
    assert sample["format"] == DEEP_PROGRAM_DATASET_FORMAT


def test_validate_deep_program_sample_rejects_missing_field() -> None:
    sample = sample_deep_program_sample()
    del sample["program_events"]
    with pytest.raises(DeepProgramDatasetError, match="missing required deep program sample field"):
        validate_deep_program_sample(sample)


def test_validate_deep_program_sample_rejects_bad_format() -> None:
    sample = sample_deep_program_sample()
    sample["format"] = "traceleak.deep_program_dataset.v0"
    with pytest.raises(DeepProgramDatasetError, match="invalid deep program sample format"):
        validate_deep_program_sample(sample)


def test_validate_deep_program_sample_rejects_public_label_input() -> None:
    sample = sample_deep_program_sample()
    sample["labels"]["public_model_input"] = True
    with pytest.raises(DeepProgramDatasetError, match="must not be marked as public model input"):
        validate_deep_program_sample(sample)


def test_validate_deep_program_sample_rejects_raw_dataset_metadata() -> None:
    sample = sample_deep_program_sample()
    sample["metadata"]["raw_capture"] = "not-public-safe"
    with pytest.raises(DeepProgramDatasetError, match="raw field"):
        validate_deep_program_sample(sample)


def test_validate_deep_program_sample_rejects_bad_masks() -> None:
    sample = sample_deep_program_sample()
    sample["masks"]["use_dependency_graph"] = False
    with pytest.raises(DeepProgramDatasetError, match="hybrid consumers require"):
        validate_deep_program_sample(sample)


def test_validate_deep_program_sample_rejects_bad_feature_names() -> None:
    sample = sample_deep_program_sample()
    del sample["feature_names"]["graph_edge_features"]
    with pytest.raises(DeepProgramDatasetError, match="missing required feature_names field"):
        validate_deep_program_sample(sample)


def test_masks_for_consumer_modes_supports_sequence_only() -> None:
    masks = masks_for_consumer_modes(["sequence"])
    assert masks == {
        "consumer_modes": ["sequence"],
        "use_program_events": True,
        "use_variable_state_sequence": True,
        "use_dependency_graph": False,
    }


def test_masks_for_consumer_modes_supports_graph_only() -> None:
    masks = masks_for_consumer_modes(["graph"])
    assert masks == {
        "consumer_modes": ["graph"],
        "use_program_events": False,
        "use_variable_state_sequence": False,
        "use_dependency_graph": True,
    }


def test_masks_for_consumer_modes_rejects_unknown_mode() -> None:
    with pytest.raises(DeepProgramDatasetError, match="invalid consumer_mode"):
        masks_for_consumer_modes(["mlp_only"])


def test_component_assembler_supports_sequence_only_sample() -> None:
    sample = sample_deep_program_sample(consumer_modes=("sequence",))
    validate_deep_program_sample(sample)
    assert sample["masks"]["consumer_modes"] == ["sequence"]
    assert sample["masks"]["use_dependency_graph"] is False
    assert sample["metadata"]["supports_sequence_model"] is True
    assert sample["metadata"]["supports_graph_model"] is False


def test_component_assembler_supports_graph_only_sample() -> None:
    sample = sample_deep_program_sample(consumer_modes=("graph",))
    validate_deep_program_sample(sample)
    assert sample["masks"]["consumer_modes"] == ["graph"]
    assert sample["masks"]["use_dependency_graph"] is True
    assert sample["masks"]["use_program_events"] is False
    assert sample["metadata"]["supports_graph_model"] is True


def test_component_assembler_marks_representation_only_scope() -> None:
    sample = sample_deep_program_sample()
    assert sample["metadata"]["dataset_kind"] == "deep_program_dataset_sample"
    assert sample["metadata"]["claim_scope"] == "representation_only_not_leakage_proof"
    assert sample["labels"]["lab_only"] is True

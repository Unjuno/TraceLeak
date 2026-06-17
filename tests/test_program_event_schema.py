import pytest

from traceleak.program_event_schema import (
    ProgramEvent,
    ProgramEventSchemaError,
    program_event_from_dict,
    program_event_from_legacy_model_step,
    program_events_from_legacy_model_sequence,
    sort_program_events,
    validate_program_event,
    validate_program_events,
)


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
            "branch_depth": 1,
        },
        "metadata": {
            "target": "synthetic-leak",
            "view": "redacted",
            "public_safe": True,
        },
    }


def sample_legacy_step() -> dict:
    return {
        "position": 2,
        "step": 2,
        "target": "synthetic-leak",
        "view": "redacted",
        "event_type": "branch",
        "phase": "synthetic_leak",
        "function": "synthetic_keygen",
        "name": "secret_dependent_branch",
        "event_token": "branch:synthetic_leak:synthetic_keygen:secret_dependent_branch",
        "source_token": "examples/synthetic/target.c:21:synthetic_keygen:secret_dependent_branch",
        "context_token": "synthetic_leak:synthetic_keygen",
        "redacted_value_tokens": ["value_redacted.branch_taken=true"],
    }


def test_validate_program_event_accepts_full_event() -> None:
    event = sample_program_event()
    validate_program_event(event)
    parsed = program_event_from_dict(event)
    assert isinstance(parsed, ProgramEvent)
    assert parsed.to_dict() == event


def test_validate_program_event_rejects_missing_field() -> None:
    event = sample_program_event()
    del event["operation"]
    with pytest.raises(ProgramEventSchemaError, match="missing required program event field"):
        validate_program_event(event)


def test_validate_program_event_rejects_bad_types() -> None:
    event = sample_program_event()
    event["time_step"] = -1
    with pytest.raises(ProgramEventSchemaError, match="time_step"):
        validate_program_event(event)

    event = sample_program_event()
    event["variable_reads"] = ["ok", 3]
    with pytest.raises(ProgramEventSchemaError, match="variable_reads"):
        validate_program_event(event)


def test_validate_program_event_rejects_raw_secret_payload_keys() -> None:
    event = sample_program_event()
    event["metadata"]["value_raw"] = "not-public-safe"
    with pytest.raises(ProgramEventSchemaError, match="raw field"):
        validate_program_event(event)


def test_validate_program_events_rejects_duplicate_ids() -> None:
    first = sample_program_event()
    second = sample_program_event()
    second["time_step"] = 2
    with pytest.raises(ProgramEventSchemaError, match="duplicate event_id"):
        validate_program_events([first, second])


def test_sort_program_events_is_deterministic() -> None:
    first = sample_program_event()
    second = sample_program_event()
    second["event_id"] = "evt_000000"
    second["time_step"] = 0
    third = sample_program_event()
    third["event_id"] = "evt_000002"
    third["time_step"] = 1
    sorted_events = sort_program_events([third, first, second])
    assert [event["event_id"] for event in sorted_events] == [
        "evt_000000",
        "evt_000001",
        "evt_000002",
    ]


def test_legacy_model_step_conversion_preserves_tokens_and_source() -> None:
    event = program_event_from_legacy_model_step(sample_legacy_step(), event_id_prefix="legacy")
    assert event["event_id"] == (
        "legacy:000002:branch_synthetic_leak_synthetic_keygen_secret_dependent_branch"
    )
    assert event["time_step"] == 2
    assert event["event_type"] == "branch"
    assert event["operation"] == "branch"
    assert event["function"] == "synthetic_keygen"
    assert event["source_location"] == {
        "file": "examples/synthetic/target.c",
        "line": 21,
    }
    assert event["value_class"] == "redacted"
    assert event["metadata"]["legacy_event_token"] == (
        "branch:synthetic_leak:synthetic_keygen:secret_dependent_branch"
    )
    assert event["metadata"]["redacted_value_tokens"] == ["value_redacted.branch_taken=true"]


def test_legacy_model_sequence_conversion_sorts_by_time() -> None:
    step = sample_legacy_step()
    earlier = dict(step)
    earlier["step"] = 1
    earlier["event_token"] = "phase:synthetic_leak:synthetic_keygen:start"
    events = program_events_from_legacy_model_sequence([step, earlier])
    assert [event["time_step"] for event in events] == [1, 2]
    assert events[0]["operation"] == "branch"


def test_legacy_model_step_missing_step_falls_back_to_position_argument() -> None:
    step = sample_legacy_step()
    del step["step"]
    del step["position"]
    event = program_event_from_legacy_model_step(step, position=7)
    assert event["time_step"] == 7

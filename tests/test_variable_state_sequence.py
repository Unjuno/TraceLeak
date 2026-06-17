import pytest

from traceleak.variable_state_sequence import (
    VariableStateRecord,
    VariableStateSequenceError,
    sort_variable_state_sequence,
    validate_variable_state_record,
    validate_variable_state_sequence,
    variable_state_from_dict,
    variable_state_records_from_program_events,
)


def sample_state_record() -> dict:
    return {
        "sequence_id": "seq_000001",
        "time_step": 1,
        "variable_id": "branch_taken",
        "scope": "synthetic_keygen",
        "state_class": "write",
        "value_observed": None,
        "value_bucket": "taken",
        "source_event_id": "evt_000001",
        "depends_on": ["candidate_bucket"],
        "taint_class": "secret_derived",
        "is_secret_derived": True,
        "metadata": {
            "target": "synthetic-leak",
            "view": "redacted",
            "public_safe": True,
        },
    }


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


def test_validate_variable_state_record_accepts_full_record() -> None:
    record = sample_state_record()
    validate_variable_state_record(record)
    parsed = variable_state_from_dict(record)
    assert isinstance(parsed, VariableStateRecord)
    assert parsed.to_dict() == record


def test_validate_variable_state_record_rejects_missing_field() -> None:
    record = sample_state_record()
    del record["taint_class"]
    with pytest.raises(VariableStateSequenceError, match="missing required variable state field"):
        validate_variable_state_record(record)


def test_validate_variable_state_record_rejects_bad_types() -> None:
    record = sample_state_record()
    record["time_step"] = -1
    with pytest.raises(VariableStateSequenceError, match="time_step"):
        validate_variable_state_record(record)

    record = sample_state_record()
    record["depends_on"] = ["ok", 3]
    with pytest.raises(VariableStateSequenceError, match="depends_on"):
        validate_variable_state_record(record)


def test_public_safe_record_rejects_secret_derived_observed_value() -> None:
    record = sample_state_record()
    record["value_observed"] = "raw-looking-secret"
    with pytest.raises(VariableStateSequenceError, match="must not expose observed values"):
        validate_variable_state_record(record)


def test_public_safe_record_rejects_raw_secret_payload_keys() -> None:
    record = sample_state_record()
    record["metadata"]["raw_capture"] = "not-public-safe"
    with pytest.raises(VariableStateSequenceError, match="raw field"):
        validate_variable_state_record(record)


def test_public_observed_value_is_allowed() -> None:
    record = sample_state_record()
    record["state_class"] = "observe"
    record["value_observed"] = "public-counter-bucket"
    record["value_bucket"] = "public-counter-bucket"
    record["depends_on"] = []
    record["taint_class"] = "public"
    record["is_secret_derived"] = False
    validate_variable_state_record(record)


def test_secret_derived_flag_must_match_taint_class() -> None:
    record = sample_state_record()
    record["taint_class"] = "redacted"
    with pytest.raises(VariableStateSequenceError, match="taint_class=secret_derived"):
        validate_variable_state_record(record)


def test_validate_sequence_rejects_duplicate_record_keys() -> None:
    first = sample_state_record()
    second = sample_state_record()
    with pytest.raises(VariableStateSequenceError, match="duplicate variable state record key"):
        validate_variable_state_sequence([first, second])


def test_sort_variable_state_sequence_is_deterministic() -> None:
    first = sample_state_record()
    second = sample_state_record()
    second["variable_id"] = "candidate_bucket"
    second["state_class"] = "read"
    second["depends_on"] = []
    third = sample_state_record()
    third["time_step"] = 0
    third["variable_id"] = "setup_flag"
    third["state_class"] = "read"
    third["depends_on"] = []
    sorted_records = sort_variable_state_sequence([first, third, second])
    assert [record["variable_id"] for record in sorted_records] == [
        "setup_flag",
        "candidate_bucket",
        "branch_taken",
    ]


def test_program_events_to_variable_state_records_uses_explicit_reads_and_writes() -> None:
    records = variable_state_records_from_program_events(
        [sample_program_event()],
        sequence_id="seq_from_events",
    )
    assert [record["state_class"] for record in records] == ["read", "read", "write"]
    assert [record["variable_id"] for record in records] == [
        "branch_guard",
        "candidate_bucket",
        "branch_taken",
    ]
    write_record = records[2]
    assert write_record["depends_on"] == ["candidate_bucket", "branch_guard"]
    assert write_record["source_event_id"] == "evt_000001"
    assert write_record["taint_class"] == "secret_derived"
    assert write_record["is_secret_derived"] is True
    assert write_record["value_bucket"] == "taken"
    assert write_record["metadata"]["derived_from_program_event"] is True


def test_program_events_to_variable_state_records_requires_variables() -> None:
    event = sample_program_event()
    event["variable_reads"] = []
    event["variable_writes"] = []
    with pytest.raises(VariableStateSequenceError, match="did not contain variable reads or writes"):
        variable_state_records_from_program_events([event])

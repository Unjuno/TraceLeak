import pytest

from traceleak.schema import TraceSchemaError, validate_run


def valid_run() -> dict:
    return {
        "run_id": "synthetic_000001",
        "target": "synthetic-leak",
        "target_version": "v0",
        "view": "redacted",
        "events": [
            {
                "step": 1,
                "phase": "synthetic_leak",
                "function": "synthetic_keygen",
                "file": "examples/synthetic/target.c",
                "line": 21,
                "event_type": "branch",
                "name": "secret_dependent_branch",
                "value_redacted": {"branch_taken": True},
            }
        ],
        "labels_lab_only": {"secret_bucket": 1},
    }


def test_validate_run_accepts_valid_redacted_run() -> None:
    validate_run(valid_run())


def test_validate_run_rejects_missing_required_field() -> None:
    run = valid_run()
    del run["run_id"]
    with pytest.raises(TraceSchemaError):
        validate_run(run)


def test_validate_run_rejects_invalid_view() -> None:
    run = valid_run()
    run["view"] = "unsafe"
    with pytest.raises(TraceSchemaError):
        validate_run(run)


def test_public_export_rejects_raw_view() -> None:
    run = valid_run()
    run["view"] = "raw"
    with pytest.raises(TraceSchemaError):
        validate_run(run, public_export=True)


def test_public_export_rejects_secret_equivalent_event_field() -> None:
    run = valid_run()
    run["events"][0]["value_raw"] = "0xdeadbeef"
    with pytest.raises(TraceSchemaError):
        validate_run(run, public_export=True)

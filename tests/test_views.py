from traceleak.views import to_view


def raw_run() -> dict:
    return {
        "run_id": "synthetic_000001",
        "target": "synthetic-leak",
        "target_version": "v0",
        "view": "raw",
        "events": [
            {
                "step": 1,
                "phase": "synthetic_leak",
                "function": "synthetic_keygen",
                "file": "examples/synthetic/target.c",
                "line": 21,
                "event_type": "branch",
                "name": "secret_dependent_branch",
                "value_type": "int",
                "value_raw": "0x01",
                "value_redacted": {"branch_taken": True},
            }
        ],
        "labels_lab_only": {"secret_bucket": 1},
    }


def test_to_path_strips_values_and_labels() -> None:
    converted = to_view(raw_run(), "path")
    assert converted["view"] == "path"
    assert "labels_lab_only" not in converted
    event = converted["events"][0]
    assert "value_raw" not in event
    assert "value_redacted" not in event
    assert event["name"] == "secret_dependent_branch"


def test_to_redacted_keeps_redacted_value_only() -> None:
    converted = to_view(raw_run(), "redacted")
    event = converted["events"][0]
    assert "value_raw" not in event
    assert event["value_redacted"] == {"branch_taken": True}


def test_to_meta_strips_events_and_labels() -> None:
    converted = to_view(raw_run(), "meta")
    assert converted["view"] == "meta"
    assert converted["events"] == []
    assert "labels_lab_only" not in converted

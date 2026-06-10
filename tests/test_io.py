from traceleak.io import read_jsonl, write_jsonl


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
                "event_type": "phase",
                "name": "keygen_start",
            }
        ],
    }


def test_write_then_read_jsonl(tmp_path) -> None:
    path = tmp_path / "runs.jsonl"
    write_jsonl(path, [valid_run()])
    loaded = list(read_jsonl(path))
    assert loaded == [valid_run()]

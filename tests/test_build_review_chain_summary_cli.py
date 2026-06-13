import json

from scripts import build_review_chain_summary as cli


def test_build_review_chain_summary_cli_writes_summary(tmp_path, monkeypatch) -> None:
    out = tmp_path / "summary.json"
    monkeypatch.setattr("sys.argv", ["build_review_chain_summary", "--out", str(out)])

    assert cli.main() == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["format"] == "traceleak.review_chain_summary.v1"
    assert data["mode"] == "review_only"
    assert data["chain"] == ["P3", "P4", "P5"]
    assert data["activation_allowed"] is False
    assert data["auto_approval"] is False
    assert data["artifact_slot_count"] == len(data["artifact_kinds"])
    assert data["artifact_slot_count"] > 0

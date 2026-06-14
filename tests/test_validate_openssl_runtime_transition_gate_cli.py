import json

from scripts import validate_openssl_runtime_transition_gate as cli
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate


def test_runtime_transition_gate_cli_builds_gate(tmp_path, monkeypatch) -> None:
    out_path = tmp_path / "runtime-gate.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_runtime_transition_gate",
            "--out",
            str(out_path),
            "--reviewer",
            "reviewer",
            "--reviewed-at",
            "2026-06-14T00:00:00Z",
        ],
    )

    assert cli.main() == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["format"] == "traceleak.openssl_runtime_transition_gate.v1"
    assert payload["conditions"]["runtime_action_enabled"] is False


def test_runtime_transition_gate_cli_rejects_bad_gate(tmp_path, monkeypatch) -> None:
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )
    gate["conditions"]["payload_access_enabled"] = True
    gate_path = tmp_path / "bad-runtime-gate.json"
    gate_path.write_text(json.dumps(gate), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_runtime_transition_gate",
            "--gate",
            str(gate_path),
        ],
    )

    assert cli.main() == 1

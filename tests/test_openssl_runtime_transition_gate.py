import pytest

from traceleak.openssl_runtime_transition_gate import (
    OpenSSLRuntimeTransitionGateError,
    build_openssl_runtime_transition_gate,
    validate_openssl_runtime_transition_gate,
)


def test_runtime_transition_gate_is_conservative() -> None:
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )

    assert gate["format"] == "traceleak.openssl_runtime_transition_gate.v1"
    assert gate["phase"] == "P28"
    assert gate["mode"] == "review_gate_only"
    assert gate["target_decision"] == "constant_time_helper_misuse_path"
    assert gate["conditions"]["target_selection_reviewed"] is True
    assert gate["conditions"]["local_workspace_required"] is True
    assert gate["conditions"]["runtime_action_enabled"] is False
    assert gate["conditions"]["payload_access_enabled"] is False


def test_runtime_transition_gate_rejects_wrong_target() -> None:
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )
    gate["target_decision"] = "all_openssl"

    with pytest.raises(OpenSSLRuntimeTransitionGateError, match="target_decision"):
        validate_openssl_runtime_transition_gate(gate)


def test_runtime_transition_gate_rejects_enabled_runtime_action() -> None:
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )
    gate["conditions"]["runtime_action_enabled"] = True

    with pytest.raises(OpenSSLRuntimeTransitionGateError, match="runtime_action_enabled"):
        validate_openssl_runtime_transition_gate(gate)


def test_runtime_transition_gate_rejects_enabled_payload_access() -> None:
    gate = build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )
    gate["conditions"]["payload_access_enabled"] = True

    with pytest.raises(OpenSSLRuntimeTransitionGateError, match="payload_access_enabled"):
        validate_openssl_runtime_transition_gate(gate)

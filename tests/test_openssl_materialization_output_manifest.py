import pytest

from traceleak.openssl_actual_execution_preflight import build_openssl_actual_execution_preflight_report
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_materialization_approval_gate import (
    build_openssl_materialization_approval_gate,
    build_openssl_materialization_approval_record,
)
from traceleak.openssl_materialization_output_contract import (
    build_openssl_materialization_output_contract,
)
from traceleak.openssl_materialization_output_manifest import (
    OpenSSLMaterializationOutputManifestError,
    build_openssl_materialization_output_manifest,
    validate_openssl_materialization_output_manifest,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)


def make_contract() -> dict:
    preflight = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=preflight)
    request = build_openssl_reviewed_materialization_request(execution_plan=plan)
    record = build_openssl_materialization_approval_record(
        reviewed_request=request,
        reviewer="reviewer",
        reviewed_at="2026-06-13T00:00:00Z",
    )
    gate = build_openssl_materialization_approval_gate(
        reviewed_request=request,
        approval_record=record,
    )
    return build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )


def test_build_openssl_materialization_output_manifest_is_metadata_only() -> None:
    contract = make_contract()
    manifest = build_openssl_materialization_output_manifest(
        output_contract=contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )

    assert manifest["format"] == "traceleak.openssl_materialization_output_manifest.v1"
    assert manifest["status"] == "manifest_ready"
    assert manifest["phase"] == "P11"
    assert manifest["mode"] == "metadata_only"
    assert manifest["contract_format"] == contract["format"]
    assert manifest["source_pin_digest"] == contract["source_pin_digest"]
    assert manifest["trace_contract_digest"] == contract["trace_contract_digest"]
    assert manifest["artifact_digests"] == {"manifest": "sha256:manifest"}
    assert manifest["metadata"]["redacted_metadata_only"] is True
    assert manifest["metadata"]["source_text_embedded"] is False
    assert manifest["metadata"]["diff_embedded"] is False
    assert manifest["metadata"]["commands_embedded"] is False
    assert manifest["metadata"]["build_output_embedded"] is False
    assert manifest["metadata"]["execution_output_embedded"] is False
    assert manifest["metadata"]["raw_capture_embedded"] is False
    assert manifest["execution_allowed"] is False


def test_openssl_materialization_output_manifest_rejects_empty_digests() -> None:
    contract = make_contract()
    manifest = build_openssl_materialization_output_manifest(
        output_contract=contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    manifest["artifact_digests"] = {}

    with pytest.raises(OpenSSLMaterializationOutputManifestError, match="artifact_digests"):
        validate_openssl_materialization_output_manifest(
            manifest=manifest,
            output_contract=contract,
        )


def test_openssl_materialization_output_manifest_rejects_contract_mismatch() -> None:
    contract = make_contract()
    manifest = build_openssl_materialization_output_manifest(
        output_contract=contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    manifest["source_pin_digest"] = "sha256:other-source-pin"

    with pytest.raises(OpenSSLMaterializationOutputManifestError, match="source_pin_digest"):
        validate_openssl_materialization_output_manifest(
            manifest=manifest,
            output_contract=contract,
        )


def test_openssl_materialization_output_manifest_rejects_payload_embedding() -> None:
    contract = make_contract()
    manifest = build_openssl_materialization_output_manifest(
        output_contract=contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    manifest["metadata"]["commands_embedded"] = True

    with pytest.raises(OpenSSLMaterializationOutputManifestError, match="commands_embedded"):
        validate_openssl_materialization_output_manifest(
            manifest=manifest,
            output_contract=contract,
        )

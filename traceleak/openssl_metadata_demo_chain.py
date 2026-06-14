"""One-command OpenSSL metadata-demo chain helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_actual_execution_preflight import (
    build_openssl_actual_execution_preflight_report,
)
from traceleak.openssl_isolated_execution_plan import build_openssl_isolated_execution_plan
from traceleak.openssl_materialization_approval_gate import (
    build_openssl_materialization_approval_gate,
    build_openssl_materialization_approval_record,
)
from traceleak.openssl_materialization_output_contract import (
    build_openssl_materialization_output_contract,
)
from traceleak.openssl_materialization_output_manifest import (
    build_openssl_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_handoff_contract import (
    build_openssl_model_sequence_handoff_contract,
)
from traceleak.openssl_model_sequence_ingestion_preflight import (
    build_openssl_model_sequence_ingestion_preflight,
)
from traceleak.openssl_model_sequence_input_contract import (
    build_openssl_model_sequence_input_contract,
)
from traceleak.openssl_model_sequence_input_manifest import (
    build_openssl_model_sequence_input_manifest,
)
from traceleak.openssl_model_sequence_metadata_demo_manifest import (
    build_openssl_model_sequence_metadata_demo_manifest,
)
from traceleak.openssl_model_sequence_metadata_sample import (
    build_openssl_model_sequence_metadata_sample,
)
from traceleak.openssl_model_sequence_metadata_sample_demo_result import (
    build_openssl_model_sequence_metadata_sample_demo_result,
)
from traceleak.openssl_model_sequence_metadata_sample_model_preflight import (
    build_openssl_model_sequence_metadata_sample_model_preflight,
)
from traceleak.openssl_model_sequence_sample_approval_gate import (
    build_openssl_model_sequence_sample_approval_gate,
    build_openssl_model_sequence_sample_approval_record,
)
from traceleak.openssl_model_sequence_sample_contract import (
    build_openssl_model_sequence_sample_contract,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    build_openssl_model_sequence_sample_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_output_contract import (
    build_openssl_model_sequence_sample_materialization_output_contract,
)
from traceleak.openssl_model_sequence_sample_materialization_output_manifest import (
    build_openssl_model_sequence_sample_materialization_output_manifest,
)
from traceleak.openssl_model_sequence_sample_materialization_request_contract import (
    build_openssl_model_sequence_sample_materialization_request_contract,
)
from traceleak.openssl_reviewed_materialization_request import (
    build_openssl_reviewed_materialization_request,
)

DEFAULT_OUTPUT_NAMES = {
    "sample_contract": "sample-contract.json",
    "sample_manifest": "sample-manifest.json",
    "approval_record": "approval-record.json",
    "approval_gate": "approval-gate.json",
    "request_contract": "request-contract.json",
    "output_contract": "output-contract.json",
    "output_manifest": "output-manifest.json",
    "metadata_sample": "metadata-sample.json",
    "model_preflight": "model-preflight.json",
    "demo_summary": "demo-summary.json",
    "baseline_result": "baseline-result.json",
    "nn_result": "nn-result.json",
    "demo_manifest": "demo-manifest.json",
}


class OpenSSLMetadataDemoChainError(ValueError):
    """Raised when metadata demo chain arguments are invalid."""


def build_openssl_metadata_demo_chain(
    *,
    record_count: int = 4,
    sample_id: str = "openssl-metadata-demo-sample",
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-14T00:00:00Z",
    epochs: int = 20,
) -> dict[str, Any]:
    """Build all public-safe metadata demo artifacts in memory."""

    if record_count < 4 or record_count % 2 != 0:
        raise OpenSSLMetadataDemoChainError("record_count must be an even integer >= 4")
    base = build_openssl_actual_execution_preflight_report(
        source_pin_digest="sha256:source-pin",
        trace_contract_digest="sha256:trace-contract",
        workspace_root="C:/tmp/traceleak-openssl-workspace",
        cleanup_plan="remove isolated workspace after review",
    )
    plan = build_openssl_isolated_execution_plan(preflight_report=base)
    request = build_openssl_reviewed_materialization_request(execution_plan=plan)
    record = build_openssl_materialization_approval_record(
        reviewed_request=request,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )
    gate = build_openssl_materialization_approval_gate(
        reviewed_request=request,
        approval_record=record,
    )
    base_output_contract = build_openssl_materialization_output_contract(
        approval_gate=gate,
        output_manifest_path="artifacts/openssl-materialization-output-manifest.json",
    )
    base_output_manifest = build_openssl_materialization_output_manifest(
        output_contract=base_output_contract,
        artifact_digests={"manifest": "sha256:manifest"},
    )
    handoff = build_openssl_model_sequence_handoff_contract(
        materialization_manifest=base_output_manifest,
        output_contract=base_output_contract,
        feature_namespace="openssl.materialization.redacted",
        sample_id=sample_id,
    )
    ingestion_preflight = build_openssl_model_sequence_ingestion_preflight(
        handoff_contract=handoff,
    )
    input_contract = build_openssl_model_sequence_input_contract(
        ingestion_preflight=ingestion_preflight,
        output_sample_path="artifacts/openssl-model-sequence-input.json",
    )
    input_manifest = build_openssl_model_sequence_input_manifest(
        input_contract=input_contract,
        input_digest="sha256:input",
    )
    sample_contract = build_openssl_model_sequence_sample_contract(
        input_manifest=input_manifest,
        input_contract=input_contract,
        feature_fields=["artifact_count", "namespace_id"],
        label_fields=["label"],
        metadata_fields=["sample_id", "input_digest"],
    )
    sample_manifest = build_openssl_model_sequence_sample_manifest(
        sample_contract=sample_contract,
        sample_digest="sha256:sample",
    )
    approval_record = build_openssl_model_sequence_sample_approval_record(
        sample_manifest=sample_manifest,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )
    approval_gate = build_openssl_model_sequence_sample_approval_gate(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
    )
    request_contract = build_openssl_model_sequence_sample_materialization_request_contract(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        planned_sample_path="artifacts/openssl-model-sequence-metadata-sample.json",
    )
    output_contract = build_openssl_model_sequence_sample_materialization_output_contract(
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        output_manifest_path="artifacts/openssl-model-sequence-metadata-sample-output-manifest.json",
    )
    output_manifest = build_openssl_model_sequence_sample_materialization_output_manifest(
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        artifact_digests={"sample": "sha256:sample"},
    )
    metadata_sample = build_openssl_model_sequence_metadata_sample(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        record_count=record_count,
    )
    model_preflight = build_openssl_model_sequence_metadata_sample_model_preflight(
        sample=metadata_sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    demo_outputs = build_openssl_model_sequence_metadata_sample_demo_result(
        sample=metadata_sample,
        model_preflight=model_preflight,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
        epochs=epochs,
    )
    demo_manifest = build_openssl_model_sequence_metadata_demo_manifest(
        summary=demo_outputs["summary"],
        baseline_result=demo_outputs["baseline_result"],
        nn_result=demo_outputs["nn_result"],
        sample=metadata_sample,
        model_preflight=model_preflight,
    )
    return {
        "sample_contract": sample_contract,
        "sample_manifest": sample_manifest,
        "approval_record": approval_record,
        "approval_gate": approval_gate,
        "request_contract": request_contract,
        "output_contract": output_contract,
        "output_manifest": output_manifest,
        "metadata_sample": metadata_sample,
        "model_preflight": model_preflight,
        "demo_summary": demo_outputs["summary"],
        "baseline_result": demo_outputs["baseline_result"],
        "nn_result": demo_outputs["nn_result"],
        "demo_manifest": demo_manifest,
    }


def write_openssl_metadata_demo_chain(
    *,
    output_dir: Path,
    artifacts: dict[str, Any],
) -> dict[str, Path]:
    """Write all metadata demo chain artifacts to a directory."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for key, filename in DEFAULT_OUTPUT_NAMES.items():
        if key not in artifacts:
            raise OpenSSLMetadataDemoChainError(f"missing artifact: {key}")
        path = output_dir / filename
        path.write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths[key] = path
    return paths

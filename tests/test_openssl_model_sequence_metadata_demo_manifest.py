import pytest

from traceleak.openssl_model_sequence_metadata_demo_manifest import (
    OpenSSLModelSequenceMetadataDemoManifestError,
    build_openssl_model_sequence_metadata_demo_manifest,
    validate_openssl_model_sequence_metadata_demo_manifest,
)


def test_metadata_demo_manifest_builds_from_demo_outputs(metadata_demo_artifacts) -> None:
    manifest = metadata_demo_artifacts["demo_manifest"]

    assert manifest["format"] == "traceleak.openssl_model_sequence_metadata_demo_manifest.v1"
    assert manifest["phase"] == "P26"
    assert manifest["sample_digest"] == metadata_demo_artifacts["demo_summary"]["sample_digest"]
    assert manifest["public_statement"]["metadata_only"] is True
    assert manifest["public_statement"]["payload_free"] is True
    assert manifest["public_statement"]["public_safe"] is True
    assert manifest["public_statement"]["openssl_leakage_claim"] is False


def test_metadata_demo_manifest_rejects_digest_mismatch(metadata_demo_artifacts) -> None:
    manifest = build_openssl_model_sequence_metadata_demo_manifest(
        summary=metadata_demo_artifacts["demo_summary"],
        baseline_result=metadata_demo_artifacts["baseline_result"],
        nn_result=metadata_demo_artifacts["nn_result"],
        sample=metadata_demo_artifacts["metadata_sample"],
        model_preflight=metadata_demo_artifacts["model_preflight"],
    )
    manifest["sample_digest"] = "sha256:other"

    with pytest.raises(OpenSSLModelSequenceMetadataDemoManifestError, match="sample_digest"):
        validate_openssl_model_sequence_metadata_demo_manifest(
            manifest=manifest,
            summary=metadata_demo_artifacts["demo_summary"],
            baseline_result=metadata_demo_artifacts["baseline_result"],
            nn_result=metadata_demo_artifacts["nn_result"],
            sample=metadata_demo_artifacts["metadata_sample"],
            model_preflight=metadata_demo_artifacts["model_preflight"],
        )


def test_metadata_demo_manifest_rejects_public_statement_claim(metadata_demo_artifacts) -> None:
    manifest = metadata_demo_artifacts["demo_manifest"]
    manifest["public_statement"]["openssl_leakage_claim"] = True

    with pytest.raises(OpenSSLModelSequenceMetadataDemoManifestError, match="openssl_leakage_claim"):
        validate_openssl_model_sequence_metadata_demo_manifest(
            manifest=manifest,
            summary=metadata_demo_artifacts["demo_summary"],
            baseline_result=metadata_demo_artifacts["baseline_result"],
            nn_result=metadata_demo_artifacts["nn_result"],
            sample=metadata_demo_artifacts["metadata_sample"],
            model_preflight=metadata_demo_artifacts["model_preflight"],
        )

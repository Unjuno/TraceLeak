import json

import pytest

from traceleak.openssl_derived_metadata_profile_demo_chain import (
    DEFAULT_PROFILE_DEMO_OUTPUT_NAMES,
    OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT,
    OpenSSLDerivedMetadataProfileDemoChainError,
    build_openssl_derived_metadata_profile_demo_chain,
    validate_openssl_derived_metadata_profile_demo_summary,
    write_openssl_derived_metadata_profile_demo_chain,
)


def test_profile_demo_chain_builds_all_outputs() -> None:
    artifacts = build_openssl_derived_metadata_profile_demo_chain(epochs=20)

    assert set(artifacts) == set(DEFAULT_PROFILE_DEMO_OUTPUT_NAMES)
    assert artifacts["profile_input"]["format"] == "traceleak.openssl_derived_metadata_profile.v1"
    assert artifacts["adapter_input"]["format"] == "traceleak.openssl_derived_metadata_input.v1"
    assert artifacts["model_sequence_sample"]["format"] == "traceleak.model_sequence.v1"
    assert artifacts["baseline_result"]["result_type"] == "model_sequence_baseline"
    assert artifacts["nn_result"]["result_type"] == "model_sequence_nn"
    assert artifacts["demo_summary"]["format"] == OPENSSL_DERIVED_METADATA_PROFILE_DEMO_CHAIN_FORMAT
    assert artifacts["demo_summary"]["bridge_summary"]["profile_to_adapter"] is True
    assert artifacts["demo_summary"]["flags"]["payload_inspected"] is False
    assert artifacts["demo_summary"]["next_level"]["level"] == 7
    validate_openssl_derived_metadata_profile_demo_summary(artifacts["demo_summary"])


def test_profile_demo_chain_writes_outputs(tmp_path) -> None:
    artifacts = build_openssl_derived_metadata_profile_demo_chain(epochs=20)

    paths = write_openssl_derived_metadata_profile_demo_chain(output_dir=tmp_path, artifacts=artifacts)

    assert set(paths) == set(DEFAULT_PROFILE_DEMO_OUTPUT_NAMES)
    for path in paths.values():
        assert path.exists()
    assert json.loads((tmp_path / "profile-demo-summary.json").read_text(encoding="utf-8"))["phase"] == "P99"


def test_profile_demo_chain_rejects_bad_epochs() -> None:
    with pytest.raises(OpenSSLDerivedMetadataProfileDemoChainError, match="epochs"):
        build_openssl_derived_metadata_profile_demo_chain(epochs=0)

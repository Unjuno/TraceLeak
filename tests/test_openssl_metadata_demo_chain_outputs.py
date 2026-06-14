import json

from traceleak.openssl_metadata_demo_chain import (
    DEFAULT_OUTPUT_NAMES,
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)


def test_metadata_demo_chain_writes_expected_json_objects(tmp_path) -> None:
    out_dir = tmp_path / "metadata_demo"
    artifacts = build_openssl_metadata_demo_chain(epochs=20)
    paths = write_openssl_metadata_demo_chain(output_dir=out_dir, artifacts=artifacts)

    assert set(paths) == set(DEFAULT_OUTPUT_NAMES)
    for key, filename in DEFAULT_OUTPUT_NAMES.items():
        path = out_dir / filename
        assert paths[key] == path
        assert path.exists()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)


def test_metadata_demo_chain_sample_shape(metadata_demo_artifacts) -> None:
    sample = metadata_demo_artifacts["metadata_sample"]

    assert sample["format"] == "traceleak.model_sequence.v1"
    assert sample["artifact_format"] == "traceleak.openssl_model_sequence_metadata_sample.v1"
    assert sample["run_count"] == len(sample["records"])
    assert sample["sample_metadata"]["metadata_only"] is True
    assert sample["sample_metadata"]["payload_free"] is True
    for record in sample["records"]:
        assert isinstance(record["run_id"], str)
        assert record["target"] == "openssl-metadata-only"
        assert record["view"] == "meta"
        assert isinstance(record["sequence"], list)
        assert isinstance(record["token_counts"], dict)
        assert isinstance(record["label"], str)


def test_metadata_demo_chain_summary_shape(metadata_demo_artifacts) -> None:
    summary = metadata_demo_artifacts["demo_summary"]

    assert summary["format"] == "traceleak.openssl_model_sequence_metadata_sample_demo_result.v1"
    assert summary["phase"] == "P24"
    assert summary["flags"]["metadata_only"] is True
    assert summary["flags"]["payload_free"] is True
    assert summary["flags"]["public_safe"] is True
    assert summary["flags"]["baseline_result_generated"] is True
    assert summary["flags"]["model_result_generated"] is True
    assert summary["flags"]["openssl_leakage_claim"] is False
    assert "baseline_summary" in summary
    assert "nn_summary" in summary

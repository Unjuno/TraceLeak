import pytest

from traceleak.analysis_bundle_contract import (
    ANALYSIS_BUNDLE_FORMAT,
    AnalysisBundleContractError,
    AnalysisBundleRecord,
    analysis_bundle_record,
    analysis_bundle_record_from_dict,
    validate_analysis_bundle_record,
)


def test_analysis_bundle_record_accepts_valid_record() -> None:
    record = analysis_bundle_record(
        bundle_id="bundle_000001",
        sample_id="sample_000001",
        model_output_id="output_000001",
        attribution_ids=["attr_000001"],
        view_contract_ids=["view_000001"],
    )
    assert record["format"] == ANALYSIS_BUNDLE_FORMAT
    assert record["metadata"]["schema_kind"] == "analysis_bundle"


def test_analysis_bundle_record_from_dict_round_trips() -> None:
    record = analysis_bundle_record(
        bundle_id="bundle_000001",
        sample_id="sample_000001",
        model_output_id="output_000001",
        attribution_ids=["attr_000001"],
        view_contract_ids=["view_000001"],
    )
    parsed = analysis_bundle_record_from_dict(record)
    assert isinstance(parsed, AnalysisBundleRecord)
    assert parsed.to_dict() == record


def test_analysis_bundle_record_rejects_missing_field() -> None:
    record = analysis_bundle_record(
        bundle_id="bundle_000001",
        sample_id="sample_000001",
        model_output_id="output_000001",
        attribution_ids=["attr_000001"],
        view_contract_ids=["view_000001"],
    )
    del record["sample_id"]
    with pytest.raises(AnalysisBundleContractError, match="missing required analysis bundle field"):
        validate_analysis_bundle_record(record)

import pytest

from traceleak.analysis_bundle_links import AnalysisBundleLinkError, analysis_bundle_from_records
from traceleak.attribution_export_schema import attribution_export_record
from traceleak.model_output_contract import model_output_record
from traceleak.view_contract import view_contract


def sample_model_output() -> dict:
    return model_output_record(
        sample_id="sample_000001",
        model_id="model_000001",
        consumer_mode="sequence",
        prediction={"class": "metadata_even"},
        confidence=0.75,
        metadata={"output_id": "output_000001"},
    )


def sample_attribution(*, sample_id: str = "sample_000001") -> dict:
    return attribution_export_record(
        sample_id=sample_id,
        model_id="model_000001",
        model_family="sequence_model",
        attribution_level="event",
        entity_id="evt_000001",
        score=0.5,
        rank=1,
        method="attention_weight",
        evidence_summary="event attention peak",
    )


def sample_view(*, sample_id: str = "sample_000001") -> dict:
    return view_contract(
        sample_id=sample_id,
        contract_id="view_000001",
        view_level="event",
        entity_ids=["evt_000001"],
        view_action="drop",
    )


def test_analysis_bundle_from_records_links_component_ids() -> None:
    bundle = analysis_bundle_from_records(
        bundle_id="bundle_000001",
        model_output=sample_model_output(),
        attribution_records=[sample_attribution()],
        view_contracts=[sample_view()],
    )
    assert bundle["sample_id"] == "sample_000001"
    assert bundle["model_output_id"] == "output_000001"
    assert bundle["view_contract_ids"] == ["view_000001"]


def test_analysis_bundle_from_records_rejects_attribution_sample_mismatch() -> None:
    with pytest.raises(AnalysisBundleLinkError, match="sample_id does not match"):
        analysis_bundle_from_records(
            bundle_id="bundle_000001",
            model_output=sample_model_output(),
            attribution_records=[sample_attribution(sample_id="sample_000002")],
            view_contracts=[sample_view()],
        )


def test_analysis_bundle_from_records_rejects_view_sample_mismatch() -> None:
    with pytest.raises(AnalysisBundleLinkError, match="sample_id does not match"):
        analysis_bundle_from_records(
            bundle_id="bundle_000001",
            model_output=sample_model_output(),
            attribution_records=[sample_attribution()],
            view_contracts=[sample_view(sample_id="sample_000002")],
        )

from traceleak.analysis_bundle_links import analysis_bundle_from_records
from traceleak.attribution_export_schema import attribution_export_record
from traceleak.model_output_contract import model_output_record
from traceleak.view_contract import view_contract


def test_analysis_bundle_from_records_links_component_ids() -> None:
    model_output = model_output_record(
        sample_id="sample_000001",
        model_id="model_000001",
        consumer_mode="sequence",
        prediction={"class": "metadata_even"},
        confidence=0.75,
        metadata={"output_id": "output_000001"},
    )
    attribution = attribution_export_record(
        sample_id="sample_000001",
        model_id="model_000001",
        model_family="sequence_model",
        attribution_level="event",
        entity_id="evt_000001",
        score=0.5,
        rank=1,
        method="attention_weight",
        evidence_summary="event attention peak",
    )
    view = view_contract(
        sample_id="sample_000001",
        contract_id="view_000001",
        view_level="event",
        entity_ids=["evt_000001"],
        view_action="drop",
    )
    bundle = analysis_bundle_from_records(
        bundle_id="bundle_000001",
        model_output=model_output,
        attribution_records=[attribution],
        view_contracts=[view],
    )
    assert bundle["sample_id"] == "sample_000001"
    assert bundle["model_output_id"] == "output_000001"
    assert bundle["view_contract_ids"] == ["view_000001"]

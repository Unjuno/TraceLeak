import json
from pathlib import Path


SAMPLE_PATH = Path("examples/openssl_preflight/openssl_rsa_keygen_preflight_sample.json")


def test_event_slot_review_is_declared_in_preflight_sample() -> None:
    manifest = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    stage_names = {stage["name"] for stage in manifest["pipeline_stages"]}

    assert "review_event_slots" in stage_names
    assert "reports/local/openssl_event_slots.md" in manifest["planned_artifacts"]
    assert "event_slot_review_planned" in manifest["gates"]
    assert "build_human_review_checklist" in stage_names
    assert "reports/local/openssl_human_review_checklist.md" in manifest["planned_artifacts"]
    assert "human_review_checklist_planned" in manifest["gates"]

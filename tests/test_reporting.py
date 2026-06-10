import json

from traceleak.attribution import AttributionScore
from traceleak.reporting import (
    attribution_report_dict,
    attribution_report_markdown,
    write_report_json,
    write_report_markdown,
)


def sample_report() -> dict:
    return attribution_report_dict(
        target="synthetic-example",
        view="redacted",
        metric="DeltaH",
        score=4.0,
        attributions=[
            AttributionScore(
                contribution=3.0,
                group_id="example_branch_event",
                group_type="branch",
                evidence=("ablation",),
                location="target.c:21",
            )
        ],
        notes=["synthetic example"],
    )


def test_attribution_report_dict_is_json_serializable() -> None:
    report = sample_report()
    encoded = json.dumps(report)
    assert "example_branch_event" in encoded


def test_attribution_report_markdown_contains_ranking() -> None:
    markdown = attribution_report_markdown(sample_report())
    assert "# TraceLeak Attribution Report" in markdown
    assert "example_branch_event" in markdown
    assert "target.c:21" in markdown


def test_write_report_json(tmp_path) -> None:
    path = tmp_path / "report.json"
    write_report_json(path, sample_report())
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["target"] == "synthetic-example"


def test_write_report_markdown(tmp_path) -> None:
    path = tmp_path / "report.md"
    write_report_markdown(path, sample_report())
    assert path.read_text(encoding="utf-8").startswith("# TraceLeak Attribution Report")

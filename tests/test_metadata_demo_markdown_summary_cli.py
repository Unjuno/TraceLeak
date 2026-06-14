import json

from scripts import metadata_demo_markdown_summary as cli
from traceleak.metadata_demo_token_ranking import build_metadata_demo_token_ranking


def write_inputs(tmp_path, metadata_demo_artifacts):
    ranking = build_metadata_demo_token_ranking(
        demo_manifest=metadata_demo_artifacts["demo_manifest"],
        nn_result=metadata_demo_artifacts["nn_result"],
    )
    paths = {}
    for key, payload in {
        "summary": metadata_demo_artifacts["demo_summary"],
        "manifest": metadata_demo_artifacts["demo_manifest"],
        "ranking": ranking,
    }.items():
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = path
    return paths


def test_metadata_demo_markdown_summary_cli_writes_markdown(tmp_path, monkeypatch, metadata_demo_artifacts) -> None:
    paths = write_inputs(tmp_path, metadata_demo_artifacts)
    out_path = tmp_path / "summary.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "metadata_demo_markdown_summary",
            "--summary",
            str(paths["summary"]),
            "--manifest",
            str(paths["manifest"]),
            "--ranking",
            str(paths["ranking"]),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 0
    markdown = out_path.read_text(encoding="utf-8")
    assert "# Metadata Demo Summary" in markdown
    assert "## Top ranked demo tokens" in markdown


def test_metadata_demo_markdown_summary_cli_rejects_bad_manifest(tmp_path, monkeypatch, metadata_demo_artifacts) -> None:
    paths = write_inputs(tmp_path, metadata_demo_artifacts)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    manifest["sample_digest"] = "sha256:other"
    paths["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
    out_path = tmp_path / "summary.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "metadata_demo_markdown_summary",
            "--summary",
            str(paths["summary"]),
            "--manifest",
            str(paths["manifest"]),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 1
    assert not out_path.exists()

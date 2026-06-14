import json

from scripts import validate_openssl_model_sequence_metadata_demo_manifest as cli
from traceleak.openssl_metadata_demo_chain import build_openssl_metadata_demo_chain


def write_artifacts(tmp_path):
    artifacts = build_openssl_metadata_demo_chain(epochs=20)
    paths = {}
    for key in [
        "demo_summary",
        "baseline_result",
        "nn_result",
        "metadata_sample",
        "model_preflight",
        "demo_manifest",
    ]:
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps(artifacts[key]), encoding="utf-8")
        paths[key] = path
    return paths


def test_validate_metadata_demo_manifest_cli_builds_manifest(tmp_path, monkeypatch) -> None:
    paths = write_artifacts(tmp_path)
    out_path = tmp_path / "built-demo-manifest.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_metadata_demo_manifest",
            "--summary",
            str(paths["demo_summary"]),
            "--baseline-result",
            str(paths["baseline_result"]),
            "--nn-result",
            str(paths["nn_result"]),
            "--sample",
            str(paths["metadata_sample"]),
            "--model-preflight",
            str(paths["model_preflight"]),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["format"] == "traceleak.openssl_model_sequence_metadata_demo_manifest.v1"
    assert payload["phase"] == "P26"


def test_validate_metadata_demo_manifest_cli_rejects_bad_manifest(tmp_path, monkeypatch) -> None:
    paths = write_artifacts(tmp_path)
    manifest = json.loads(paths["demo_manifest"].read_text(encoding="utf-8"))
    manifest["public_statement"]["openssl_leakage_claim"] = True
    paths["demo_manifest"].write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_openssl_model_sequence_metadata_demo_manifest",
            "--summary",
            str(paths["demo_summary"]),
            "--baseline-result",
            str(paths["baseline_result"]),
            "--nn-result",
            str(paths["nn_result"]),
            "--sample",
            str(paths["metadata_sample"]),
            "--model-preflight",
            str(paths["model_preflight"]),
            "--manifest",
            str(paths["demo_manifest"]),
        ],
    )

    assert cli.main() == 1

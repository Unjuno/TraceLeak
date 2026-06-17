import json

import pytest

from scripts.build_path_deep_sample import build_path_deep_sample
from traceleak.deep_program_dataset import DEEP_PROGRAM_DATASET_FORMAT
from traceleak.path_manifest_scanner import PATH_MANIFEST_FORMAT, PathManifestScannerError, scan_path_manifest


def test_scan_path_manifest_collects_relative_source_paths(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    (tmp_path / "ssl" / "statem").mkdir(parents=True)
    (tmp_path / "crypto" / "bn" / "bn_lib.c").write_text("", encoding="utf-8")
    (tmp_path / "ssl" / "statem" / "statem_lib.c").write_text("", encoding="utf-8")

    manifest = scan_path_manifest(root=tmp_path)

    assert manifest["format"] == PATH_MANIFEST_FORMAT
    assert manifest["content_read_enabled"] is False
    assert manifest["path_records"] == [
        {"path": "crypto/bn/bn_lib.c", "role": "bignum"},
        {"path": "ssl/statem/statem_lib.c", "role": "ssl"},
    ]


def test_build_path_deep_sample_from_scanned_tree(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    (tmp_path / "ssl" / "statem").mkdir(parents=True)
    (tmp_path / "crypto" / "bn" / "bn_lib.c").write_text("", encoding="utf-8")
    (tmp_path / "ssl" / "statem" / "statem_lib.c").write_text("", encoding="utf-8")
    output_path = tmp_path / "sample.json"

    payload = build_path_deep_sample(
        manifest_path=None,
        root=tmp_path,
        output_path=output_path,
        sample_id="path_sample_000001",
        label="path_sample",
    )
    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload == written
    assert written["format"] == DEEP_PROGRAM_DATASET_FORMAT
    assert len(written["program_events"]) == 2
    assert written["variable_state_sequence"]
    assert written["dependency_graph"]["nodes"]


def test_scan_path_manifest_rejects_empty_tree(tmp_path) -> None:
    with pytest.raises(PathManifestScannerError, match="no matching paths found"):
        scan_path_manifest(root=tmp_path)

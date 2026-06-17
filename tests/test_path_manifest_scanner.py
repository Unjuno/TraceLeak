import pytest

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


def test_scan_path_manifest_rejects_empty_tree(tmp_path) -> None:
    with pytest.raises(PathManifestScannerError, match="no matching paths found"):
        scan_path_manifest(root=tmp_path)

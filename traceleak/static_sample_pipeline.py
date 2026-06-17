"""Pipeline helper for filesystem scan to static DeepProgramSample."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from traceleak.path_manifest_scanner import scan_path_manifest
from traceleak.static_program_sample import build_static_program_deep_sample


def build_static_sample_from_tree(
    *,
    root: Path,
    sample_id: str,
    label: str = "static_program_sample",
    max_paths: int = 64,
    max_lines_per_file: int = 400,
) -> dict[str, Any]:
    """Scan a local tree and build a static DeepProgramSample from selected paths."""

    manifest = scan_path_manifest(root=root, max_paths=max_paths)
    relative_paths = [record["path"] for record in manifest["path_records"]]
    return build_static_program_deep_sample(
        root=root,
        relative_paths=relative_paths,
        sample_id=sample_id,
        label=label,
        max_lines_per_file=max_lines_per_file,
    )

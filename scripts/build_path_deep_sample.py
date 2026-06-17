#!/usr/bin/env python3
"""Build a path-based DeepProgramSample JSON artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from traceleak.openssl_path_deep_sample import build_openssl_path_deep_program_sample
from traceleak.path_manifest_scanner import scan_path_manifest


class BuildPathDeepSampleError(ValueError):
    """Raised when path DeepProgramSample generation fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build path-based DeepProgramSample JSON.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument("--root", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--label", default="path_sample")
    parser.add_argument("--max-paths", type=int, default=512)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_path_deep_sample(
            manifest_path=args.manifest,
            root=args.root,
            output_path=args.out,
            sample_id=args.sample_id,
            label=args.label,
            max_paths=args.max_paths,
        )
    except (BuildPathDeepSampleError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote DeepProgramSample: {args.out} ({len(payload['program_events'])} event(s))")
    return 0


def build_path_deep_sample(
    *,
    manifest_path: Path | None,
    root: Path | None,
    output_path: Path,
    sample_id: str,
    label: str,
    max_paths: int = 512,
) -> dict[str, Any]:
    if manifest_path is not None:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    elif root is not None:
        manifest = scan_path_manifest(root=root, max_paths=max_paths)
    else:
        raise BuildPathDeepSampleError("manifest_path or root is required")
    return build_from_manifest_payload(
        manifest=manifest,
        output_path=output_path,
        sample_id=sample_id,
        label=label,
    )


def build_from_manifest(
    *,
    manifest_path: Path,
    output_path: Path,
    sample_id: str,
    label: str,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return build_from_manifest_payload(
        manifest=manifest,
        output_path=output_path,
        sample_id=sample_id,
        label=label,
    )


def build_from_manifest_payload(
    *,
    manifest: Any,
    output_path: Path,
    sample_id: str,
    label: str,
) -> dict[str, Any]:
    path_records = _path_records_from_manifest(manifest)
    payload = build_openssl_path_deep_program_sample(
        sample_id=sample_id,
        path_records=path_records,
        label=label,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _path_records_from_manifest(manifest: Any) -> list[dict[str, Any]]:
    if isinstance(manifest, list):
        return [dict(record) for record in manifest]
    if isinstance(manifest, dict) and isinstance(manifest.get("path_records"), list):
        return [dict(record) for record in manifest["path_records"]]
    raise BuildPathDeepSampleError("manifest must be a list or an object with path_records")


if __name__ == "__main__":
    raise SystemExit(main())

"""Filesystem path manifest scanner for DeepProgramSample inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

PATH_MANIFEST_FORMAT = "traceleak.path_manifest.v1"
DEFAULT_PATH_SUFFIXES: tuple[str, ...] = (".c", ".h")


class PathManifestScannerError(ValueError):
    """Raised when a path manifest cannot be scanned."""


def scan_path_manifest(
    *,
    root: Path,
    include_prefixes: Iterable[str] = ("crypto", "ssl", "providers"),
    suffixes: Iterable[str] = DEFAULT_PATH_SUFFIXES,
    max_paths: int = 512,
) -> dict:
    """Scan a local tree into public-safe path records.

    The scanner records only relative paths and derived roles. It does not read
    or store file contents.
    """

    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise PathManifestScannerError("root must be an existing directory")
    suffix_tuple = tuple(suffixes)
    prefix_tuple = tuple(prefix.strip("/") for prefix in include_prefixes)
    if not suffix_tuple:
        raise PathManifestScannerError("suffixes must be non-empty")
    if not prefix_tuple:
        raise PathManifestScannerError("include_prefixes must be non-empty")
    if not isinstance(max_paths, int) or max_paths <= 0:
        raise PathManifestScannerError("max_paths must be a positive integer")

    records: list[dict[str, str]] = []
    for path in sorted(root_path.rglob("*")):
        if not path.is_file() or path.suffix not in suffix_tuple:
            continue
        relative_path = path.relative_to(root_path).as_posix()
        if not _matches_prefix(relative_path, prefix_tuple):
            continue
        records.append({"path": relative_path, "role": _role_from_path(relative_path)})
        if len(records) >= max_paths:
            break
    if not records:
        raise PathManifestScannerError("no matching paths found")
    return {
        "format": PATH_MANIFEST_FORMAT,
        "root_name": root_path.name,
        "content_read_enabled": False,
        "path_records": records,
    }


def _matches_prefix(relative_path: str, prefixes: tuple[str, ...]) -> bool:
    return any(relative_path == prefix or relative_path.startswith(prefix + "/") for prefix in prefixes)


def _role_from_path(path: str) -> str:
    lower = path.lower()
    if "/bn/" in lower or lower.endswith("bn.h") or "bn_" in lower:
        return "bignum"
    if "/evp/" in lower or lower.endswith("evp.h"):
        return "evp"
    if "/ssl/" in lower or lower.startswith("ssl/"):
        return "ssl"
    if "/providers/" in lower or lower.startswith("providers/"):
        return "provider"
    return "generic"

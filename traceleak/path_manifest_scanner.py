"""Filesystem path manifest scanner for DeepProgramSample inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

PATH_MANIFEST_FORMAT = "traceleak.path_manifest.v1"
DEFAULT_PATH_SUFFIXES: tuple[str, ...] = (".c", ".h")
DEFAULT_PATH_EXCLUDES: tuple[str, ...] = (
    "test/",
    "fuzz/",
    "demos/",
    "doc/",
    "apps/",
)
PATH_PRIORITY_PREFIXES: tuple[tuple[str, int], ...] = (
    ("crypto/bn/", 0),
    ("crypto/rsa/", 1),
    ("crypto/evp/", 2),
    ("providers/", 3),
    ("ssl/statem/", 4),
    ("ssl/", 5),
    ("crypto/", 6),
)


class PathManifestScannerError(ValueError):
    """Raised when a path manifest cannot be scanned."""


def scan_path_manifest(
    *,
    root: Path,
    include_prefixes: Iterable[str] = ("crypto", "ssl", "providers"),
    exclude_prefixes: Iterable[str] = DEFAULT_PATH_EXCLUDES,
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
    exclude_tuple = tuple(prefix.strip("/") for prefix in exclude_prefixes)
    if not suffix_tuple:
        raise PathManifestScannerError("suffixes must be non-empty")
    if not prefix_tuple:
        raise PathManifestScannerError("include_prefixes must be non-empty")
    if not isinstance(max_paths, int) or max_paths <= 0:
        raise PathManifestScannerError("max_paths must be a positive integer")

    candidates: list[str] = []
    for path in root_path.rglob("*"):
        if not path.is_file() or path.suffix not in suffix_tuple:
            continue
        relative_path = path.relative_to(root_path).as_posix()
        if not _matches_prefix(relative_path, prefix_tuple):
            continue
        if _matches_prefix(relative_path, exclude_tuple):
            continue
        candidates.append(relative_path)

    records = [_record_from_path(relative_path) for relative_path in _sorted_paths(candidates)[:max_paths]]
    if not records:
        raise PathManifestScannerError("no matching paths found")
    return {
        "format": PATH_MANIFEST_FORMAT,
        "root_name": root_path.name,
        "content_read_enabled": False,
        "path_records": records,
    }


def _record_from_path(relative_path: str) -> dict[str, str]:
    return {
        "path": relative_path,
        "role": _role_from_path(relative_path),
    }


def _sorted_paths(paths: list[str]) -> list[str]:
    return sorted(paths, key=lambda path: (_priority_from_path(path), path))


def _matches_prefix(relative_path: str, prefixes: tuple[str, ...]) -> bool:
    return any(relative_path == prefix or relative_path.startswith(prefix + "/") for prefix in prefixes)


def _priority_from_path(path: str) -> int:
    lower = path.lower()
    for prefix, priority in PATH_PRIORITY_PREFIXES:
        if lower.startswith(prefix):
            return priority
    return len(PATH_PRIORITY_PREFIXES)


def _role_from_path(path: str) -> str:
    lower = path.lower()
    if "/bn/" in lower or lower.endswith("bn.h") or "bn_" in lower:
        return "bignum"
    if "/rsa/" in lower or "rsa" in lower:
        return "rsa"
    if "/evp/" in lower or lower.endswith("evp.h"):
        return "evp"
    if "rand" in lower or "drbg" in lower:
        return "random"
    if "/ssl/" in lower or lower.startswith("ssl/"):
        return "ssl"
    if "/providers/" in lower or lower.startswith("providers/"):
        return "provider"
    return "generic"

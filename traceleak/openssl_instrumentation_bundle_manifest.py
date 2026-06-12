"""Build and validate deterministic manifests for OpenSSL instrumentation bundles.

The manifest records the expected review-only bundle files with size and SHA-256
checksums. It is a reproducibility/integrity layer over the bundle validator and
does not build, run, instrument, patch, compile, or trace OpenSSL.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from traceleak.openssl_instrumentation_bundle import (
    OpenSSLInstrumentationBundleError,
    validate_openssl_instrumentation_bundle,
)
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, validate_openssl_trace_contract

BUNDLE_MANIFEST_FORMAT = "traceleak.openssl_instrumentation_bundle_manifest.v1"
EXPECTED_BUNDLE_RELATIVE_FILES = [
    "openssl_instrumentation_chain_summary.json",
    "openssl_instrumentation_chain_summary.md",
    "openssl_instrumentation_stub.json",
    "openssl_instrumentation_stub.md",
    "openssl_source_edit_proposal.json",
    "openssl_source_edit_proposal.md",
    "openssl_event_emitter_artifact.json",
    "openssl_event_emitter_artifact.md",
    "openssl_event_emitter_files/traceleak_openssl_event.h",
    "openssl_event_emitter_files/traceleak_openssl_event.c",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_summary.json",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_summary.md",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_events.jsonl",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_event_stream_report.json",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_event_stream_report.md",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_model_sequence_sample.json",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_acceptance_report.json",
    "openssl_event_emitter_self_check/openssl_event_emitter_self_check_acceptance_report.md",
    "openssl_redacted_event_stream_report.json",
    "openssl_redacted_event_stream_report.md",
    "openssl_model_sequence_sample.json",
    "openssl_trace_sample_acceptance_report.json",
    "openssl_trace_sample_acceptance_report.md",
]


class OpenSSLInstrumentationBundleManifestError(ValueError):
    """Raised when an OpenSSL instrumentation bundle manifest is invalid."""


def build_openssl_instrumentation_bundle_manifest(
    *,
    contract: dict[str, Any],
    bundle_dir: str | Path,
) -> dict[str, Any]:
    """Build a deterministic checksum manifest for a validated bundle."""

    validation_report = _validate_contract_and_bundle(contract=contract, bundle_dir=bundle_dir)
    base_dir = Path(bundle_dir)
    files = [_file_entry(base_dir, relative_path) for relative_path in EXPECTED_BUNDLE_RELATIVE_FILES]
    total_size = sum(int(entry["size_bytes"]) for entry in files)
    manifest = {
        "format": BUNDLE_MANIFEST_FORMAT,
        "status": "bundle_manifest_ready",
        "validation_status": validation_report["status"],
        "contract_id": contract["contract_id"],
        "target": contract["target"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_collection_mode": "redacted",
        "bundle_dir": str(base_dir),
        "file_count": len(files),
        "total_size_bytes": total_size,
        "bundle_sha256": _bundle_digest(files),
        "files": files,
        "notes": [
            "Manifest checks only the review-only TraceLeak bundle artifacts.",
            "A matching manifest is not proof of an actual OpenSSL run.",
        ],
    }
    validate_openssl_instrumentation_bundle_manifest(
        contract=contract,
        bundle_dir=bundle_dir,
        manifest=manifest,
    )
    return manifest


def validate_openssl_instrumentation_bundle_manifest(
    *,
    contract: dict[str, Any],
    bundle_dir: str | Path,
    manifest: dict[str, Any],
) -> None:
    """Validate a saved bundle manifest against current bundle files."""

    validation_report = _validate_contract_and_bundle(contract=contract, bundle_dir=bundle_dir)
    _require_equal(manifest.get("format"), BUNDLE_MANIFEST_FORMAT, "format")
    _require_equal(manifest.get("status"), "bundle_manifest_ready", "status")
    _require_equal(manifest.get("validation_status"), validation_report["status"], "validation_status")
    _require_equal(manifest.get("contract_id"), contract["contract_id"], "contract_id")
    _require_equal(manifest.get("target"), contract["target"], "target")
    _require_equal(manifest.get("target_version"), contract["target_version"], "target_version")
    _require_equal(manifest.get("source_pin"), contract["source_pin"], "source_pin")
    _require_equal(manifest.get("build_id"), contract["build_id"], "build_id")
    _require_equal(manifest.get("execution_allowed"), False, "execution_allowed")
    _require_equal(manifest.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(manifest.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(manifest.get("compile_allowed"), False, "compile_allowed")
    _require_equal(manifest.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(manifest.get("trace_collection_mode"), "redacted", "trace_collection_mode")
    current_files = [_file_entry(Path(bundle_dir), relative_path) for relative_path in EXPECTED_BUNDLE_RELATIVE_FILES]
    _require_equal(manifest.get("file_count"), len(current_files), "file_count")
    _require_equal(
        manifest.get("total_size_bytes"),
        sum(int(entry["size_bytes"]) for entry in current_files),
        "total_size_bytes",
    )
    _require_equal(manifest.get("bundle_sha256"), _bundle_digest(current_files), "bundle_sha256")
    _require_equal(manifest.get("files"), current_files, "files")


def load_openssl_instrumentation_bundle_manifest(path: str | Path) -> dict[str, Any]:
    """Load a bundle manifest from JSON."""

    manifest_path = Path(path)
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OpenSSLInstrumentationBundleManifestError(f"bundle manifest not found: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise OpenSSLInstrumentationBundleManifestError(f"invalid JSON in {manifest_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OpenSSLInstrumentationBundleManifestError("bundle manifest must be a JSON object")
    return value


def write_openssl_instrumentation_bundle_manifest_json(path: str | Path, manifest: dict[str, Any]) -> None:
    """Write bundle manifest JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_instrumentation_bundle_manifest_markdown(path: str | Path, manifest: dict[str, Any]) -> None:
    """Write bundle manifest Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(openssl_instrumentation_bundle_manifest_markdown(manifest), encoding="utf-8")


def openssl_instrumentation_bundle_manifest_markdown(manifest: dict[str, Any]) -> str:
    """Render bundle manifest as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Instrumentation Bundle Manifest",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Validation status: `{manifest['validation_status']}`",
        f"- Contract: `{manifest['contract_id']}`",
        f"- Target: `{manifest['target']}`",
        f"- Target version: `{manifest['target_version']}`",
        f"- Source pin: `{manifest['source_pin']}`",
        f"- Build ID: `{manifest['build_id']}`",
        f"- Bundle SHA-256: `{manifest['bundle_sha256']}`",
        f"- File count: `{manifest['file_count']}`",
        f"- Total size bytes: `{manifest['total_size_bytes']}`",
        f"- Execution allowed: `{str(manifest['execution_allowed']).lower()}`",
        f"- Patch application allowed: `{str(manifest['patch_application_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(manifest['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Files",
        "",
    ]
    lines.extend(
        f"- `{entry['relative_path']}` `{entry['sha256']}` `{entry['size_bytes']}` bytes"
        for entry in manifest["files"]
    )
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in manifest["notes"])
    lines.append("")
    return "\n".join(lines)


def _validate_contract_and_bundle(*, contract: dict[str, Any], bundle_dir: str | Path) -> dict[str, Any]:
    try:
        validate_openssl_trace_contract(contract)
        return validate_openssl_instrumentation_bundle(contract=contract, bundle_dir=bundle_dir)
    except (OpenSSLTraceContractError, OpenSSLInstrumentationBundleError) as exc:
        raise OpenSSLInstrumentationBundleManifestError(str(exc)) from exc


def _file_entry(base_dir: Path, relative_path: str) -> dict[str, Any]:
    path = base_dir / relative_path
    if not path.exists():
        raise OpenSSLInstrumentationBundleManifestError(f"expected bundle file not found: {path}")
    if not path.is_file():
        raise OpenSSLInstrumentationBundleManifestError(f"expected bundle path is not a file: {path}")
    data = path.read_bytes()
    return {
        "relative_path": relative_path,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _bundle_digest(files: list[dict[str, Any]]) -> str:
    payload = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLInstrumentationBundleManifestError(f"{name} must be {expected!r}")

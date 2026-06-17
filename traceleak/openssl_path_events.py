"""Convert OpenSSL path records into ProgramEvent records."""

from __future__ import annotations

from typing import Any

from traceleak.program_event_schema import validate_program_events

OPENSSL_PATH_EVENT_FORMAT = "traceleak.openssl_path_event.v1"


class OpenSSLPathEventError(ValueError):
    """Raised when path records cannot be converted."""


def openssl_path_records_to_program_events(path_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert public path manifest records into ProgramEvent records."""

    if not isinstance(path_records, list) or not path_records:
        raise OpenSSLPathEventError("path_records must be a non-empty list")
    events = [_event_from_path_record(record, index=index) for index, record in enumerate(path_records, start=1)]
    validate_program_events(events)
    return events


def _event_from_path_record(record: dict[str, Any], *, index: int) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise OpenSSLPathEventError("path record must be an object")
    path = _require_path(record.get("path"))
    module = _module_from_path(path)
    stem = _stem_from_path(path)
    role = str(record.get("role") or "generic")
    return {
        "event_id": f"openssl_path_{index:06d}",
        "time_step": index,
        "event_type": "metadata",
        "operation": "metadata",
        "function": stem,
        "source_location": {"file": path, "line": None},
        "variable_reads": [f"module:{module}", f"role:{role}"],
        "variable_writes": [f"path:{stem}"],
        "value_class": "metadata",
        "dependency_tags": ["openssl_path", "manifest_record"],
        "control_context": {"module": module, "role": role},
        "metadata": {"path": path, "module": module, "role": role},
    }


def _module_from_path(path: str) -> str:
    parts = [part for part in path.replace("\\", "/").split("/") if part]
    return parts[0] if parts else "unknown"


def _stem_from_path(path: str) -> str:
    name = path.replace("\\", "/").split("/")[-1]
    return name.rsplit(".", 1)[0] or "unknown"


def _require_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLPathEventError("path must be a non-empty string")
    parts = value.replace("\\", "/").split("/")
    if ".." in parts:
        raise OpenSSLPathEventError("path must not contain parent traversal")
    return value

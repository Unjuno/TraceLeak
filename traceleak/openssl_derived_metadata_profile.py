"""Profile boundary for OpenSSL-derived metadata ingestion."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from traceleak.openssl_derived_metadata_adapter import (
    OPENSSL_DERIVED_METADATA_INPUT_FORMAT,
    validate_openssl_derived_metadata_input,
)

OPENSSL_DERIVED_METADATA_PROFILE_FORMAT = "traceleak.openssl_derived_metadata_profile.v1"
OPENSSL_DERIVED_METADATA_PROFILE_PHASE = "P96"
DEFAULT_TARGET_DECISION = "constant_time_helper_misuse_path"
PROFILE_TO_ADAPTER_BRIDGE_PHASE = "P98"
REQUIRED_TOP_LEVEL_FIELDS = {
    "format",
    "phase",
    "target_decision",
    "metadata_only",
    "payload_free",
    "public_safe",
    "label_name",
    "source_pin_digest",
    "records",
}
REQUIRED_RECORD_FIELDS = {"run_id", "source_region_token", "transition_token", "label"}
OPTIONAL_SAFE_RECORD_FIELDS = {
    "function_token",
    "module_token",
    "operation_family",
    "observation_class",
    "metadata_tags",
}
FORBIDDEN_PROFILE_FIELDS = {
    "source_text",
    "diff_text",
    "command_text",
    "build_output",
    "execution_output",
    "raw_capture",
    "payload",
    "private_key",
    "secret",
    "secret_value",
    "value_raw",
    "memory_dump",
    "trace_bytes",
    "stdout",
    "stderr",
}
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")


class OpenSSLDerivedMetadataProfileError(ValueError):
    """Raised when a derived metadata profile input is invalid."""


def default_openssl_derived_metadata_profile_records() -> list[dict[str, Any]]:
    """Return a balanced default record set for local Level 6 checks."""

    return [
        {
            "run_id": "openssl-derived-profile-0000",
            "source_region_token": "bn_window_path_a",
            "transition_token": "ct_select_branch_a",
            "function_token": "bn_mod_exp_family",
            "module_token": "crypto_bn",
            "operation_family": "rsa_private_path",
            "observation_class": "branch_metadata",
            "metadata_tags": {"profile": "level6", "bucket": "a"},
            "label": "candidate_a",
        },
        {
            "run_id": "openssl-derived-profile-0001",
            "source_region_token": "bn_window_path_a2",
            "transition_token": "ct_select_branch_a2",
            "function_token": "bn_mod_exp_family",
            "module_token": "crypto_bn",
            "operation_family": "rsa_private_path",
            "observation_class": "branch_metadata",
            "metadata_tags": {"profile": "level6", "bucket": "a"},
            "label": "candidate_a",
        },
        {
            "run_id": "openssl-derived-profile-0002",
            "source_region_token": "bn_window_path_b",
            "transition_token": "ct_select_branch_b",
            "function_token": "bn_mod_exp_family",
            "module_token": "crypto_bn",
            "operation_family": "rsa_private_path",
            "observation_class": "access_metadata",
            "metadata_tags": {"profile": "level6", "bucket": "b"},
            "label": "candidate_b",
        },
        {
            "run_id": "openssl-derived-profile-0003",
            "source_region_token": "bn_window_path_b2",
            "transition_token": "ct_select_branch_b2",
            "function_token": "bn_mod_exp_family",
            "module_token": "crypto_bn",
            "operation_family": "rsa_private_path",
            "observation_class": "access_metadata",
            "metadata_tags": {"profile": "level6", "bucket": "b"},
            "label": "candidate_b",
        },
    ]


def build_openssl_derived_metadata_profile_input(
    *,
    records: list[dict[str, Any]] | None = None,
    source_pin_digest: str = "sha256:source-pin",
    label_name: str = "profile_bucket",
    target_decision: str = DEFAULT_TARGET_DECISION,
) -> dict[str, Any]:
    """Build a Level 6 metadata-only ingestion profile input."""

    payload = {
        "format": OPENSSL_DERIVED_METADATA_PROFILE_FORMAT,
        "phase": OPENSSL_DERIVED_METADATA_PROFILE_PHASE,
        "target_decision": target_decision,
        "metadata_only": True,
        "payload_free": True,
        "public_safe": True,
        "label_name": label_name,
        "source_pin_digest": source_pin_digest,
        "required_record_fields": sorted(REQUIRED_RECORD_FIELDS),
        "optional_safe_record_fields": sorted(OPTIONAL_SAFE_RECORD_FIELDS),
        "forbidden_fields": sorted(FORBIDDEN_PROFILE_FIELDS),
        "records": _normalize_records(records or default_openssl_derived_metadata_profile_records()),
    }
    validate_openssl_derived_metadata_profile_input(payload)
    return payload


def validate_openssl_derived_metadata_profile_input(payload: dict[str, Any]) -> None:
    """Validate Level 6 OpenSSL-derived metadata profile input."""

    if not isinstance(payload, dict):
        raise OpenSSLDerivedMetadataProfileError("profile input must be an object")
    _reject_forbidden(payload, "profile")
    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(payload))
    if missing:
        raise OpenSSLDerivedMetadataProfileError(f"missing required top-level fields: {missing}")
    _eq(payload.get("format"), OPENSSL_DERIVED_METADATA_PROFILE_FORMAT, "format")
    _eq(payload.get("phase"), OPENSSL_DERIVED_METADATA_PROFILE_PHASE, "phase")
    _eq(payload.get("target_decision"), DEFAULT_TARGET_DECISION, "target_decision")
    _eq(payload.get("metadata_only"), True, "metadata_only")
    _eq(payload.get("payload_free"), True, "payload_free")
    _eq(payload.get("public_safe"), True, "public_safe")
    _safe_token(payload.get("label_name"), "label_name")
    _safe_digest(payload.get("source_pin_digest"), "source_pin_digest")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) < 4:
        raise OpenSSLDerivedMetadataProfileError("records must contain at least four entries")
    seen_run_ids: set[str] = set()
    label_counts: Counter[str] = Counter()
    for index, item in enumerate(records):
        _validate_profile_record(item, index, seen_run_ids, label_counts)
    if len(label_counts) < 2:
        raise OpenSSLDerivedMetadataProfileError("records must contain at least two labels")
    if min(label_counts.values()) < 2:
        raise OpenSSLDerivedMetadataProfileError("each label must have at least two records")


def adapt_openssl_derived_metadata_profile_to_adapter_input(
    profile_input: dict[str, Any],
) -> dict[str, Any]:
    """Convert a validated Level 6 profile input into the existing adapter input shape."""

    validate_openssl_derived_metadata_profile_input(profile_input)
    records = []
    for item in profile_input["records"]:
        records.append(
            {
                "run_id": item["run_id"],
                "source_region_token": item["source_region_token"],
                "transition_token": item["transition_token"],
                "label": item["label"],
            }
        )
    adapter_input = {
        "format": OPENSSL_DERIVED_METADATA_INPUT_FORMAT,
        "authoring_phase": PROFILE_TO_ADAPTER_BRIDGE_PHASE,
        "source_pin_digest": profile_input["source_pin_digest"],
        "target_decision": profile_input["target_decision"],
        "metadata_only": True,
        "payload_free": True,
        "label_name": profile_input["label_name"],
        "records": records,
    }
    validate_openssl_derived_metadata_input(adapter_input)
    return adapter_input


def write_openssl_derived_metadata_profile_input(path: Path, payload: dict[str, Any]) -> None:
    """Write Level 6 profile input JSON."""

    validate_openssl_derived_metadata_profile_input(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_derived_metadata_profile_adapter_input(path: Path, payload: dict[str, Any]) -> None:
    """Write bridged adapter input JSON."""

    validate_openssl_derived_metadata_input(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(records, list):
        raise OpenSSLDerivedMetadataProfileError("records must be a list")
    output: list[dict[str, Any]] = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise OpenSSLDerivedMetadataProfileError(f"records[{index}] must be an object")
        _reject_forbidden(item, f"records[{index}]")
        missing = sorted(REQUIRED_RECORD_FIELDS - set(item))
        if missing:
            raise OpenSSLDerivedMetadataProfileError(f"records[{index}] missing fields: {missing}")
        normalized = {
            "run_id": _stringify(item["run_id"], f"records[{index}].run_id"),
            "source_region_token": _stringify(
                item["source_region_token"], f"records[{index}].source_region_token"
            ),
            "transition_token": _stringify(
                item["transition_token"], f"records[{index}].transition_token"
            ),
            "label": _stringify(item["label"], f"records[{index}].label"),
        }
        for key in sorted(OPTIONAL_SAFE_RECORD_FIELDS):
            if key in item:
                value = item[key]
                if key == "metadata_tags":
                    normalized[key] = _safe_metadata_tags(value, f"records[{index}].metadata_tags")
                else:
                    normalized[key] = _stringify(value, f"records[{index}].{key}")
        output.append(normalized)
    return output


def _validate_profile_record(
    item: Any,
    index: int,
    seen_run_ids: set[str],
    label_counts: Counter[str],
) -> None:
    if not isinstance(item, dict):
        raise OpenSSLDerivedMetadataProfileError(f"records[{index}] must be an object")
    _reject_forbidden(item, f"records[{index}]")
    missing = sorted(REQUIRED_RECORD_FIELDS - set(item))
    if missing:
        raise OpenSSLDerivedMetadataProfileError(f"records[{index}] missing fields: {missing}")
    extra_fields = set(item) - REQUIRED_RECORD_FIELDS - OPTIONAL_SAFE_RECORD_FIELDS
    if extra_fields:
        raise OpenSSLDerivedMetadataProfileError(
            f"records[{index}] contains unsupported fields: {sorted(extra_fields)}"
        )
    run_id = _safe_token(item["run_id"], f"records[{index}].run_id", pattern=RUN_ID_PATTERN)
    if run_id in seen_run_ids:
        raise OpenSSLDerivedMetadataProfileError("run_id values must be unique")
    seen_run_ids.add(run_id)
    _safe_token(item["source_region_token"], f"records[{index}].source_region_token")
    _safe_token(item["transition_token"], f"records[{index}].transition_token")
    label = _safe_token(item["label"], f"records[{index}].label")
    for key in sorted(OPTIONAL_SAFE_RECORD_FIELDS - {"metadata_tags"}):
        if key in item:
            _safe_token(item[key], f"records[{index}].{key}")
    if "metadata_tags" in item:
        _safe_metadata_tags(item["metadata_tags"], f"records[{index}].metadata_tags")
    label_counts[label] += 1


def _safe_metadata_tags(value: Any, name: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise OpenSSLDerivedMetadataProfileError(f"{name} must be an object")
    result: dict[str, str] = {}
    for key, child in value.items():
        safe_key = _safe_token(key, f"{name}.key")
        safe_value = _safe_token(child, f"{name}.{safe_key}")
        result[safe_key] = safe_value
    return result


def _reject_forbidden(value: Any, name: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_PROFILE_FIELDS:
                raise OpenSSLDerivedMetadataProfileError(f"{name} must not contain {key}")
            _reject_forbidden(child, f"{name}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden(child, f"{name}[{index}]")


def _safe_digest(value: Any, name: str) -> str:
    text = _stringify(value, name)
    if not text.startswith("sha256:"):
        raise OpenSSLDerivedMetadataProfileError(f"{name} must start with 'sha256:'")
    return text


def _safe_token(value: Any, name: str, pattern: re.Pattern[str] = TOKEN_PATTERN) -> str:
    text = _stringify(value, name)
    if not pattern.fullmatch(text):
        raise OpenSSLDerivedMetadataProfileError(f"{name} contains unsupported characters")
    if ".." in Path(text).parts or "/" in text or "\\" in text or Path(text).is_absolute():
        raise OpenSSLDerivedMetadataProfileError(f"{name} must not be path-like")
    return text


def _stringify(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OpenSSLDerivedMetadataProfileError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLDerivedMetadataProfileError(f"{name} must be {expected!r}")

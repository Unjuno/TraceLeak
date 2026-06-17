"""Static C-file ProgramEvent extractor."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from traceleak.c_call_events import call_targets_from_line
from traceleak.program_event_schema import validate_program_events

C_STATIC_EVENT_FORMAT = "traceleak.c_static_event.v1"

_ASSIGNMENT_RE = re.compile(r"(?<![=!<>])=(?!=)")
_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_FUNCTION_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")

C_RESERVED_WORDS: set[str] = {
    "break", "case", "char", "const", "continue", "default", "do", "else",
    "enum", "extern", "for", "goto", "if", "int", "long", "return", "short",
    "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned",
    "void", "volatile", "while",
}


class CStaticEventError(ValueError):
    """Raised when C static events cannot be extracted."""


def c_paths_to_program_events(
    *,
    root: Path,
    relative_paths: list[str],
    max_lines_per_file: int = 400,
) -> list[dict[str, Any]]:
    """Convert selected C/H files into public-safe ProgramEvent records."""

    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise CStaticEventError("root must be an existing directory")
    if not isinstance(max_lines_per_file, int) or max_lines_per_file <= 0:
        raise CStaticEventError("max_lines_per_file must be a positive integer")
    if not isinstance(relative_paths, list) or not relative_paths:
        raise CStaticEventError("relative_paths must be a non-empty list")

    events: list[dict[str, Any]] = []
    for relative_path in relative_paths:
        path = _safe_path(root_path, relative_path)
        events.extend(
            _events_from_file(
                path=path,
                relative_path=relative_path,
                start_index=len(events),
                max_lines=max_lines_per_file,
            )
        )
    if not events:
        raise CStaticEventError("no C static events were extracted")
    validate_program_events(events)
    return events


def _events_from_file(
    *,
    path: Path,
    relative_path: str,
    start_index: int,
    max_lines: int,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_function = "file_scope"
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if line_number > max_lines:
            break
        normalized = _strip_inline_comment(line).strip()
        if not normalized or normalized.startswith("/*") or normalized.startswith("*"):
            continue
        maybe_function = _function_name(normalized)
        if maybe_function is not None:
            current_function = maybe_function
        reads, writes = _read_write_candidates(normalized)
        if not reads and not writes:
            continue
        line_class = _line_class(normalized)
        call_targets = call_targets_from_line(normalized)
        event_index = start_index + len(events)
        events.append(
            {
                "event_id": f"c_static_{event_index:06d}",
                "time_step": event_index + 1,
                "event_type": _event_type(normalized),
                "operation": _operation(normalized),
                "function": current_function,
                "source_location": {"file": relative_path, "line": line_number},
                "variable_reads": reads,
                "variable_writes": writes,
                "value_class": "metadata",
                "dependency_tags": ["c_static", "line_summary", f"line_class:{line_class}"],
                "control_context": {"line_class": line_class, "call_targets": call_targets},
                "metadata": {
                    "format": C_STATIC_EVENT_FORMAT,
                    "line_digest": hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16],
                    "line_length": len(normalized),
                    "call_target_count": len(call_targets),
                },
            }
        )
    return events


def _read_write_candidates(line: str) -> tuple[list[str], list[str]]:
    identifiers = _identifiers(line)
    if not identifiers:
        return [], []
    if _ASSIGNMENT_RE.search(line):
        left = line.split("=", 1)[0]
        left_ids = _identifiers(left)
        writes = left_ids[-1:] if left_ids else ["assignment_target"]
        reads = [identifier for identifier in identifiers if identifier not in set(writes)]
        return _unique_limited(reads), _unique_limited(writes)
    if line.startswith("return"):
        return _unique_limited(identifiers), ["return_value"]
    if line.startswith(("if", "for", "while", "switch")):
        return _unique_limited(identifiers), ["control_branch"]
    return _unique_limited(identifiers), ["line_observation"]


def _identifiers(line: str) -> list[str]:
    return [identifier for identifier in _IDENTIFIER_RE.findall(line) if identifier not in C_RESERVED_WORDS]


def _unique_limited(values: list[str], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def _event_type(line: str) -> str:
    if line.startswith(("if", "for", "while", "switch")):
        return "branch"
    if line.startswith("return"):
        return "return"
    if _ASSIGNMENT_RE.search(line):
        return "assign"
    if "(" in line and ")" in line:
        return "call"
    return "metadata"


def _operation(line: str) -> str:
    if line.startswith(("if", "for", "while", "switch")):
        return "branch"
    if line.startswith("return"):
        return "return"
    if _ASSIGNMENT_RE.search(line):
        return "assign"
    if "(" in line and ")" in line:
        return "call"
    return "metadata"


def _line_class(line: str) -> str:
    if _ASSIGNMENT_RE.search(line):
        return "assignment"
    if line.startswith(("if", "for", "while", "switch")):
        return "control"
    if line.startswith("return"):
        return "return"
    if "(" in line and ")" in line:
        return "call"
    return "other"


def _function_name(line: str) -> str | None:
    if line.startswith(("if", "for", "while", "switch", "return")):
        return None
    match = _FUNCTION_RE.search(line)
    if not match:
        return None
    name = match.group(1)
    return None if name in C_RESERVED_WORDS else name


def _strip_inline_comment(line: str) -> str:
    return line.split("//", 1)[0]


def _safe_path(root: Path, relative_path: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise CStaticEventError("relative_paths must contain only non-empty strings")
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise CStaticEventError("relative_paths must stay inside root")
    if not relative_path.endswith((".c", ".h")):
        raise CStaticEventError("relative_paths must point to C source or header files")
    path = (root / relative_path).resolve()
    if root not in path.parents and path != root:
        raise CStaticEventError("relative path escaped root")
    if not path.exists() or not path.is_file():
        raise CStaticEventError(f"path not found: {relative_path}")
    return path

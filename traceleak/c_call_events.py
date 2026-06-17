"""Static C call ProgramEvent extractor."""

from __future__ import annotations

import re

C_CALL_EVENT_FORMAT = "traceleak.c_call_event.v1"
_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")

_RESERVED_CALL_NAMES: set[str] = {
    "for",
    "if",
    "return",
    "sizeof",
    "switch",
    "while",
}


class CCallEventError(ValueError):
    """Raised when C call events cannot be extracted."""


def call_targets_from_line(line: str) -> list[str]:
    """Return unique call targets from one C-like line."""

    result: list[str] = []
    seen: set[str] = set()
    for name in _CALL_RE.findall(line):
        if name in _RESERVED_CALL_NAMES or name in seen:
            continue
        seen.add(name)
        result.append(name)
        if len(result) >= 8:
            break
    return result

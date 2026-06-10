"""JSONL IO helpers for TraceLeak runs."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from traceleak.schema import validate_run


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield TraceLeak run objects from a JSONL file."""

    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                run = json.loads(stripped)
            except json.JSONDecodeError as exc:  # pragma: no cover - passthrough details vary.
                raise ValueError(f"invalid JSON on line {line_number}: {exc}") from exc
            validate_run(run)
            yield run


def write_jsonl(path: str | Path, runs: Iterable[dict[str, Any]]) -> None:
    """Write TraceLeak run objects to a JSONL file after validation."""

    with Path(path).open("w", encoding="utf-8") as handle:
        for run in runs:
            validate_run(run)
            handle.write(json.dumps(run, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

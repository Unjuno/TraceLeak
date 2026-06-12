"""Inspect pinned OpenSSL source-layout manifests.

This module reads source files referenced by a pinned manifest and records symbol
occurrence lines. It does not build, patch, or execute OpenSSL.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from traceleak.openssl_source_pin import load_openssl_source_pin


class OpenSSLLayoutInspectionError(ValueError):
    """Raised when source layout inspection cannot be completed."""


def inspect_openssl_layout_manifest(path: str | Path) -> dict[str, Any]:
    """Inspect source files and symbol lines for a pinned OpenSSL layout manifest."""

    manifest = load_openssl_source_pin(path)
    if manifest.get("mode") != "pinned":
        raise OpenSSLLayoutInspectionError("layout inspection requires a pinned manifest")
    source = manifest["source"]
    worktree = Path(source.get("worktree_path") or source.get("worktree_hint") or "")
    if not worktree.exists() or not worktree.is_dir():
        raise OpenSSLLayoutInspectionError(f"worktree not found: {worktree}")

    inspected_layout = []
    for item in manifest["source_layout"]:
        inspected_layout.append(_inspect_layout_item(worktree=worktree, item=item))

    return {
        "report_type": "openssl_layout_inspection",
        "status": "layout_inspected",
        "experiment_id": manifest["experiment_id"],
        "target_family": manifest["target_family"],
        "exact_commit_sha": source["exact_commit_sha"],
        "worktree_path": str(worktree),
        "dirty": bool(source.get("dirty")),
        "layout": inspected_layout,
        "notes": [
            "Line numbers are inspection anchors, not instrumentation patches.",
            "Patch planning must re-check these anchors against the same pinned commit.",
        ],
    }


def layout_inspection_markdown(report: dict[str, Any]) -> str:
    """Render source layout inspection as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Layout Inspection",
        "",
        f"- Experiment: `{report['experiment_id']}`",
        f"- Target family: `{report['target_family']}`",
        f"- Commit: `{report['exact_commit_sha']}`",
        f"- Worktree: `{report['worktree_path']}`",
        f"- Dirty: `{str(report['dirty']).lower()}`",
        "",
        "## Symbol Anchors",
        "",
        "| Path | Symbol | Anchor line | All lines | Event groups |",
        "|---|---|---:|---:|---|",
    ]
    for item in report["layout"]:
        for symbol in item["symbols"]:
            line_numbers = ", ".join(str(line) for line in symbol["line_numbers"])
            lines.append(
                "| `{path}` | `{symbol}` | `{anchor}` | `{lines_}` | `{groups}` |".format(
                    path=item["target_path"],
                    symbol=symbol["name"],
                    anchor=symbol["anchor_line"],
                    lines_=line_numbers,
                    groups=", ".join(item["related_event_groups"]),
                )
            )
    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.append("")
    return "\n".join(lines)


def write_layout_inspection_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write layout inspection report as JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_layout_inspection_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write layout inspection report as Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(layout_inspection_markdown(report), encoding="utf-8")


def _inspect_layout_item(*, worktree: Path, item: dict[str, Any]) -> dict[str, Any]:
    target_path = item["target_path"]
    source_file = worktree / target_path
    if not source_file.exists() or not source_file.is_file():
        raise OpenSSLLayoutInspectionError(f"target source file not found: {source_file}")
    lines = source_file.read_text(encoding="utf-8", errors="replace").splitlines()
    symbols = []
    for symbol in item["required_symbols"]:
        line_numbers = [index + 1 for index, line in enumerate(lines) if symbol in line]
        if not line_numbers:
            raise OpenSSLLayoutInspectionError(f"symbol not found in {target_path}: {symbol}")
        definition_line = _definition_line(lines=lines, symbol=symbol)
        anchor_line = definition_line or line_numbers[0]
        symbols.append(
            {
                "name": symbol,
                "line_numbers": line_numbers,
                "first_line": line_numbers[0],
                "definition_line": definition_line,
                "anchor_line": anchor_line,
            }
        )
    return {
        "target_path": target_path,
        "related_event_groups": list(item.get("related_event_groups", [])),
        "line_binding_policy": item["line_binding_policy"],
        "symbols": symbols,
    }


def _definition_line(*, lines: list[str], symbol: str) -> int | None:
    pattern = re.compile(rf"\b{re.escape(symbol)}\s*\(")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not pattern.search(stripped):
            continue
        if stripped.endswith(";"):
            continue
        if stripped.startswith("#"):
            continue
        return index + 1
    return None

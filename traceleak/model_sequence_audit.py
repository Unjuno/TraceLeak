"""Audit model-sequence samples for label leakage and feature dependence.

These helpers are designed to run before real OpenSSL experiments. They do not
prove or disprove leakage; they flag circular label/feature definitions and test
whether a model result survives simple feature ablations.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline

SENSITIVE_TERMS = {
    "secret",
    "private",
    "prime",
    "candidate",
    "seed",
    "rng",
    "p",
    "q",
    "d",
}
DEFAULT_ABLATIONS = (
    "drop_redacted_value",
    "drop_source_token",
    "drop_context_token",
    "event_type_phase_only",
)


class ModelSequenceAuditError(ValueError):
    """Raised when a model-sequence audit cannot be completed."""


def load_model_sequence_sample(path: str | Path) -> dict[str, Any]:
    """Load a model-sequence sample JSON object."""

    input_path = Path(path)
    if not input_path.exists():
        raise ModelSequenceAuditError(f"input file not found: {input_path}")
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelSequenceAuditError(f"invalid JSON in {input_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ModelSequenceAuditError("input must be a JSON object")
    _require_records(payload)
    return payload


def label_leakage_audit(data: dict[str, Any]) -> dict[str, Any]:
    """Flag feature tokens that appear dangerously close to label semantics."""

    records = _require_records(data)
    label_name = str(data.get("label_name", "label"))
    label_terms = _token_terms(label_name)
    labels = {str(record.get("label", "")) for record in records}
    for label in labels:
        label_terms.update(_token_terms(label))

    token_counts = _aggregate_token_counts(records)
    risky_tokens: list[dict[str, Any]] = []
    sensitive_tokens: list[dict[str, Any]] = []
    for token, count in sorted(token_counts.items()):
        token_terms = _token_terms(token)
        overlap = sorted(label_terms & token_terms)
        sensitive_overlap = sorted(SENSITIVE_TERMS & token_terms)
        if overlap:
            risky_tokens.append({"token": token, "count": count, "label_term_overlap": overlap})
        if sensitive_overlap:
            sensitive_tokens.append(
                {"token": token, "count": count, "sensitive_term_overlap": sensitive_overlap}
            )

    risk_level = "low"
    if risky_tokens:
        risk_level = "high"
    elif sensitive_tokens:
        risk_level = "medium"

    return {
        "report_type": "model_sequence_label_leakage_audit",
        "target": data.get("target", _target_from_records(records)),
        "view": data.get("view", _view_from_records(records)),
        "label_name": label_name,
        "record_count": len(records),
        "feature_count": len(token_counts),
        "risk_level": risk_level,
        "risky_token_count": len(risky_tokens),
        "sensitive_token_count": len(sensitive_tokens),
        "risky_tokens": risky_tokens[:25],
        "sensitive_tokens": sensitive_tokens[:25],
        "notes": [
            "High risk means feature tokens share terms with label names or label values.",
            "Medium risk means feature tokens include sensitive cryptographic terms even without direct label overlap.",
            "This audit is conservative and should be reviewed before real OpenSSL experiments.",
        ],
    }


def model_sequence_ablation_report(
    data: dict[str, Any],
    *,
    epochs: int = 80,
    learning_rate: float = 0.8,
    l2: float = 0.0001,
    top_drop_k: int = 2,
) -> dict[str, Any]:
    """Compare original model-sequence performance against feature ablations."""

    _require_records(data)
    original = compare_model_sequence_nn_to_baseline(
        data,
        epochs=epochs,
        learning_rate=learning_rate,
        l2=l2,
    )
    ablations: list[dict[str, Any]] = []
    for mode in DEFAULT_ABLATIONS:
        ablated = ablate_model_sequence_sample(data, mode=mode)
        comparison = compare_model_sequence_nn_to_baseline(
            ablated,
            epochs=epochs,
            learning_rate=learning_rate,
            l2=l2,
        )
        ablations.append(_ablation_row(mode, original, comparison))

    top_tokens = [
        str(item.get("group_id"))
        for item in original.get("neural", {}).get("top_attributions", [])[:top_drop_k]
    ]
    if top_tokens:
        ablated = ablate_model_sequence_sample(data, mode="drop_tokens", tokens_to_drop=top_tokens)
        comparison = compare_model_sequence_nn_to_baseline(
            ablated,
            epochs=epochs,
            learning_rate=learning_rate,
            l2=l2,
        )
        row = _ablation_row("drop_top_attributions", original, comparison)
        row["dropped_tokens"] = top_tokens
        ablations.append(row)

    return {
        "report_type": "model_sequence_ablation_report",
        "target": original["target"],
        "view": original["view"],
        "label_name": original["label_name"],
        "example_count": original["example_count"],
        "original": original,
        "ablations": ablations,
        "summary": _ablation_summary(original, ablations),
        "notes": [
            "Ablation checks whether NN performance survives removing feature families.",
            "A large drop after removing label-overlapping or attribution tokens weakens causal claims.",
        ],
    }


def ablate_model_sequence_sample(
    data: dict[str, Any],
    *,
    mode: str,
    tokens_to_drop: list[str] | None = None,
) -> dict[str, Any]:
    """Return a copy of a model-sequence sample with feature tokens removed."""

    ablated = copy.deepcopy(data)
    records = _require_records(ablated)
    for record in records:
        token_counts = record.get("token_counts")
        if not isinstance(token_counts, dict):
            raise ModelSequenceAuditError("all records must include token_counts for ablation")
        record["token_counts"] = _ablate_token_counts(
            token_counts,
            mode=mode,
            tokens_to_drop=tokens_to_drop or [],
        )
    ablated["audit_ablation_mode"] = mode
    return ablated


def audit_report_markdown(report: dict[str, Any]) -> str:
    """Render a label leakage audit as Markdown."""

    lines = [
        "# TraceLeak Model Sequence Label Leakage Audit",
        "",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Label: `{report['label_name']}`",
        f"- Records: `{report['record_count']}`",
        f"- Features: `{report['feature_count']}`",
        f"- Risk level: `{report['risk_level']}`",
        f"- Risky token count: `{report['risky_token_count']}`",
        f"- Sensitive token count: `{report['sensitive_token_count']}`",
        "",
        "## Risky Tokens",
        "",
    ]
    risky_tokens = report.get("risky_tokens") or []
    if risky_tokens:
        lines.extend(
            f"- `{row['token']}` count=`{row['count']}` overlap=`{','.join(row['label_term_overlap'])}`"
            for row in risky_tokens
        )
    else:
        lines.append("- `none`")

    lines.extend(["", "## Sensitive Tokens", ""])
    sensitive_tokens = report.get("sensitive_tokens") or []
    if sensitive_tokens:
        lines.extend(
            f"- `{row['token']}` count=`{row['count']}` overlap=`{','.join(row['sensitive_term_overlap'])}`"
            for row in sensitive_tokens
        )
    else:
        lines.append("- `none`")

    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def ablation_report_markdown(report: dict[str, Any]) -> str:
    """Render a model-sequence ablation report as Markdown."""

    original = report["original"]
    lines = [
        "# TraceLeak Model Sequence Ablation Report",
        "",
        f"- Target: `{report['target']}`",
        f"- View: `{report['view']}`",
        f"- Label: `{report['label_name']}`",
        f"- Examples: `{report['example_count']}`",
        f"- Original NN accuracy: `{original['neural']['leave_one_out_accuracy']}`",
        f"- Original baseline NN accuracy: `{original['baseline']['leave_one_out_nearest_neighbor_accuracy']}`",
        "",
        "## Ablations",
        "",
        "| Ablation | NN Accuracy | Baseline NN | Delta vs Original NN | Interpretation |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["ablations"]:
        lines.append(
            "| `{name}` | {nn:.6g} | {baseline:.6g} | {delta:.6g} | `{interp}` |".format(
                name=row["name"],
                nn=float(row["neural_accuracy"]),
                baseline=float(row["baseline_accuracy"]),
                delta=float(row["delta_vs_original_neural"]),
                interp=row["interpretation"],
            )
        )
    lines.extend(["", "## Summary", ""])
    for key, value in report["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a JSON artifact."""

    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: str | Path, content: str) -> None:
    """Write a Markdown artifact."""

    Path(path).write_text(content, encoding="utf-8")


def _ablate_token_counts(
    token_counts: dict[str, Any],
    *,
    mode: str,
    tokens_to_drop: list[str],
) -> dict[str, float]:
    result: dict[str, float] = {}
    for token, value in token_counts.items():
        token = str(token)
        numeric_value = float(value)
        if mode == "drop_redacted_value" and token.startswith("redacted_value="):
            continue
        if mode == "drop_source_token" and token.startswith("source_token="):
            continue
        if mode == "drop_context_token" and token.startswith("context_token="):
            continue
        if mode == "event_type_phase_only" and not (
            token.startswith("event_type=") or token.startswith("phase=")
        ):
            continue
        if mode == "drop_tokens" and token in tokens_to_drop:
            continue
        if mode not in (*DEFAULT_ABLATIONS, "drop_tokens"):
            raise ModelSequenceAuditError(f"unknown ablation mode: {mode}")
        result[token] = numeric_value
    return result


def _ablation_row(name: str, original: dict[str, Any], comparison: dict[str, Any]) -> dict[str, Any]:
    original_nn = float(original["neural"]["leave_one_out_accuracy"])
    current_nn = float(comparison["neural"]["leave_one_out_accuracy"])
    return {
        "name": name,
        "neural_accuracy": current_nn,
        "baseline_accuracy": float(comparison["baseline"]["leave_one_out_nearest_neighbor_accuracy"]),
        "delta_vs_original_neural": current_nn - original_nn,
        "interpretation": comparison["interpretation"],
    }


def _ablation_summary(original: dict[str, Any], ablations: list[dict[str, Any]]) -> dict[str, Any]:
    original_nn = float(original["neural"]["leave_one_out_accuracy"])
    if not ablations:
        return {"min_neural_accuracy": original_nn, "max_drop": 0.0, "status": "no_ablations"}
    min_nn = min(float(row["neural_accuracy"]) for row in ablations)
    max_drop = original_nn - min_nn
    status = "ablation_sensitive" if max_drop >= 0.25 else "ablation_stable"
    return {
        "min_neural_accuracy": min_nn,
        "max_drop": max_drop,
        "status": status,
    }


def _aggregate_token_counts(records: list[dict[str, Any]]) -> dict[str, float]:
    counts: dict[str, float] = {}
    for record in records:
        token_counts = record.get("token_counts")
        if not isinstance(token_counts, dict):
            raise ModelSequenceAuditError("all records must include token_counts for audit")
        for token, value in token_counts.items():
            counts[str(token)] = counts.get(str(token), 0.0) + float(value)
    return counts


def _require_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ModelSequenceAuditError("model sequence sample must contain non-empty records")
    if not all(isinstance(record, dict) for record in records):
        raise ModelSequenceAuditError("all records must be objects")
    return records


def _target_from_records(records: list[dict[str, Any]]) -> str:
    return str(records[0].get("target", "unknown"))


def _view_from_records(records: list[dict[str, Any]]) -> str:
    return str(records[0].get("view", "unknown"))


def _token_terms(value: str) -> set[str]:
    return {term for term in re.split(r"[^A-Za-z0-9]+", value.lower()) if term}

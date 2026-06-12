# ruff: noqa: I001

import json
import subprocess
import sys


SAMPLE = {
    "format": "traceleak.model_sequence.v1",
    "target": "toy-audit-cli",
    "view": "redacted",
    "label_name": "prime_attempt_bucket",
    "include_counts": True,
    "records": [
        {
            "run_id": "r1",
            "target": "toy-audit-cli",
            "view": "redacted",
            "label": "low",
            "token_counts": {
                "event_token=loop:prime_candidate:attempt_round": 1,
                "source_token=target.py:10:keygen:attempt_round": 1,
                "context_token=keygen:attempt": 1,
                "event_type=loop": 1,
                "phase=keygen": 1,
            },
        },
        {
            "run_id": "r2",
            "target": "toy-audit-cli",
            "view": "redacted",
            "label": "low",
            "token_counts": {
                "event_token=loop:prime_candidate:attempt_round": 1,
                "source_token=target.py:10:keygen:attempt_round": 1,
                "context_token=keygen:attempt": 1,
                "event_type=loop": 1,
                "phase=keygen": 1,
            },
        },
        {
            "run_id": "r3",
            "target": "toy-audit-cli",
            "view": "redacted",
            "label": "high",
            "token_counts": {
                "event_token=loop:prime_candidate:attempt_round": 4,
                "source_token=target.py:10:keygen:attempt_round": 4,
                "context_token=keygen:attempt": 4,
                "event_type=loop": 4,
                "phase=keygen": 4,
            },
        },
        {
            "run_id": "r4",
            "target": "toy-audit-cli",
            "view": "redacted",
            "label": "high",
            "token_counts": {
                "event_token=loop:prime_candidate:attempt_round": 4,
                "source_token=target.py:10:keygen:attempt_round": 4,
                "context_token=keygen:attempt": 4,
                "event_type=loop": 4,
                "phase=keygen": 4,
            },
        },
    ],
}


def test_audit_model_sequence_labels_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "sample.json"
    output_path = tmp_path / "audit.md"
    input_path.write_text(json.dumps(SAMPLE), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_model_sequence_labels.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Model Sequence Label Leakage Audit" in markdown
    assert "prime_candidate" in markdown


def test_model_sequence_ablation_report_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "sample.json"
    output_path = tmp_path / "ablation.json"
    input_path.write_text(json.dumps(SAMPLE), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_sequence_ablation_report.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
            "--format",
            "json",
            "--epochs",
            "20",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["report_type"] == "model_sequence_ablation_report"
    assert payload["ablations"]
    assert payload["top_attribution_ablation"]["status"] in {
        "baseline_dominates",
        "top_attribution_sensitive",
        "top_attribution_stable",
    }


def test_audit_model_sequence_labels_cli_rejects_missing_file(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_model_sequence_labels.py",
            "--in",
            str(tmp_path / "missing.json"),
            "--out",
            str(tmp_path / "audit.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "input file not found" in result.stderr

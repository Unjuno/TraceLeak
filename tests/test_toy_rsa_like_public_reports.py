import json
import subprocess
import sys

from traceleak.comparison import comparison_report_dict, load_comparison


def test_toy_rsa_like_report_sample_json() -> None:
    payload = json.loads(open("examples/toy_rsa_like/report_sample.json", encoding="utf-8").read())
    assert payload["target"] == "toy-rsa-like"
    assert payload["view"] == "redacted"
    assert payload["score"] == 6.0
    assert payload["attributions"][0]["group_id"] == "candidate_result"
    assert payload["attributions"][0]["contribution"] == 4.0


def test_toy_rsa_like_report_sample_markdown() -> None:
    text = open("examples/toy_rsa_like/report_sample.md", encoding="utf-8").read()
    assert "TraceLeak Attribution Report" in text
    assert "toy-rsa-like" in text
    assert "candidate_result" in text
    assert "small_divisor_check" in text


def test_toy_rsa_like_report_can_be_regenerated(tmp_path) -> None:
    output_path = tmp_path / "toy_report.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_report.py",
            "--in",
            "examples/toy_rsa_like/ablation_sample.json",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Attribution Report" in text
    assert "candidate_result" in text


def test_synthetic_vs_toy_comparison_sample_is_valid() -> None:
    data = load_comparison("examples/toy_rsa_like/synthetic_vs_toy_comparison_sample.json")
    report = comparison_report_dict(data)
    assert report["comparison_type"] == "synthetic_vs_toy"
    assert report["status"] == "higher"
    assert report["delta"] == 4.0


def test_synthetic_vs_toy_comparison_renders(tmp_path) -> None:
    output_path = tmp_path / "synthetic_vs_toy.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            "examples/toy_rsa_like/synthetic_vs_toy_comparison_sample.json",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Comparison Report" in text
    assert "synthetic_vs_toy" in text
    assert "toy-rsa-like" in text

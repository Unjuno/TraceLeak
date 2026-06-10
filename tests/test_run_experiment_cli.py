import json
import subprocess
import sys
from pathlib import Path


def test_run_experiment_cli_generates_outputs(tmp_path) -> None:
    out_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_experiment.py",
            "experiments/exp_000_synthetic_leak/config.json",
            "--out-dir",
            str(out_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    expected = [
        Path("reports/local/exp_000_synthetic_leak.md"),
        Path("reports/local/exp_000_synthetic_leak.json"),
        out_dir / "exp_000_synthetic_leak.features.json",
        out_dir / "exp_000_synthetic_leak.features.csv",
        out_dir / "exp_000_synthetic_leak.baseline.json",
    ]
    for path in expected:
        assert path.exists(), f"missing output: {path}"

    report = json.loads(Path("reports/local/exp_000_synthetic_leak.json").read_text(encoding="utf-8"))
    assert report["target"] == "synthetic-example"

    # Clean configured local outputs created by the sample config.
    for path in [
        Path("reports/local/exp_000_synthetic_leak.md"),
        Path("reports/local/exp_000_synthetic_leak.json"),
    ]:
        path.unlink(missing_ok=True)

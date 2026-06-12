import json
import subprocess
import sys


def test_train_model_sequence_nn_cli_writes_valid_model_result(tmp_path) -> None:
    output_path = tmp_path / "model_sequence_nn_result.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/train_model_sequence_nn.py",
            "--in",
            "examples/synthetic/model_sequence_baseline_sample.json",
            "--out",
            str(output_path),
            "--epochs",
            "80",
            "--learning-rate",
            "0.8",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["result_type"] == "model_sequence_nn"
    assert payload["model"]["type"] == "neural"
    assert payload["metrics"]["leave_one_out"]["accuracy"] == 1.0


def test_train_model_sequence_mlp_cli_writes_valid_model_result(tmp_path) -> None:
    output_path = tmp_path / "model_sequence_mlp_result.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/train_model_sequence_mlp.py",
            "--in",
            "examples/synthetic/model_sequence_baseline_sample.json",
            "--out",
            str(output_path),
            "--epochs",
            "80",
            "--learning-rate",
            "0.2",
            "--hidden-size",
            "4",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["result_type"] == "model_sequence_nn"
    assert payload["model"]["name"] == "mlp-model-sequence-nn"
    assert payload["model"]["architecture"] == "one-hidden-layer-tanh-softmax"
    assert payload["model"]["hidden_size"] == 4
    assert payload["metrics"]["leave_one_out"]["accuracy"] >= 0.5


def test_train_model_sequence_nn_cli_rejects_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/train_model_sequence_nn.py",
            "--in",
            str(tmp_path / "missing.json"),
            "--out",
            str(tmp_path / "model_sequence_nn_result.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "input file not found" in result.stderr

import pytest

from traceleak.config import ConfigError, config_summary, validate_config


def valid_config() -> dict:
    return {
        "experiment_id": "exp_000_synthetic_leak",
        "experiment_type": "synthetic",
        "target": "synthetic-example",
        "view": "redacted",
        "metric": "DeltaH",
        "inputs": {
            "trace": "examples/synthetic/synthetic_trace_sample.jsonl",
        },
        "outputs": {
            "report": "reports/local/report.md",
        },
        "safety": {
            "contains_raw_trace": False,
            "contains_secret_equivalent": False,
        },
    }


def test_validate_config_accepts_valid_config() -> None:
    validate_config(valid_config())


def test_validate_config_rejects_missing_required_field() -> None:
    config = valid_config()
    del config["experiment_id"]
    with pytest.raises(ConfigError):
        validate_config(config)


def test_validate_config_rejects_raw_view_by_default() -> None:
    config = valid_config()
    config["view"] = "raw"
    with pytest.raises(ConfigError):
        validate_config(config)


def test_validate_config_allows_raw_when_not_public_safe() -> None:
    config = valid_config()
    config["view"] = "raw"
    validate_config(config, public_safe=False)


def test_validate_config_rejects_raw_flag_by_default() -> None:
    config = valid_config()
    config["safety"]["contains_raw_trace"] = True
    with pytest.raises(ConfigError):
        validate_config(config)


def test_config_summary() -> None:
    summary = config_summary(valid_config())
    assert summary == {
        "experiment_id": "exp_000_synthetic_leak",
        "experiment_type": "synthetic",
        "target": "synthetic-example",
        "view": "redacted",
        "metric": "DeltaH",
        "input_count": 1,
        "output_count": 1,
    }

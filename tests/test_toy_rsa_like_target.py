from examples.toy_rsa_like.target import (
    _bucket_attempt,
    _bucket_bit_length,
    _bucket_divisor,
    _bucket_divisor_count,
    make_run,
)
from traceleak.schema import validate_run


def test_toy_rsa_like_buckets() -> None:
    assert _bucket_bit_length(11) == "000-011"
    assert _bucket_bit_length(12) == "012"
    assert _bucket_bit_length(13) == "013-plus"
    assert _bucket_attempt(1) == "1"
    assert _bucket_attempt(2) == "2"
    assert _bucket_attempt(3) == "3-plus"
    assert _bucket_divisor(3) == "small"
    assert _bucket_divisor(7) == "medium"
    assert _bucket_divisor(13) == "large"
    assert _bucket_divisor_count(5) == "4-6"


def test_make_run_generates_public_safe_trace() -> None:
    run = make_run(0)
    validate_run(run, public_export=True)
    assert run["target"] == "toy-rsa-like"
    assert run["view"] == "redacted"
    assert len(run["events"]) == 4
    assert "toy_result_bucket" in run["labels_lab_only"]

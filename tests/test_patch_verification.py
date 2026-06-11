import pytest

from traceleak.patch_verification import (
    PatchVerificationError,
    classify_delta,
    patch_verification_summary,
    validate_patch_verification,
    verification_delta,
)


def valid_result() -> dict:
    return {
        "verification_id": "synthetic_patch_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before": {"run_id": "before", "score": 4.0},
        "after": {"run_id": "after", "score": 1.0},
        "delta": 3.0,
        "status": "reduced",
    }


def test_verification_delta() -> None:
    assert verification_delta(4.0, 1.0) == pytest.approx(3.0)


def test_classify_delta() -> None:
    assert classify_delta(1.0) == "reduced"
    assert classify_delta(0.0) == "unchanged"
    assert classify_delta(-1.0) == "increased"


def test_validate_patch_verification_accepts_valid_result() -> None:
    validate_patch_verification(valid_result())


def test_validate_patch_verification_rejects_delta_mismatch() -> None:
    result = valid_result()
    result["delta"] = 2.0
    with pytest.raises(PatchVerificationError):
        validate_patch_verification(result)


def test_validate_patch_verification_rejects_raw_public_view() -> None:
    result = valid_result()
    result["view"] = "raw"
    with pytest.raises(PatchVerificationError):
        validate_patch_verification(result)


def test_validate_patch_verification_rejects_secret_equivalent_field() -> None:
    result = valid_result()
    result["private_key"] = "not allowed"
    with pytest.raises(PatchVerificationError):
        validate_patch_verification(result)


def test_patch_verification_summary() -> None:
    summary = patch_verification_summary(valid_result())
    assert summary == {
        "verification_id": "synthetic_patch_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before_score": 4.0,
        "after_score": 1.0,
        "delta": 3.0,
        "status": "reduced",
    }

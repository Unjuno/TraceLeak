import pytest

from traceleak.claim_levels import (
    ClaimLevelError,
    claim_report_dict,
    claim_summary,
    validate_claim,
)


def l5_claim() -> dict:
    return {
        "claim_id": "synthetic_claim_l5_0001",
        "level": "L5",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "evidence": {
            "attribution_report": {
                "path": "reports/local/exp_001_synthetic_generated.md",
                "top_group_id": "synthetic_branch_event",
            },
            "patch_verification": {
                "verification_id": "synthetic_patch_0001",
                "status": "reduced",
            },
            "stability": {
                "stability_id": "synthetic_stability_0001",
                "status": "reduced",
            },
        },
        "safety": {
            "public_safe": True,
            "contains_raw_trace": False,
            "contains_secret_equivalent": False,
        },
    }


def test_validate_claim_accepts_l5_claim() -> None:
    validate_claim(l5_claim())


def test_validate_claim_rejects_unknown_level() -> None:
    claim = l5_claim()
    claim["level"] = "L9"
    with pytest.raises(ClaimLevelError):
        validate_claim(claim)


def test_validate_claim_rejects_raw_public_view() -> None:
    claim = l5_claim()
    claim["view"] = "raw"
    with pytest.raises(ClaimLevelError):
        validate_claim(claim)


def test_validate_claim_rejects_unsafe_public_claim() -> None:
    claim = l5_claim()
    claim["safety"]["contains_raw_trace"] = True
    with pytest.raises(ClaimLevelError):
        validate_claim(claim)


def test_validate_claim_rejects_l5_without_reduced_patch_verification() -> None:
    claim = l5_claim()
    claim["evidence"]["patch_verification"]["status"] = "unchanged"
    with pytest.raises(ClaimLevelError):
        validate_claim(claim)


def test_validate_claim_rejects_l5_without_reduced_stability() -> None:
    claim = l5_claim()
    claim["evidence"]["stability"]["status"] = "inconclusive"
    with pytest.raises(ClaimLevelError):
        validate_claim(claim)


def test_validate_claim_rejects_secret_equivalent_field() -> None:
    claim = l5_claim()
    claim["private_key"] = "not allowed"
    with pytest.raises(ClaimLevelError):
        validate_claim(claim)


def test_claim_summary() -> None:
    summary = claim_summary(l5_claim())
    assert summary["claim_id"] == "synthetic_claim_l5_0001"
    assert summary["level"] == "L5"
    assert summary["has_patch_verification"] is True
    assert summary["has_stability"] is True


def test_claim_report_dict() -> None:
    report = claim_report_dict(l5_claim())
    assert report["report_type"] == "claim_level"
    assert report["level"] == "L5"
    assert report["evidence"]["patch_verification"]["status"] == "reduced"

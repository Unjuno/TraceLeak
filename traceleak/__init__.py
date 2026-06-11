"""TraceLeak: source-level leakage assessment primitives."""

from traceleak.attribution import AttributionScore, ablation_drop
from traceleak.claim_levels import claim_report_dict, claim_summary, validate_claim
from traceleak.comparison import (
    classify_comparison,
    comparison_delta,
    comparison_report_dict,
)
from traceleak.config import validate_config
from traceleak.features import extract_feature_vector
from traceleak.metrics import accuracy, delta_h, top_k_recall
from traceleak.patch_reporting import patch_verification_report_dict
from traceleak.patch_verification import (
    classify_delta,
    validate_patch_verification,
    verification_delta,
)
from traceleak.schema import TraceEvent, TraceRun, validate_run
from traceleak.stability import stability_result, stability_summary
from traceleak.views import to_view
from traceleak.workflow import WorkflowResult, run_lightweight_experiment

__all__ = [
    "AttributionScore",
    "TraceEvent",
    "TraceRun",
    "WorkflowResult",
    "ablation_drop",
    "accuracy",
    "claim_report_dict",
    "claim_summary",
    "classify_comparison",
    "classify_delta",
    "comparison_delta",
    "comparison_report_dict",
    "delta_h",
    "extract_feature_vector",
    "patch_verification_report_dict",
    "run_lightweight_experiment",
    "stability_result",
    "stability_summary",
    "to_view",
    "top_k_recall",
    "validate_claim",
    "validate_config",
    "validate_patch_verification",
    "validate_run",
    "verification_delta",
]

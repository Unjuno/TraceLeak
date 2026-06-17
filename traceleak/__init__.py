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
from traceleak.model_features import (
    event_token,
    model_sequence_vocabulary,
    redacted_value_tokens,
    sequence_token_counts,
    source_token,
    trace_to_model_sequence,
)
from traceleak.patch_reporting import patch_verification_report_dict
from traceleak.patch_verification import (
    classify_delta,
    validate_patch_verification,
    verification_delta,
)
from traceleak.program_event_schema import (
    ProgramEvent,
    ProgramEventSchemaError,
    program_event_from_dict,
    program_event_from_legacy_model_step,
    program_events_from_legacy_model_sequence,
    sort_program_events,
    validate_program_event,
    validate_program_events,
)
from traceleak.schema import TraceEvent, TraceRun, validate_run
from traceleak.stability import stability_result, stability_summary
from traceleak.views import to_view
from traceleak.workflow import WorkflowResult, run_lightweight_experiment

__all__ = [
    "AttributionScore",
    "ProgramEvent",
    "ProgramEventSchemaError",
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
    "event_token",
    "extract_feature_vector",
    "model_sequence_vocabulary",
    "patch_verification_report_dict",
    "program_event_from_dict",
    "program_event_from_legacy_model_step",
    "program_events_from_legacy_model_sequence",
    "redacted_value_tokens",
    "run_lightweight_experiment",
    "sequence_token_counts",
    "sort_program_events",
    "source_token",
    "stability_result",
    "stability_summary",
    "to_view",
    "top_k_recall",
    "trace_to_model_sequence",
    "validate_claim",
    "validate_config",
    "validate_patch_verification",
    "validate_program_event",
    "validate_program_events",
    "validate_run",
    "verification_delta",
]

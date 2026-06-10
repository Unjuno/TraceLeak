"""TraceLeak: source-level leakage assessment primitives."""

from traceleak.attribution import AttributionScore, ablation_drop
from traceleak.config import validate_config
from traceleak.features import extract_feature_vector
from traceleak.metrics import accuracy, delta_h, top_k_recall
from traceleak.schema import TraceEvent, TraceRun, validate_run
from traceleak.views import to_view
from traceleak.workflow import WorkflowResult, run_lightweight_experiment

__all__ = [
    "AttributionScore",
    "TraceEvent",
    "TraceRun",
    "WorkflowResult",
    "ablation_drop",
    "accuracy",
    "delta_h",
    "extract_feature_vector",
    "run_lightweight_experiment",
    "to_view",
    "top_k_recall",
    "validate_config",
    "validate_run",
]

"""Registry for analysis-level contract formats."""

from __future__ import annotations

from traceleak.analysis_bundle_contract import ANALYSIS_BUNDLE_FORMAT
from traceleak.evidence_chain_contract import EVIDENCE_CHAIN_FORMAT
from traceleak.model_output_contract import MODEL_OUTPUT_FORMAT
from traceleak.view_contract import VIEW_CONTRACT_FORMAT

ANALYSIS_CONTRACT_FORMATS: tuple[str, ...] = (
    ANALYSIS_BUNDLE_FORMAT,
    MODEL_OUTPUT_FORMAT,
    EVIDENCE_CHAIN_FORMAT,
    VIEW_CONTRACT_FORMAT,
)


def analysis_contract_formats() -> list[str]:
    """Return registered analysis-level contract formats."""

    return list(ANALYSIS_CONTRACT_FORMATS)

from traceleak.evidence_chain_contract import EVIDENCE_CHAIN_FORMAT


def test_evidence_chain_format() -> None:
    assert EVIDENCE_CHAIN_FORMAT == "traceleak.evidence_chain.v1"

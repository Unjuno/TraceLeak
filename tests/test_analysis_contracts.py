from traceleak.analysis_contracts import analysis_contract_formats


def test_analysis_contract_formats_are_available() -> None:
    assert len(analysis_contract_formats()) >= 1

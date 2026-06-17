from traceleak.view_contract import ALLOWED_VIEW_LEVELS, VIEW_CONTRACT_FORMAT, view_contract


def test_view_contract_format() -> None:
    assert VIEW_CONTRACT_FORMAT == "traceleak.view_contract.v1"


def test_view_contract_format_prefix() -> None:
    assert VIEW_CONTRACT_FORMAT.startswith("traceleak.")


def test_view_contract_levels_are_available() -> None:
    assert len(ALLOWED_VIEW_LEVELS) >= 1


def test_view_contract_builder_is_callable() -> None:
    assert callable(view_contract)

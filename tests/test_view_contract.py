from traceleak.view_contract import (
    ALLOWED_VIEW_ACTIONS,
    ALLOWED_VIEW_LEVELS,
    REQUIRED_VIEW_CONTRACT_FIELDS,
    VIEW_CONTRACT_FORMAT,
    sort_view_contracts,
    validate_view_contract,
    view_contract,
)


def test_view_contract_format() -> None:
    assert VIEW_CONTRACT_FORMAT == "traceleak.view_contract.v1"


def test_view_contract_format_prefix() -> None:
    assert VIEW_CONTRACT_FORMAT.startswith("traceleak.")


def test_view_contract_levels_are_available() -> None:
    assert len(ALLOWED_VIEW_LEVELS) >= 1


def test_view_contract_actions_are_available() -> None:
    assert len(ALLOWED_VIEW_ACTIONS) >= 1


def test_view_contract_required_fields_are_available() -> None:
    assert len(REQUIRED_VIEW_CONTRACT_FIELDS) == 7


def test_view_contract_builder_is_callable() -> None:
    assert callable(view_contract)


def test_view_contract_validation_helpers_are_callable() -> None:
    assert callable(validate_view_contract)
    assert callable(sort_view_contracts)

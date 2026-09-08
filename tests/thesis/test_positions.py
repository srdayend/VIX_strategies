import pytest

from vix_strategies.thesis.positions import ContractPosition, same_contract_pnl


def test_rank_change_does_not_create_holding_pnl_from_new_rank_price():
    previous_positions = [
        ContractPosition(contract_id="VXH26", quantity=1.0, previous_price=18.0),
    ]
    current_prices = {
        "VXH26": 18.5,
        "VXJ26": 21.0,
    }

    pnl = same_contract_pnl(previous_positions, current_prices)

    assert pnl.by_contract == {"VXH26": 0.5}
    assert pnl.total == 0.5


def test_same_contract_pnl_rejects_rank_only_position_labels():
    previous_positions = [
        ContractPosition(contract_id="M1", quantity=1.0, previous_price=18.0),
    ]

    with pytest.raises(ValueError, match="rank label"):
        same_contract_pnl(previous_positions, {"M1": 21.0})


def test_same_contract_pnl_rejects_rank_only_current_price_labels():
    previous_positions = [
        ContractPosition(contract_id="VXH26", quantity=1.0, previous_price=18.0),
    ]

    with pytest.raises(ValueError, match="rank label"):
        same_contract_pnl(previous_positions, {"M1": 21.0})

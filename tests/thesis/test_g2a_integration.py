from datetime import date

import pytest

from vix_strategies.thesis import (
    ContractPosition,
    ContractRecord,
    CurvePoint,
    build_local_curve,
    compute_contract_roll_down,
    compute_spread_cird,
    curve_price_at_dte,
    decompose_contract_move,
    same_contract_pnl,
)


def test_g2a_two_contract_synthetic_path_preserves_economic_invariants():
    trade_date = date(2026, 3, 13)
    next_trade_date = date(2026, 3, 16)
    front = ContractRecord(
        contract_id="SYNTH_FRONT",
        trade_date=trade_date,
        settlement_date=date(2026, 3, 23),
        settlement_price=17.0,
        rank_label="M1",
        settlement_date_source="official",
    )
    deferred = ContractRecord(
        contract_id="SYNTH_DEFERRED",
        trade_date=trade_date,
        settlement_date=date(2026, 4, 22),
        settlement_price=23.0,
        rank_label="M2",
        settlement_date_source="official",
    )
    next_front_dte = (front.settlement_date - next_trade_date).days
    next_deferred_dte = (deferred.settlement_date - next_trade_date).days
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[
            CurvePoint(dte=front.dte, price=front.settlement_price),
            CurvePoint(dte=deferred.dte, price=deferred.settlement_price),
        ],
    )

    front_rd = compute_contract_roll_down(
        current_price=front.settlement_price,
        current_dte=front.dte,
        next_dte=next_front_dte,
        curve=curve,
    )
    deferred_rd = compute_contract_roll_down(
        current_price=deferred.settlement_price,
        current_dte=deferred.dte,
        next_dte=next_deferred_dte,
        curve=curve,
    )
    deferred_move = decompose_contract_move(
        current_price=deferred.settlement_price,
        next_price=22.1,
        current_dte=deferred.dte,
        next_dte=next_deferred_dte,
        curve=curve,
    )
    holding_pnl = same_contract_pnl(
        [ContractPosition(contract_id="SYNTH_FRONT", quantity=1.0, previous_price=17.0)],
        {"SYNTH_FRONT": 16.6, "SYNTH_DEFERRED": 22.1},
    )

    assert curve_price_at_dte(curve, 0.0) == 15.0
    assert front.dte - next_front_dte == 3
    assert deferred.dte - next_deferred_dte == 3
    assert front_rd == pytest.approx(-0.6)
    assert deferred_rd == pytest.approx(-0.6)
    assert compute_spread_cird(front_rd, deferred_rd, hedge_ratio=0.5) == pytest.approx(0.3)
    assert deferred_move.realized == pytest.approx(deferred_move.roll_down + deferred_move.repricing)
    assert deferred_move.repricing == pytest.approx(-0.3)
    assert holding_pnl.by_contract == {"SYNTH_FRONT": pytest.approx(-0.4)}
    assert holding_pnl.total == pytest.approx(-0.4)

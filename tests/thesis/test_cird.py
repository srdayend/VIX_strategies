from datetime import date

import pytest

from vix_strategies.thesis.cird import (
    compute_contract_roll_down,
    compute_spread_cird,
    decompose_contract_move,
)
from vix_strategies.thesis.contracts import compute_calendar_dte
from vix_strategies.thesis.curve import CurvePoint, build_local_curve


def test_deferred_short_roll_down_is_positive_carry_under_simple_contango():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=23.0)],
    )

    deferred_rd = compute_contract_roll_down(
        current_price=23.0,
        current_dte=40.0,
        next_dte=39.0,
        curve=curve,
    )

    assert deferred_rd == pytest.approx(-0.2)
    assert -deferred_rd == pytest.approx(0.2)


def test_roll_down_rejects_current_dte_not_represented_by_local_curve():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=23.0)],
    )

    with pytest.raises(ValueError, match="current_dte outside local curve bounds"):
        compute_contract_roll_down(
            current_price=24.0,
            current_dte=50.0,
            next_dte=39.0,
            curve=curve,
        )


def test_roll_down_rejects_current_price_inconsistent_with_same_day_curve():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=23.0)],
    )

    with pytest.raises(ValueError, match="current_price must match"):
        compute_contract_roll_down(
            current_price=22.0,
            current_dte=40.0,
            next_dte=39.0,
            curve=curve,
        )


def test_front_long_roll_down_is_hedge_carry_cost_under_simple_contango():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=23.0)],
    )

    front_rd = compute_contract_roll_down(
        current_price=17.0,
        current_dte=10.0,
        next_dte=9.0,
        curve=curve,
    )
    deferred_rd = compute_contract_roll_down(
        current_price=23.0,
        current_dte=40.0,
        next_dte=39.0,
        curve=curve,
    )

    assert front_rd == pytest.approx(-0.2)
    assert compute_spread_cird(front_rd, deferred_rd, hedge_ratio=0.5) == pytest.approx(0.1)


def test_spread_cird_rejects_negative_hedge_ratio():
    with pytest.raises(ValueError, match="hedge_ratio must be non-negative"):
        compute_spread_cird(front_rd=-0.2, deferred_rd=-0.2, hedge_ratio=-0.5)


def test_roll_down_uses_friday_to_monday_calendar_aging():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=23.0)],
    )
    settlement = date(2026, 3, 23)
    current_dte = compute_calendar_dte(date(2026, 3, 13), settlement)
    next_dte = compute_calendar_dte(date(2026, 3, 16), settlement)

    roll_down = compute_contract_roll_down(
        current_price=17.0,
        current_dte=current_dte,
        next_dte=next_dte,
        curve=curve,
    )

    assert current_dte - next_dte == 3
    assert roll_down == pytest.approx(-0.6)


def test_decomposition_exactly_splits_realized_move_into_roll_down_and_repricing():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=23.0)],
    )

    move = decompose_contract_move(
        current_price=23.0,
        next_price=22.6,
        current_dte=40.0,
        next_dte=39.0,
        curve=curve,
    )

    assert move.realized == pytest.approx(-0.4)
    assert move.roll_down == pytest.approx(-0.2)
    assert move.repricing == pytest.approx(-0.2)
    assert move.realized == pytest.approx(move.roll_down + move.repricing)

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite

from vix_strategies.thesis.curve import LocalCurve, curve_price_at_dte


@dataclass(frozen=True)
class ContractMoveDecomposition:
    realized: float
    roll_down: float
    repricing: float


def compute_contract_roll_down(
    *,
    current_price: float,
    current_dte: float,
    next_dte: float,
    curve: LocalCurve,
) -> float:
    _validate_interval(current_price, current_dte, next_dte)
    try:
        curve_current_price = curve_price_at_dte(curve, current_dte)
    except ValueError as exc:
        raise ValueError("current_dte outside local curve bounds") from exc
    if not isclose(current_price, curve_current_price, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("current_price must match same-day curve price at current_dte")
    return curve_price_at_dte(curve, next_dte) - current_price


def decompose_contract_move(
    *,
    current_price: float,
    next_price: float,
    current_dte: float,
    next_dte: float,
    curve: LocalCurve,
) -> ContractMoveDecomposition:
    _validate_price(next_price, "next_price")
    roll_down = compute_contract_roll_down(
        current_price=current_price,
        current_dte=current_dte,
        next_dte=next_dte,
        curve=curve,
    )
    implied_next_price = curve_price_at_dte(curve, next_dte)
    repricing = next_price - implied_next_price
    realized = next_price - current_price
    return ContractMoveDecomposition(
        realized=realized,
        roll_down=roll_down,
        repricing=repricing,
    )


def compute_spread_cird(front_rd: float, deferred_rd: float, hedge_ratio: float) -> float:
    for value, name in [
        (front_rd, "front_rd"),
        (deferred_rd, "deferred_rd"),
        (hedge_ratio, "hedge_ratio"),
    ]:
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if hedge_ratio < 0:
        raise ValueError("hedge_ratio must be non-negative")
    return hedge_ratio * front_rd - deferred_rd


def _validate_interval(current_price: float, current_dte: float, next_dte: float) -> None:
    _validate_price(current_price, "current_price")
    for value, name in [(current_dte, "current_dte"), (next_dte, "next_dte")]:
        if not isfinite(value) or value < 0:
            raise ValueError(f"{name} must be non-negative and finite")
    if next_dte == 0:
        raise ValueError("next_dte == 0 requires final-settlement-specific handling")
    if next_dte > current_dte:
        raise ValueError("next_dte cannot exceed current_dte")


def _validate_price(price: float, name: str) -> None:
    if not isfinite(price) or price <= 0:
        raise ValueError(f"{name} must be positive and finite")

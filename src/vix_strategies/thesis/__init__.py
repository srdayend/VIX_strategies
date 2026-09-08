"""Thesis-grade contract-level VIX futures research primitives."""

from vix_strategies.thesis.cird import (
    ContractMoveDecomposition,
    compute_contract_roll_down,
    compute_spread_cird,
    decompose_contract_move,
)
from vix_strategies.thesis.contracts import (
    ContractRecord,
    compute_calendar_dte,
    compute_monthly_vx_settlement_date,
)
from vix_strategies.thesis.curve import (
    CurvePoint,
    LocalCurve,
    build_local_curve,
    curve_price_at_dte,
)
from vix_strategies.thesis.positions import (
    ContractPosition,
    SameContractPnl,
    same_contract_pnl,
)

__all__ = [
    "ContractMoveDecomposition",
    "ContractPosition",
    "ContractRecord",
    "CurvePoint",
    "LocalCurve",
    "SameContractPnl",
    "build_local_curve",
    "compute_calendar_dte",
    "compute_contract_roll_down",
    "compute_monthly_vx_settlement_date",
    "compute_spread_cird",
    "curve_price_at_dte",
    "decompose_contract_move",
    "same_contract_pnl",
]

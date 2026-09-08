from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Dict, Iterable, Mapping


@dataclass(frozen=True)
class ContractPosition:
    contract_id: str
    quantity: float
    previous_price: float

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise ValueError("contract_id is required")
        if not isfinite(self.quantity):
            raise ValueError("quantity must be finite")
        _validate_price(self.previous_price, "previous_price")


@dataclass(frozen=True)
class SameContractPnl:
    by_contract: Mapping[str, float]
    total: float


def same_contract_pnl(
    previous_positions: Iterable[ContractPosition],
    current_prices: Mapping[str, float],
) -> SameContractPnl:
    for contract_id, price in current_prices.items():
        _reject_rank_label(contract_id)
        _validate_price(price, "current price")

    by_contract: Dict[str, float] = {}
    for position in previous_positions:
        _reject_rank_label(position.contract_id)
        if position.contract_id not in current_prices:
            raise KeyError(f"missing current price for {position.contract_id}")
        pnl = position.quantity * (current_prices[position.contract_id] - position.previous_price)
        by_contract[position.contract_id] = by_contract.get(position.contract_id, 0.0) + pnl

    return SameContractPnl(
        by_contract=by_contract,
        total=sum(by_contract.values()),
    )


def _reject_rank_label(label: str) -> None:
    normalized = label.upper()
    if (
        normalized in {"M1", "M2", "VX1", "VX2"}
        or (normalized.startswith("M") and normalized[1:].isdigit())
        or (normalized.startswith("VX") and normalized[2:].isdigit())
    ):
        raise ValueError("rank label cannot be used for same-contract P&L")


def _validate_price(price: float, name: str) -> None:
    if not isfinite(price) or price <= 0:
        raise ValueError(f"{name} must be positive and finite")

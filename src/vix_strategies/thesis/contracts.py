from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Optional, Set


def compute_calendar_dte(trade_date: date, settlement_date: date) -> int:
    """Calendar days from trade date to final settlement date."""
    dte = (settlement_date - trade_date).days
    if dte < 0:
        raise ValueError("settlement_date precedes trade_date")
    return dte


def compute_monthly_vx_settlement_date(
    year: int,
    month: int,
    holidays: Optional[Iterable[date]] = None,
) -> date:
    """Rule-derived monthly VX final settlement date.

    The rule is 30 calendar days before the third Friday of the following
    month, adjusted backward when the nominal date is a weekend or explicit
    holiday. Authoritative source dates should be used when available.
    """
    following_year = year + (1 if month == 12 else 0)
    following_month = 1 if month == 12 else month + 1
    third_friday = _nth_weekday_of_month(
        following_year,
        following_month,
        calendar.FRIDAY,
        3,
    )
    settlement = third_friday - timedelta(days=30)
    holiday_set: Set[date] = set(holidays or ())

    while settlement.weekday() >= 5 or settlement in holiday_set:
        settlement -= timedelta(days=1)

    return settlement


@dataclass(frozen=True)
class ContractRecord:
    contract_id: str
    trade_date: date
    settlement_date: date
    settlement_price: float
    rank_label: Optional[str] = None
    settlement_date_source: str = "official"

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise ValueError("contract_id is required")
        if self.settlement_price <= 0:
            raise ValueError("settlement_price must be positive")
        if self.settlement_date_source not in {"official", "derived"}:
            raise ValueError("settlement_date_source must be 'official' or 'derived'")
        compute_calendar_dte(self.trade_date, self.settlement_date)

    @property
    def dte(self) -> int:
        return compute_calendar_dte(self.trade_date, self.settlement_date)

    @classmethod
    def from_monthly_vx(
        cls,
        *,
        contract_id: str,
        trade_date: date,
        contract_year: int,
        contract_month: int,
        settlement_price: float,
        official_settlement_date: Optional[date] = None,
        holidays: Optional[Iterable[date]] = None,
        rank_label: Optional[str] = None,
    ) -> "ContractRecord":
        if official_settlement_date is not None:
            settlement_date = official_settlement_date
            settlement_date_source = "official"
        else:
            settlement_date = compute_monthly_vx_settlement_date(
                contract_year,
                contract_month,
                holidays=holidays,
            )
            settlement_date_source = "derived"

        return cls(
            contract_id=contract_id,
            trade_date=trade_date,
            settlement_date=settlement_date,
            settlement_price=settlement_price,
            rank_label=rank_label,
            settlement_date_source=settlement_date_source,
        )


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    matches = [
        day
        for day in range(1, calendar.monthrange(year, month)[1] + 1)
        if date(year, month, day).weekday() == weekday
    ]
    return date(year, month, matches[n - 1])

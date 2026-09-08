from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from math import isfinite
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
    holiday_set: Set[date] = set(holidays or ())
    third_friday = _previous_business_day_if_needed(
        _nth_weekday_of_month(
            following_year,
            following_month,
            calendar.FRIDAY,
            3,
        ),
        holiday_set,
    )
    settlement = third_friday - timedelta(days=30)
    return _previous_business_day_if_needed(settlement, holiday_set)


def _previous_business_day_if_needed(day: date, holidays: Set[date]) -> date:
    while day.weekday() >= 5 or day in holidays:
        day -= timedelta(days=1)
    return day


@dataclass(frozen=True)
class ContractRecord:
    contract_id: str
    trade_date: date
    settlement_date: date
    settlement_price: float
    settlement_date_source: str
    rank_label: Optional[str] = None
    listing_type: str = "monthly"

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise ValueError("contract_id is required")
        if not isfinite(self.settlement_price) or self.settlement_price <= 0:
            raise ValueError("settlement_price must be positive and finite")
        if self.settlement_date_source not in {"official", "derived"}:
            raise ValueError("settlement_date_source must be 'official' or 'derived'")
        if self.listing_type != "monthly":
            raise ValueError("listing_type must be 'monthly'")
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
            settlement_date_source=settlement_date_source,
            rank_label=rank_label,
            listing_type="monthly",
        )


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    matches = [
        day
        for day in range(1, calendar.monthrange(year, month)[1] + 1)
        if date(year, month, day).weekday() == weekday
    ]
    return date(year, month, matches[n - 1])

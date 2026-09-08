from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Iterable, Optional, Sequence, Set, Tuple

from vix_strategies.thesis.contracts import compute_monthly_vx_settlement_date


MODERN_RULE_EFFECTIVE_DATE = date(2005, 10, 17)


class SettlementRuleRegime(str, Enum):
    LEGACY = "legacy"
    MODERN = "modern"


class SettlementDateValidationStatus(str, Enum):
    EXPLICIT_OFFICIAL = "explicit_official"
    RULE_DERIVED_VALIDATED = "rule_derived_validated"
    RULE_DERIVED_UNVALIDATED = "rule_derived_unvalidated"


@dataclass(frozen=True)
class ContractCalendarEntry:
    contract_id: str
    contract_month: date
    final_settlement_date: date
    settlement_rule_regime: SettlementRuleRegime
    settlement_date_source: str
    validation_status: SettlementDateValidationStatus
    evidence_reference: str

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise ValueError("contract_id is required")
        if not self.settlement_date_source:
            raise ValueError("settlement_date_source is required")
        if not self.evidence_reference:
            raise ValueError("evidence_reference is required")
        if self.contract_month.day != 1:
            raise ValueError("contract_month must be the first day of the month")


def compute_legacy_vx_settlement_date(
    year: int,
    month: int,
    holidays: Optional[Iterable[date]] = None,
) -> date:
    holiday_set = set(holidays or ())
    third_friday = _nth_weekday_of_month(year, month, calendar.FRIDAY, 3)
    settlement = third_friday - timedelta(days=2)
    return _previous_business_day_if_needed(settlement, holiday_set)


def compute_modern_vx_settlement_date(
    year: int,
    month: int,
    holidays: Optional[Iterable[date]] = None,
) -> date:
    return compute_monthly_vx_settlement_date(year, month, holidays=holidays)


def build_contract_calendar_entry(
    *,
    contract_year: int,
    contract_month: int,
    settlement_date_source: str,
    validation_status: SettlementDateValidationStatus,
    evidence_reference: str,
    holidays: Optional[Iterable[date]] = None,
    explicit_final_settlement_date: Optional[date] = None,
) -> ContractCalendarEntry:
    regime = _settlement_rule_regime(contract_year, contract_month, holidays)
    if explicit_final_settlement_date is not None:
        final_settlement_date = explicit_final_settlement_date
    elif regime == SettlementRuleRegime.LEGACY:
        final_settlement_date = compute_legacy_vx_settlement_date(
            contract_year,
            contract_month,
            holidays=holidays,
        )
    else:
        final_settlement_date = compute_modern_vx_settlement_date(
            contract_year,
            contract_month,
            holidays=holidays,
        )

    return ContractCalendarEntry(
        contract_id=f"VX_{contract_year:04d}{contract_month:02d}",
        contract_month=date(contract_year, contract_month, 1),
        final_settlement_date=final_settlement_date,
        settlement_rule_regime=regime,
        settlement_date_source=settlement_date_source,
        validation_status=validation_status,
        evidence_reference=evidence_reference,
    )


def primary_eligible_calendar_entries(
    entries: Sequence[ContractCalendarEntry],
) -> Tuple[ContractCalendarEntry, ...]:
    unvalidated = [
        entry.contract_id
        for entry in entries
        if entry.validation_status
        == SettlementDateValidationStatus.RULE_DERIVED_UNVALIDATED
    ]
    if unvalidated:
        raise ValueError(
            "rule_derived_unvalidated calendar entries are not primary-eligible: "
            + ", ".join(unvalidated)
        )
    return tuple(entries)


def _settlement_rule_regime(
    year: int,
    month: int,
    holidays: Optional[Iterable[date]],
) -> SettlementRuleRegime:
    legacy_settlement = compute_legacy_vx_settlement_date(year, month, holidays)
    if legacy_settlement < MODERN_RULE_EFFECTIVE_DATE:
        return SettlementRuleRegime.LEGACY
    return SettlementRuleRegime.MODERN


def _previous_business_day_if_needed(day: date, holidays: Set[date]) -> date:
    while day.weekday() >= 5 or day in holidays:
        day -= timedelta(days=1)
    return day


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    matches = [
        day
        for day in range(1, calendar.monthrange(year, month)[1] + 1)
        if date(year, month, day).weekday() == weekday
    ]
    return date(year, month, matches[n - 1])

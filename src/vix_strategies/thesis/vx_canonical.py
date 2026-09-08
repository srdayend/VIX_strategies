from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, Tuple

from vix_strategies.thesis.vx_calendar import (
    ContractCalendarEntry,
    SettlementDateValidationStatus,
    SettlementRuleRegime,
)
from vix_strategies.thesis.vx_normalization import (
    PriceScaleRegime,
    normalization_factor_for_date,
    normalize_vx_price,
    price_scale_regime_for_date,
    source_multiplier_for_date,
)
from vix_strategies.thesis.vx_raw import RawVxRecord
from vix_strategies.thesis.vx_universe import ListingType, classify_vx_listing


HISTORICAL_DEVELOPMENT_CUTOFF = date(2026, 5, 1)


class ObservationType(str, Enum):
    DAILY_DSP = "DAILY_DSP"
    FINAL_SOQ = "FINAL_SOQ"


class SampleRole(str, Enum):
    DEVELOPMENT_CONTAMINATED = "development_contaminated"
    POST_FREEZE_HOLDOUT = "post_freeze_holdout"


@dataclass(frozen=True)
class CanonicalVxRecord:
    trade_date: date
    contract_id: str
    contract_month: date
    source_symbol: str
    final_settlement_date: date
    settlement_rule_regime: SettlementRuleRegime
    settlement_date_source: str
    settlement_date_validation_status: SettlementDateValidationStatus
    listing_type: ListingType
    observation_type: ObservationType
    price_scale_regime: PriceScaleRegime
    source_multiplier: int
    normalization_factor: float
    open_norm: Optional[float]
    high_norm: Optional[float]
    low_norm: Optional[float]
    close_norm: Optional[float]
    settle_norm: Optional[float]
    volume: Optional[int]
    open_interest: Optional[int]
    source_file: str
    source_row_id: str
    source_sha256: str
    quality_flags: Tuple[str, ...]
    sample_role: SampleRole

    @property
    def is_primary_curve_eligible(self) -> bool:
        return (
            self.listing_type == ListingType.STANDARD_MONTHLY
            and self.observation_type == ObservationType.DAILY_DSP
            and self.settle_norm is not None
            and self.settlement_date_validation_status
            != SettlementDateValidationStatus.RULE_DERIVED_UNVALIDATED
        )


def canonicalize_raw_record(
    raw_record: RawVxRecord,
    *,
    calendar_entry: ContractCalendarEntry,
) -> CanonicalVxRecord:
    listing = classify_vx_listing(
        raw_record.source_symbol,
        final_settlement_date=calendar_entry.final_settlement_date,
        expected_monthly_final_settlement_date=calendar_entry.final_settlement_date,
    )
    if not listing.is_primary:
        raise ValueError(
            f"source_symbol is not primary monthly VX: {raw_record.source_symbol}"
        )

    observation_type = (
        ObservationType.FINAL_SOQ
        if raw_record.trade_date == calendar_entry.final_settlement_date
        else ObservationType.DAILY_DSP
    )
    quality_flags = []
    settle_norm = _normalize_optional_price(
        raw_record.raw_settle,
        raw_record.trade_date,
        raw_record.raw_row_id,
        "Settle",
    )
    if settle_norm is None:
        quality_flags.append("missing_settlement")

    return CanonicalVxRecord(
        trade_date=raw_record.trade_date,
        contract_id=calendar_entry.contract_id,
        contract_month=calendar_entry.contract_month,
        source_symbol=raw_record.source_symbol,
        final_settlement_date=calendar_entry.final_settlement_date,
        settlement_rule_regime=calendar_entry.settlement_rule_regime,
        settlement_date_source=calendar_entry.settlement_date_source,
        settlement_date_validation_status=calendar_entry.validation_status,
        listing_type=listing.listing_type,
        observation_type=observation_type,
        price_scale_regime=price_scale_regime_for_date(raw_record.trade_date),
        source_multiplier=source_multiplier_for_date(raw_record.trade_date),
        normalization_factor=normalization_factor_for_date(raw_record.trade_date),
        open_norm=_normalize_optional_price(
            raw_record.raw_open,
            raw_record.trade_date,
            raw_record.raw_row_id,
            "Open",
        ),
        high_norm=_normalize_optional_price(
            raw_record.raw_high,
            raw_record.trade_date,
            raw_record.raw_row_id,
            "High",
        ),
        low_norm=_normalize_optional_price(
            raw_record.raw_low,
            raw_record.trade_date,
            raw_record.raw_row_id,
            "Low",
        ),
        close_norm=_normalize_optional_price(
            raw_record.raw_close,
            raw_record.trade_date,
            raw_record.raw_row_id,
            "Close",
        ),
        settle_norm=settle_norm,
        volume=_parse_optional_int(raw_record.raw_volume, raw_record.raw_row_id, "Total Volume"),
        open_interest=_parse_optional_int(
            raw_record.raw_open_interest,
            raw_record.raw_row_id,
            "Open Interest",
        ),
        source_file=raw_record.source_file,
        source_row_id=raw_record.raw_row_id,
        source_sha256=raw_record.source_sha256,
        quality_flags=tuple(quality_flags),
        sample_role=_sample_role_for_date(raw_record.trade_date),
    )


def _sample_role_for_date(trade_date: date) -> SampleRole:
    if trade_date <= HISTORICAL_DEVELOPMENT_CUTOFF:
        return SampleRole.DEVELOPMENT_CONTAMINATED
    return SampleRole.POST_FREEZE_HOLDOUT


def _normalize_optional_price(
    raw_value: Optional[str],
    trade_date: date,
    row_id: str,
    field_name: str,
) -> Optional[float]:
    if raw_value is None:
        return None
    try:
        parsed = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"invalid {field_name} price at {row_id}: {raw_value}") from exc
    return normalize_vx_price(trade_date, parsed)


def _parse_optional_int(
    raw_value: Optional[str],
    row_id: str,
    field_name: str,
) -> Optional[int]:
    if raw_value is None:
        return None
    try:
        return int(raw_value.replace(",", ""))
    except ValueError as exc:
        raise ValueError(f"invalid {field_name} at {row_id}: {raw_value}") from exc

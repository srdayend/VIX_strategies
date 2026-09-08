from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from enum import Enum


class ListingType(str, Enum):
    STANDARD_MONTHLY = "standard_monthly"
    WEEKLY = "weekly"
    TAS = "tas"
    MINI_VIX = "mini_vix"
    SPREAD_COMBINATION = "spread_combination"
    NON_MONTHLY_VX = "non_monthly_vx"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ListingClassification:
    listing_type: ListingType
    is_primary: bool
    reason: str


def canonical_contract_id(year: int, month: int) -> str:
    if month < 1 or month > 12:
        raise ValueError("month must be in 1..12")
    return f"VX_{year:04d}{month:02d}"


def classify_vx_listing(
    source_symbol: str,
    *,
    final_settlement_date: date,
    expected_monthly_final_settlement_date: date,
) -> ListingClassification:
    symbol = source_symbol.strip().upper()
    compact = re.sub(r"\s+", " ", symbol)

    if not compact:
        return ListingClassification(ListingType.UNKNOWN, False, "empty source symbol")
    if compact.startswith("VXM"):
        return ListingClassification(ListingType.MINI_VIX, False, "VXM is mini VIX")
    if compact.startswith("VXT") or " TAS" in f" {compact} ":
        return ListingClassification(ListingType.TAS, False, "TAS/VXT is separate")
    if _looks_like_spread_or_combination(compact):
        return ListingClassification(
            ListingType.SPREAD_COMBINATION,
            False,
            "calendar spread or combination",
        )
    if _looks_like_weekly_vx(compact):
        return ListingClassification(ListingType.WEEKLY, False, "weekly VX")
    if not compact.startswith("VX"):
        return ListingClassification(ListingType.UNKNOWN, False, "not VX")
    if final_settlement_date != expected_monthly_final_settlement_date:
        return ListingClassification(
            ListingType.NON_MONTHLY_VX,
            False,
            "settlement date does not match monthly calendar evidence",
        )
    return ListingClassification(
        ListingType.STANDARD_MONTHLY,
        True,
        "VX root with matching monthly settlement calendar evidence",
    )


def is_primary_monthly_vx(
    source_symbol: str,
    *,
    final_settlement_date: date,
    expected_monthly_final_settlement_date: date,
) -> bool:
    return classify_vx_listing(
        source_symbol,
        final_settlement_date=final_settlement_date,
        expected_monthly_final_settlement_date=expected_monthly_final_settlement_date,
    ).is_primary


def _looks_like_spread_or_combination(symbol: str) -> bool:
    if symbol.count("VX") > 1:
        return True
    if "-" in symbol:
        return True
    return "SPREAD" in symbol or "COMBO" in symbol or "COMBINATION" in symbol


def _looks_like_weekly_vx(symbol: str) -> bool:
    return re.match(r"^VX\d+[/\s-]", symbol) is not None

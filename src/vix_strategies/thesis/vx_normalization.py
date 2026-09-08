from __future__ import annotations

from datetime import date
from enum import Enum
from math import isfinite


RESCALING_EFFECTIVE_DATE = date(2007, 3, 26)
CANONICAL_COMPARISON_MULTIPLIER = 1000


class PriceScaleRegime(str, Enum):
    PRE_2007_RESCALING = "pre_2007_rescaling"
    POST_2007_STANDARD = "post_2007_standard"


def price_scale_regime_for_date(trade_date: date) -> PriceScaleRegime:
    if trade_date < RESCALING_EFFECTIVE_DATE:
        return PriceScaleRegime.PRE_2007_RESCALING
    return PriceScaleRegime.POST_2007_STANDARD


def normalize_vx_price(trade_date: date, raw_price: float) -> float:
    if not isfinite(raw_price) or raw_price <= 0:
        raise ValueError("raw_price must be positive and finite")
    return raw_price * normalization_factor_for_date(trade_date)


def source_multiplier_for_date(trade_date: date) -> int:
    if price_scale_regime_for_date(trade_date) == PriceScaleRegime.PRE_2007_RESCALING:
        return 100
    return 1000


def normalization_factor_for_date(trade_date: date) -> float:
    if price_scale_regime_for_date(trade_date) == PriceScaleRegime.PRE_2007_RESCALING:
        return 0.1
    return 1.0

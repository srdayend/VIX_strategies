from datetime import date
from math import inf, nan

import pytest

from vix_strategies.thesis.vx_normalization import (
    CANONICAL_COMPARISON_MULTIPLIER,
    PriceScaleRegime,
    normalize_vx_price,
    normalization_factor_for_date,
    price_scale_regime_for_date,
    source_multiplier_for_date,
)


def test_pre_2007_rescale_boundary_normalizes_price_and_multiplier():
    trade_date = date(2007, 3, 23)

    assert price_scale_regime_for_date(trade_date) == PriceScaleRegime.PRE_2007_RESCALING
    assert normalize_vx_price(trade_date, 103.90) == pytest.approx(10.39)
    assert source_multiplier_for_date(trade_date) == 100
    assert normalization_factor_for_date(trade_date) == 0.1
    assert CANONICAL_COMPARISON_MULTIPLIER == 1000


def test_post_2007_rescale_boundary_keeps_display_price_and_uses_1000_multiplier():
    trade_date = date(2007, 3, 26)

    assert price_scale_regime_for_date(trade_date) == PriceScaleRegime.POST_2007_STANDARD
    assert normalize_vx_price(trade_date, 10.39) == pytest.approx(10.39)
    assert source_multiplier_for_date(trade_date) == 1000
    assert normalization_factor_for_date(trade_date) == 1.0


def test_2007_rescaling_preserves_dollar_contract_value_for_documented_example():
    assert 103.90 * source_multiplier_for_date(date(2007, 3, 23)) == pytest.approx(
        normalize_vx_price(date(2007, 3, 26), 10.39)
        * source_multiplier_for_date(date(2007, 3, 26))
    )


@pytest.mark.parametrize("raw_price", [nan, inf, -inf, 0.0, -1.0])
def test_normalization_rejects_non_finite_or_non_positive_prices(raw_price):
    with pytest.raises(ValueError, match="raw_price must be positive and finite"):
        normalize_vx_price(date(2026, 5, 1), raw_price)

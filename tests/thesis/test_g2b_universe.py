from datetime import date

import pytest

from vix_strategies.thesis.vx_universe import (
    ListingType,
    canonical_contract_id,
    classify_vx_listing,
    is_primary_monthly_vx,
)


def test_canonical_contract_id_uses_vx_year_month_identity():
    assert canonical_contract_id(2026, 3) == "VX_202603"


def test_standard_monthly_vx_is_primary_when_calendar_evidence_matches():
    classification = classify_vx_listing(
        "VX H6",
        final_settlement_date=date(2026, 3, 18),
        expected_monthly_final_settlement_date=date(2026, 3, 18),
    )

    assert classification.listing_type == ListingType.STANDARD_MONTHLY
    assert classification.is_primary
    assert is_primary_monthly_vx(
        "VX H6",
        final_settlement_date=date(2026, 3, 18),
        expected_monthly_final_settlement_date=date(2026, 3, 18),
    )


def test_vx_weekly_is_excluded_even_when_root_is_vx():
    classification = classify_vx_listing(
        "VX36/U6",
        final_settlement_date=date(2026, 9, 9),
        expected_monthly_final_settlement_date=date(2026, 9, 16),
    )

    assert classification.listing_type == ListingType.WEEKLY
    assert not classification.is_primary


def test_vxm_mini_vix_is_excluded():
    classification = classify_vx_listing(
        "VXM/U6",
        final_settlement_date=date(2026, 9, 16),
        expected_monthly_final_settlement_date=date(2026, 9, 16),
    )

    assert classification.listing_type == ListingType.MINI_VIX
    assert not classification.is_primary


@pytest.mark.parametrize("source_symbol", ["VXT K6", "VX TAS K6"])
def test_tas_vxt_is_excluded_as_separate_listing_family(source_symbol):
    classification = classify_vx_listing(
        source_symbol,
        final_settlement_date=date(2026, 5, 20),
        expected_monthly_final_settlement_date=date(2026, 5, 20),
    )

    assert classification.listing_type == ListingType.TAS
    assert not classification.is_primary


@pytest.mark.parametrize("source_symbol", ["VX K6-VX M6", "VX K6 / VX M6"])
def test_calendar_spreads_and_combinations_are_excluded(source_symbol):
    classification = classify_vx_listing(
        source_symbol,
        final_settlement_date=date(2026, 5, 20),
        expected_monthly_final_settlement_date=date(2026, 5, 20),
    )

    assert classification.listing_type == ListingType.SPREAD_COMBINATION
    assert not classification.is_primary


def test_vx_symbol_without_matching_calendar_evidence_is_not_primary_monthly():
    classification = classify_vx_listing(
        "VX U6",
        final_settlement_date=date(2026, 9, 9),
        expected_monthly_final_settlement_date=date(2026, 9, 16),
    )

    assert classification.listing_type == ListingType.NON_MONTHLY_VX
    assert not classification.is_primary

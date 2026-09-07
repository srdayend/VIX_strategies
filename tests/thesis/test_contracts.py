from datetime import date

import pytest

from vix_strategies.thesis.contracts import (
    ContractRecord,
    compute_calendar_dte,
    compute_monthly_vx_settlement_date,
)


def test_contract_record_preserves_actual_contract_identity_and_calendar_dte():
    record = ContractRecord(
        contract_id="VXH26",
        trade_date=date(2026, 3, 13),
        settlement_date=date(2026, 3, 18),
        settlement_price=18.25,
        rank_label="M1",
        settlement_date_source="official",
    )

    assert record.contract_id == "VXH26"
    assert record.rank_label == "M1"
    assert record.dte == 5


def test_monthly_vx_settlement_date_uses_third_friday_minus_30_calendar_days():
    settlement = compute_monthly_vx_settlement_date(2026, 3)

    assert settlement == date(2026, 3, 18)


def test_monthly_vx_settlement_date_moves_to_previous_business_day_for_holiday():
    settlement = compute_monthly_vx_settlement_date(
        2026,
        3,
        holidays={date(2026, 3, 18)},
    )

    assert settlement == date(2026, 3, 17)


def test_monthly_vx_settlement_date_moves_when_following_third_friday_is_holiday():
    settlement = compute_monthly_vx_settlement_date(
        2014,
        3,
        holidays={date(2014, 4, 18)},
    )

    assert settlement == date(2014, 3, 18)


def test_official_settlement_date_overrides_rule_derived_date():
    record = ContractRecord.from_monthly_vx(
        contract_id="VXH26",
        trade_date=date(2026, 3, 13),
        contract_year=2026,
        contract_month=3,
        settlement_price=18.25,
        official_settlement_date=date(2026, 3, 17),
    )

    assert record.settlement_date == date(2026, 3, 17)
    assert record.settlement_date_source == "official"


def test_rule_derived_settlement_date_is_marked_as_derived():
    record = ContractRecord.from_monthly_vx(
        contract_id="VXH26",
        trade_date=date(2026, 3, 13),
        contract_year=2026,
        contract_month=3,
        settlement_price=18.25,
    )

    assert record.settlement_date == date(2026, 3, 18)
    assert record.settlement_date_source == "derived"


def test_calendar_dte_uses_calendar_days_across_weekends():
    assert compute_calendar_dte(date(2026, 3, 13), date(2026, 3, 16)) == 3


def test_calendar_dte_rejects_expired_contract_dates():
    with pytest.raises(ValueError, match="settlement_date precedes trade_date"):
        compute_calendar_dte(date(2026, 3, 19), date(2026, 3, 18))


def test_contract_record_rejects_weekly_listing_type_in_g2a_monthly_schema():
    with pytest.raises(ValueError, match="listing_type must be 'monthly'"):
        ContractRecord(
            contract_id="VXH26",
            trade_date=date(2026, 3, 13),
            settlement_date=date(2026, 3, 18),
            settlement_price=18.25,
            settlement_date_source="official",
            listing_type="weekly",
        )

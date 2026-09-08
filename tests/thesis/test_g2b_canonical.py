from datetime import date, datetime, timezone

import pytest

from vix_strategies.thesis.data_sources import SourceFamily
from vix_strategies.thesis.vx_calendar import (
    ContractCalendarEntry,
    SettlementDateValidationStatus,
    SettlementRuleRegime,
)
from vix_strategies.thesis.vx_canonical import (
    ObservationType,
    SampleRole,
    canonicalize_raw_record,
)
from vix_strategies.thesis.vx_normalization import PriceScaleRegime
from vix_strategies.thesis.vx_raw import RawVxRecord
from vix_strategies.thesis.vx_universe import ListingType


def _raw_record(
    *,
    trade_date=date(2026, 5, 1),
    source_symbol="VX K6",
    raw_open="18.20",
    raw_high="18.65",
    raw_low="18.10",
    raw_close="18.40",
    raw_settle="18.45",
):
    return RawVxRecord(
        source_file="current_detail_sample.csv",
        source_family=SourceFamily.CFE_CURRENT_DETAIL,
        source_url="https://www.cboe.com/fixture/current_detail_sample.csv",
        source_sha256="a" * 64,
        retrieval_timestamp=datetime(2026, 9, 8, tzinfo=timezone.utc),
        parser_version="g2b1-vx-raw-v1",
        raw_row_id="current_detail_sample.csv:2",
        source_symbol=source_symbol,
        trade_date=trade_date,
        raw_open=raw_open,
        raw_high=raw_high,
        raw_low=raw_low,
        raw_close=raw_close,
        raw_settle=raw_settle,
        raw_change="0.15",
        raw_volume="100234",
        raw_efp="0",
        raw_open_interest="432100",
    )


def _calendar_entry(
    *,
    contract_id="VX_202605",
    contract_month=date(2026, 5, 1),
    final_settlement_date=date(2026, 5, 20),
):
    return ContractCalendarEntry(
        contract_id=contract_id,
        contract_month=contract_month,
        final_settlement_date=final_settlement_date,
        settlement_rule_regime=SettlementRuleRegime.MODERN,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        evidence_reference="test calendar fixture",
    )


def test_ordinary_settlement_row_becomes_daily_dsp_and_is_curve_eligible():
    row = canonicalize_raw_record(_raw_record(), calendar_entry=_calendar_entry())

    assert row.observation_type == ObservationType.DAILY_DSP
    assert row.listing_type == ListingType.STANDARD_MONTHLY
    assert row.settle_norm == pytest.approx(18.45)
    assert row.is_primary_curve_eligible


def test_final_settlement_date_row_becomes_final_soq_not_daily_curve_point():
    row = canonicalize_raw_record(
        _raw_record(trade_date=date(2026, 5, 20), raw_settle="18.90"),
        calendar_entry=_calendar_entry(final_settlement_date=date(2026, 5, 20)),
    )

    assert row.observation_type == ObservationType.FINAL_SOQ
    assert row.settle_norm == pytest.approx(18.90)
    assert not row.is_primary_curve_eligible


def test_final_soq_allows_zero_ohlc_from_source_without_price_repair():
    row = canonicalize_raw_record(
        _raw_record(
            trade_date=date(2026, 5, 20),
            raw_open="0.00",
            raw_high="0.00",
            raw_low="0.00",
            raw_close="0.00",
            raw_settle="19.05",
        ),
        calendar_entry=_calendar_entry(final_settlement_date=date(2026, 5, 20)),
    )

    assert row.observation_type == ObservationType.FINAL_SOQ
    assert row.open_norm is None
    assert row.high_norm is None
    assert row.low_norm is None
    assert row.close_norm is None
    assert row.settle_norm == pytest.approx(19.05)
    assert "final_soq_zero_ohlc" in row.quality_flags
    assert not row.is_primary_curve_eligible


def test_non_positive_daily_settlement_is_flagged_ineligible_not_forward_filled():
    row = canonicalize_raw_record(
        _raw_record(raw_settle="0.00"),
        calendar_entry=_calendar_entry(),
    )

    assert row.settle_norm is None
    assert "non_positive_settlement" in row.quality_flags
    assert not row.is_primary_curve_eligible


@pytest.mark.parametrize(
    "trade_date, expected_role",
    [
        (date(2026, 5, 1), SampleRole.DEVELOPMENT_CONTAMINATED),
        (date(2026, 5, 4), SampleRole.POST_FREEZE_HOLDOUT),
    ],
)
def test_sample_role_marks_post_2026_05_01_holdout(trade_date, expected_role):
    row = canonicalize_raw_record(
        _raw_record(trade_date=trade_date),
        calendar_entry=_calendar_entry(),
    )

    assert row.sample_role == expected_role


def test_canonical_row_keeps_raw_source_lineage_and_calendar_metadata():
    row = canonicalize_raw_record(_raw_record(), calendar_entry=_calendar_entry())

    assert row.source_file == "current_detail_sample.csv"
    assert row.source_row_id == "current_detail_sample.csv:2"
    assert row.source_sha256 == "a" * 64
    assert row.contract_id == "VX_202605"
    assert row.contract_month == date(2026, 5, 1)
    assert row.final_settlement_date == date(2026, 5, 20)
    assert row.settlement_rule_regime == SettlementRuleRegime.MODERN
    assert (
        row.settlement_date_validation_status
        == SettlementDateValidationStatus.RULE_DERIVED_VALIDATED
    )


def test_canonicalization_applies_official_2007_normalization_to_ohlc_and_settle():
    row = canonicalize_raw_record(
        _raw_record(
            trade_date=date(2004, 3, 26),
            source_symbol="VX K4",
            raw_open="181.00",
            raw_high="185.00",
            raw_low="178.50",
            raw_close="180.50",
            raw_settle="180.50",
        ),
        calendar_entry=ContractCalendarEntry(
            contract_id="VX_200405",
            contract_month=date(2004, 5, 1),
            final_settlement_date=date(2004, 5, 19),
            settlement_rule_regime=SettlementRuleRegime.LEGACY,
            settlement_date_source="rule_derived",
            validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
            evidence_reference="test legacy calendar fixture",
        ),
    )

    assert row.price_scale_regime == PriceScaleRegime.PRE_2007_RESCALING
    assert row.source_multiplier == 100
    assert row.normalization_factor == 0.1
    assert row.open_norm == pytest.approx(18.10)
    assert row.high_norm == pytest.approx(18.50)
    assert row.low_norm == pytest.approx(17.85)
    assert row.close_norm == pytest.approx(18.05)
    assert row.settle_norm == pytest.approx(18.05)


def test_missing_settlement_gets_explicit_quality_flag_and_is_not_forward_filled():
    row = canonicalize_raw_record(
        _raw_record(raw_settle=None),
        calendar_entry=_calendar_entry(),
    )

    assert row.settle_norm is None
    assert "missing_settlement" in row.quality_flags
    assert not row.is_primary_curve_eligible

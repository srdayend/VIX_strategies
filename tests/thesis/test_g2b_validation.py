from dataclasses import replace
from datetime import date

from vix_strategies.thesis.vx_calendar import (
    SettlementDateValidationStatus,
    SettlementRuleRegime,
)
from vix_strategies.thesis.vx_canonical import (
    CanonicalVxRecord,
    ObservationType,
    SampleRole,
)
from vix_strategies.thesis.vx_normalization import PriceScaleRegime
from vix_strategies.thesis.vx_universe import ListingType
from vix_strategies.thesis.vx_validation import (
    canonical_key,
    development_rows,
    validate_canonical_records,
)


def _record(
    *,
    trade_date=date(2026, 5, 1),
    contract_id="VX_202605",
    observation_type=ObservationType.DAILY_DSP,
    settle_norm=18.45,
    source_row_id="current_detail_sample.csv:2",
    source_file="current_detail_sample.csv",
    source_sha256="a" * 64,
    sample_role=SampleRole.DEVELOPMENT_CONTAMINATED,
):
    return CanonicalVxRecord(
        trade_date=trade_date,
        contract_id=contract_id,
        contract_month=date(2026, 5, 1),
        source_symbol="VX K6",
        final_settlement_date=date(2026, 5, 20),
        settlement_rule_regime=SettlementRuleRegime.MODERN,
        settlement_date_source="rule_derived",
        settlement_date_validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        listing_type=ListingType.STANDARD_MONTHLY,
        observation_type=observation_type,
        price_scale_regime=PriceScaleRegime.POST_2007_STANDARD,
        source_multiplier=1000,
        normalization_factor=1.0,
        open_norm=18.20,
        high_norm=18.65,
        low_norm=18.10,
        close_norm=18.40,
        settle_norm=settle_norm,
        volume=100234,
        open_interest=432100,
        source_file=source_file,
        source_row_id=source_row_id,
        source_sha256=source_sha256,
        quality_flags=(),
        sample_role=sample_role,
    )


def test_canonical_uniqueness_key_is_trade_date_contract_id_observation_type():
    record = _record(observation_type=ObservationType.FINAL_SOQ)

    assert canonical_key(record) == (
        date(2026, 5, 1),
        "VX_202605",
        ObservationType.FINAL_SOQ,
    )


def test_identical_duplicates_are_collapsed_deterministically_and_flagged():
    first = _record(source_file="b.csv", source_row_id="b.csv:7", source_sha256="b" * 64)
    second = replace(first, source_file="a.csv", source_row_id="a.csv:2", source_sha256="a" * 64)

    result = validate_canonical_records([first, second])

    assert result.accepted
    assert not result.conflicts
    assert len(result.records) == 1
    assert result.records[0].source_file == "a.csv"
    assert result.records[0].source_row_id == "a.csv:2"
    assert "exact_duplicate_collapsed" in result.records[0].quality_flags


def test_conflicting_duplicates_create_unresolved_conflict_and_block_acceptance():
    first = _record(settle_norm=18.45, source_row_id="a.csv:2")
    conflict = replace(first, settle_norm=18.55, source_row_id="a.csv:3")

    result = validate_canonical_records([first, conflict])

    assert not result.accepted
    assert len(result.conflicts) == 1
    assert result.conflicts[0].key == canonical_key(first)
    assert result.conflicts[0].reason == "conflicting_duplicate"
    assert len(result.conflicts[0].records) == 2


def test_development_rows_excludes_post_freeze_holdout_by_default():
    development = _record(trade_date=date(2026, 5, 1))
    holdout = _record(
        trade_date=date(2026, 5, 4),
        source_row_id="current_detail_sample.csv:3",
        sample_role=SampleRole.POST_FREEZE_HOLDOUT,
    )

    assert development_rows([development, holdout]) == (development,)


def test_development_rows_requires_explicit_opt_in_for_holdout_access():
    development = _record(trade_date=date(2026, 5, 1))
    holdout = _record(
        trade_date=date(2026, 5, 4),
        source_row_id="current_detail_sample.csv:3",
        sample_role=SampleRole.POST_FREEZE_HOLDOUT,
    )

    assert development_rows([development, holdout], include_holdout=True) == (
        development,
        holdout,
    )

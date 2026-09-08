from datetime import date

import pytest

from vix_strategies.thesis.vx_calendar import (
    ContractCalendarEntry,
    SettlementDateValidationStatus,
    SettlementRuleRegime,
    build_contract_calendar_entry,
    compute_legacy_vx_settlement_date,
    compute_modern_vx_settlement_date,
    primary_eligible_calendar_entries,
)


def test_legacy_vx_settlement_date_uses_wednesday_before_same_month_third_friday():
    assert compute_legacy_vx_settlement_date(2004, 5) == date(2004, 5, 19)


def test_modern_vx_settlement_date_uses_thirty_days_before_following_month_third_friday():
    assert compute_modern_vx_settlement_date(2026, 3) == date(2026, 3, 18)


def test_contract_calendar_regime_boundary_uses_2005_10_17_effective_date():
    september = build_contract_calendar_entry(
        contract_year=2005,
        contract_month=9,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        evidence_reference="CFE-2005-28 boundary fixture",
    )
    october = build_contract_calendar_entry(
        contract_year=2005,
        contract_month=10,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        evidence_reference="CFE-2005-28 boundary fixture",
    )

    assert september.settlement_rule_regime == SettlementRuleRegime.LEGACY
    assert september.final_settlement_date == date(2005, 9, 14)
    assert october.settlement_rule_regime == SettlementRuleRegime.MODERN
    assert october.final_settlement_date == date(2005, 10, 19)


def test_modern_vx_settlement_adjusts_when_following_third_friday_is_holiday():
    assert compute_modern_vx_settlement_date(
        2014,
        3,
        holidays={date(2014, 4, 18)},
    ) == date(2014, 3, 18)


def test_primary_eligible_calendar_entries_reject_rule_derived_unvalidated():
    validated = ContractCalendarEntry(
        contract_id="VX_202603",
        contract_month=date(2026, 3, 1),
        final_settlement_date=date(2026, 3, 18),
        settlement_rule_regime=SettlementRuleRegime.MODERN,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        evidence_reference="test validated fixture",
    )
    unvalidated = ContractCalendarEntry(
        contract_id="VX_202604",
        contract_month=date(2026, 4, 1),
        final_settlement_date=date(2026, 4, 15),
        settlement_rule_regime=SettlementRuleRegime.MODERN,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_UNVALIDATED,
        evidence_reference="test unvalidated fixture",
    )

    with pytest.raises(ValueError, match="rule_derived_unvalidated"):
        primary_eligible_calendar_entries([validated, unvalidated])


def test_calendar_entry_requires_evidence_reference():
    with pytest.raises(ValueError, match="evidence_reference is required"):
        build_contract_calendar_entry(
            contract_year=2026,
            contract_month=3,
            settlement_date_source="rule_derived",
            validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
            evidence_reference="",
        )

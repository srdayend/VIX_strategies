import csv
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from vix_strategies.thesis.data_sources import (
    CBOE_CURRENT_DETAIL_SOURCE,
    CBOE_HISTORICAL_ARCHIVE_SOURCE,
)
from vix_strategies.thesis.vx_calendar import (
    ContractCalendarEntry,
    SettlementDateValidationStatus,
    SettlementRuleRegime,
)
from vix_strategies.thesis.vx_canonical import ObservationType, SampleRole
from vix_strategies.thesis.vx_pipeline import (
    G2B1SourceInput,
    RawParserKind,
    run_g2b1_pipeline,
)


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "g2b"


def test_g2b1_fixture_pipeline_emits_reproducible_outputs_and_blocks_conflicts(
    tmp_path,
):
    archive_calendar = ContractCalendarEntry(
        contract_id="VX_200405",
        contract_month=date(2004, 5, 1),
        final_settlement_date=date(2004, 5, 19),
        settlement_rule_regime=SettlementRuleRegime.LEGACY,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        evidence_reference="test legacy calendar fixture",
    )
    current_calendar = ContractCalendarEntry(
        contract_id="VX_202605",
        contract_month=date(2026, 5, 1),
        final_settlement_date=date(2026, 5, 20),
        settlement_rule_regime=SettlementRuleRegime.MODERN,
        settlement_date_source="rule_derived",
        validation_status=SettlementDateValidationStatus.RULE_DERIVED_VALIDATED,
        evidence_reference="test modern calendar fixture",
    )

    result = run_g2b1_pipeline(
        [
            G2B1SourceInput(
                local_path=FIXTURE_DIR / "archive_contract_sample.csv",
                source_spec=CBOE_HISTORICAL_ARCHIVE_SOURCE,
                source_url="https://www.cboe.com/fixture/archive_contract_sample.csv",
                retrieval_timestamp=datetime(2026, 9, 8, 12, tzinfo=timezone.utc),
                parser_kind=RawParserKind.ARCHIVE_CONTRACT,
                calendar_entry=archive_calendar,
            ),
            G2B1SourceInput(
                local_path=FIXTURE_DIR / "pipeline_current_conflict_sample.csv",
                source_spec=CBOE_CURRENT_DETAIL_SOURCE,
                source_url=(
                    "https://www.cboe.com/fixture/"
                    "pipeline_current_conflict_sample.csv"
                ),
                retrieval_timestamp=datetime(2026, 9, 8, 13, tzinfo=timezone.utc),
                parser_kind=RawParserKind.CURRENT_DETAIL,
                calendar_entry=current_calendar,
            ),
        ],
        output_dir=tmp_path,
        run_timestamp=datetime(2026, 9, 8, 14, tzinfo=timezone.utc),
    )

    assert result.status == "not_accepted"
    assert len(result.manifest_records) == 2
    assert result.output_paths.source_manifest.exists()
    assert result.output_paths.canonical_records.exists()
    assert result.output_paths.conflict_report.exists()
    assert result.output_paths.run_metadata.exists()

    manifest = json.loads(result.output_paths.source_manifest.read_text(encoding="utf-8"))
    assert {row["source_family"] for row in manifest} == {
        "cfe_historical_archive",
        "cfe_current_detail",
    }
    assert all(row["source_sha256"] for row in manifest)
    assert all(row["retrieval_timestamp"] for row in manifest)

    assert all(row.source_file and row.source_row_id and row.source_sha256 for row in result.records)
    assert {row.settlement_rule_regime for row in result.records} == {
        SettlementRuleRegime.LEGACY,
        SettlementRuleRegime.MODERN,
    }

    legacy = next(row for row in result.records if row.contract_id == "VX_200405")
    assert legacy.settle_norm == pytest.approx(18.05)
    modern_holdout = next(
        row
        for row in result.records
        if row.contract_id == "VX_202605" and row.trade_date == date(2026, 5, 4)
    )
    assert modern_holdout.settle_norm == pytest.approx(18.75)
    assert modern_holdout.sample_role == SampleRole.POST_FREEZE_HOLDOUT
    assert modern_holdout not in result.development_records

    final_soq = next(
        row
        for row in result.records
        if row.contract_id == "VX_202605" and row.trade_date == date(2026, 5, 20)
    )
    assert final_soq.observation_type == ObservationType.FINAL_SOQ
    assert not final_soq.is_primary_curve_eligible

    conflicts = json.loads(result.output_paths.conflict_report.read_text(encoding="utf-8"))
    assert conflicts[0]["reason"] == "conflicting_duplicate"
    assert conflicts[0]["key"] == ["2026-05-01", "VX_202605", "DAILY_DSP"]

    with result.output_paths.canonical_records.open(newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    assert "M1" not in header
    assert "M2" not in header
    assert "rank_label" not in header

    metadata = json.loads(result.output_paths.run_metadata.read_text(encoding="utf-8"))
    assert metadata["status"] == "not_accepted"
    assert metadata["source_count"] == 2
    assert metadata["conflict_count"] == 1
    assert metadata["run_timestamp"] == "2026-09-08T14:00:00+00:00"


def test_g2b1_cli_builds_fixture_pipeline_outputs(tmp_path):
    config_path = tmp_path / "g2b1_sources.json"
    output_dir = tmp_path / "out"
    config_path.write_text(
        json.dumps(
            {
                "run_timestamp": "2026-09-08T14:00:00+00:00",
                "sources": [
                    {
                        "local_path": str(FIXTURE_DIR / "archive_contract_sample.csv"),
                        "source_family": "cfe_historical_archive",
                        "source_url": (
                            "https://www.cboe.com/fixture/"
                            "archive_contract_sample.csv"
                        ),
                        "retrieval_timestamp": "2026-09-08T12:00:00+00:00",
                        "parser_kind": "archive_contract",
                        "calendar_entry": {
                            "contract_id": "VX_200405",
                            "contract_month": "2004-05-01",
                            "final_settlement_date": "2004-05-19",
                            "settlement_rule_regime": "legacy",
                            "settlement_date_source": "rule_derived",
                            "validation_status": "rule_derived_validated",
                            "evidence_reference": "test legacy calendar fixture",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_g2b1_vx_canonical_panel.py",
            "--source-config",
            str(config_path),
            "--output-dir",
            str(output_dir),
        ],
        cwd=Path.cwd(),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    metadata = json.loads((output_dir / "run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["status"] == "accepted"
    assert (output_dir / "source_manifest.json").exists()
    assert (output_dir / "canonical_vx_contract_dates.csv").exists()

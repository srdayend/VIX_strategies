from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vix_strategies.thesis.data_sources import (  # noqa: E402
    CBOE_CURRENT_DETAIL_SOURCE,
    CBOE_HISTORICAL_ARCHIVE_SOURCE,
)
from vix_strategies.thesis.vx_calendar import (  # noqa: E402
    ContractCalendarEntry,
    SettlementDateValidationStatus,
    SettlementRuleRegime,
)
from vix_strategies.thesis.vx_pipeline import (  # noqa: E402
    G2B1SourceInput,
    RawParserKind,
    run_g2b1_pipeline,
)


SOURCE_SPECS = {
    CBOE_HISTORICAL_ARCHIVE_SOURCE.source_family.value: CBOE_HISTORICAL_ARCHIVE_SOURCE,
    CBOE_CURRENT_DETAIL_SOURCE.source_family.value: CBOE_CURRENT_DETAIL_SOURCE,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the G2-B1 canonical VX contract-date panel from local raw Cboe files.",
    )
    parser.add_argument("--source-config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    config = json.loads(args.source_config.read_text(encoding="utf-8"))
    sources = [_source_input_from_config(row) for row in config["sources"]]
    run_timestamp = _parse_datetime(config["run_timestamp"]) if "run_timestamp" in config else None
    result = run_g2b1_pipeline(
        sources,
        output_dir=args.output_dir,
        run_timestamp=run_timestamp,
    )
    print(
        json.dumps(
            {
                "status": result.status,
                "canonical_records": len(result.records),
                "conflicts": len(result.conflicts),
                "output_dir": str(args.output_dir),
            },
            sort_keys=True,
        )
    )
    return 1 if result.conflicts else 0


def _source_input_from_config(row: dict) -> G2B1SourceInput:
    source_family = row["source_family"]
    if source_family not in SOURCE_SPECS:
        raise ValueError(f"unsupported source_family: {source_family}")
    return G2B1SourceInput(
        local_path=Path(row["local_path"]),
        source_spec=SOURCE_SPECS[source_family],
        source_url=row["source_url"],
        retrieval_timestamp=_parse_datetime(row["retrieval_timestamp"]),
        parser_kind=RawParserKind(row["parser_kind"]),
        calendar_entry=_calendar_entry_from_config(row["calendar_entry"]),
    )


def _calendar_entry_from_config(row: dict) -> ContractCalendarEntry:
    return ContractCalendarEntry(
        contract_id=row["contract_id"],
        contract_month=_parse_date(row["contract_month"]),
        final_settlement_date=_parse_date(row["final_settlement_date"]),
        settlement_rule_regime=SettlementRuleRegime(row["settlement_rule_regime"]),
        settlement_date_source=row["settlement_date_source"],
        validation_status=SettlementDateValidationStatus(row["validation_status"]),
        evidence_reference=row["evidence_reference"],
    )


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


if __name__ == "__main__":
    raise SystemExit(main())

from datetime import datetime, timezone
from pathlib import Path

import pytest

from vix_strategies.thesis.data_sources import (
    CBOE_CURRENT_DETAIL_SOURCE,
    CBOE_HISTORICAL_ARCHIVE_SOURCE,
    build_manifest_record,
)
from vix_strategies.thesis.vx_raw import (
    RAW_VX_PARSER_VERSION,
    parse_archive_contract_file,
    parse_current_detail_file,
)


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "g2b"


def _manifest(path: Path, source_spec):
    return build_manifest_record(
        source_spec=source_spec,
        source_url=f"https://www.cboe.com/fixture/{path.name}",
        retrieval_timestamp=datetime(2026, 9, 8, tzinfo=timezone.utc),
        local_path=path,
        parser_version=RAW_VX_PARSER_VERSION,
        ingest_status="fixture",
    )


def test_archive_parser_preserves_source_values_without_normalization():
    path = FIXTURE_DIR / "archive_contract_sample.csv"

    records = parse_archive_contract_file(
        path,
        manifest_record=_manifest(path, CBOE_HISTORICAL_ARCHIVE_SOURCE),
    )

    first = records[0]
    assert first.source_symbol == "VX K4"
    assert first.trade_date.isoformat() == "2004-03-26"
    assert first.raw_open == "181.00"
    assert first.raw_high == "185.00"
    assert first.raw_low == "178.50"
    assert first.raw_close == "180.50"
    assert first.raw_settle == "180.50"
    assert first.raw_change == "-0.50"
    assert first.raw_volume == "123"
    assert first.raw_efp == "0"
    assert first.raw_open_interest == "456"


def test_archive_parser_keeps_source_missingness_and_deterministic_row_ids():
    path = FIXTURE_DIR / "archive_contract_sample.csv"

    records = parse_archive_contract_file(
        path,
        manifest_record=_manifest(path, CBOE_HISTORICAL_ARCHIVE_SOURCE),
    )

    second = records[1]
    assert second.raw_row_id == "archive_contract_sample.csv:3"
    assert second.raw_open is None
    assert second.raw_high is None
    assert second.raw_low is None
    assert second.raw_close is None
    assert second.raw_settle == "181.25"
    assert second.raw_volume is None
    assert second.raw_efp is None
    assert second.raw_open_interest is None


def test_parser_attaches_manifest_lineage_to_each_raw_record():
    path = FIXTURE_DIR / "current_detail_sample.csv"
    manifest = _manifest(path, CBOE_CURRENT_DETAIL_SOURCE)

    records = parse_current_detail_file(path, manifest_record=manifest)

    assert len(records) == 2
    assert records[0].source_file == "current_detail_sample.csv"
    assert records[0].source_family == CBOE_CURRENT_DETAIL_SOURCE.source_family
    assert records[0].source_url == "https://www.cboe.com/fixture/current_detail_sample.csv"
    assert records[0].source_sha256 == manifest.source_sha256
    assert records[0].retrieval_timestamp == manifest.retrieval_timestamp
    assert records[0].parser_version == RAW_VX_PARSER_VERSION
    assert records[0].raw_row_id == "current_detail_sample.csv:2"


def test_parser_fails_loudly_when_required_columns_are_missing(tmp_path):
    path = tmp_path / "broken.csv"
    path.write_text(
        "Trade Date,Futures,Open,High,Low,Close,Change,Total Volume,EFP,Open Interest\n"
        "2026-05-01,VX K6,18.20,18.65,18.10,18.40,0.15,100234,0,432100\n",
        encoding="utf-8",
    )
    manifest = _manifest(path, CBOE_CURRENT_DETAIL_SOURCE)

    with pytest.raises(ValueError, match="missing required source columns: Settle"):
        parse_current_detail_file(path, manifest_record=manifest)


def test_parser_fails_loudly_for_malformed_trade_date(tmp_path):
    path = tmp_path / "bad_date.csv"
    path.write_text(
        "Trade Date,Futures,Open,High,Low,Close,Settle,Change,Total Volume,EFP,Open Interest\n"
        "not-a-date,VX K6,18.20,18.65,18.10,18.40,18.45,0.15,100234,0,432100\n",
        encoding="utf-8",
    )
    manifest = _manifest(path, CBOE_CURRENT_DETAIL_SOURCE)

    with pytest.raises(ValueError, match="invalid Trade Date at bad_date.csv:2"):
        parse_current_detail_file(path, manifest_record=manifest)

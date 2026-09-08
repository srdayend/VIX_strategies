from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from vix_strategies.thesis.data_sources import SourceFamily, SourceManifestRecord


RAW_VX_PARSER_VERSION = "g2b1-vx-raw-v1"

REQUIRED_SOURCE_COLUMNS = (
    "Trade Date",
    "Futures",
    "Open",
    "High",
    "Low",
    "Close",
    "Settle",
    "Change",
    "Total Volume",
    "EFP",
    "Open Interest",
)


@dataclass(frozen=True)
class RawVxRecord:
    source_file: str
    source_family: SourceFamily
    source_url: str
    source_sha256: str
    retrieval_timestamp: datetime
    parser_version: str
    raw_row_id: str
    source_symbol: str
    trade_date: date
    raw_open: Optional[str]
    raw_high: Optional[str]
    raw_low: Optional[str]
    raw_close: Optional[str]
    raw_settle: Optional[str]
    raw_change: Optional[str]
    raw_volume: Optional[str]
    raw_efp: Optional[str]
    raw_open_interest: Optional[str]


def parse_archive_contract_file(
    path: Path,
    *,
    manifest_record: SourceManifestRecord,
) -> List[RawVxRecord]:
    return _parse_contract_file(path, manifest_record=manifest_record)


def parse_current_detail_file(
    path: Path,
    *,
    manifest_record: SourceManifestRecord,
) -> List[RawVxRecord]:
    return _parse_contract_file(path, manifest_record=manifest_record)


def _parse_contract_file(
    path: Path,
    *,
    manifest_record: SourceManifestRecord,
) -> List[RawVxRecord]:
    _validate_manifest_path(path, manifest_record)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames or (), REQUIRED_SOURCE_COLUMNS)
        records = []
        for line_number, row in enumerate(reader, start=2):
            row_id = f"{path.name}:{line_number}"
            trade_date = _parse_trade_date(row["Trade Date"], row_id)
            source_symbol = _missing_to_none(row["Futures"])
            if source_symbol is None:
                raise ValueError(f"missing Futures at {row_id}")
            records.append(
                RawVxRecord(
                    source_file=manifest_record.source_filename,
                    source_family=manifest_record.source_family,
                    source_url=manifest_record.source_url,
                    source_sha256=manifest_record.source_sha256,
                    retrieval_timestamp=manifest_record.retrieval_timestamp,
                    parser_version=manifest_record.parser_version,
                    raw_row_id=row_id,
                    source_symbol=source_symbol,
                    trade_date=trade_date,
                    raw_open=_missing_to_none(row["Open"]),
                    raw_high=_missing_to_none(row["High"]),
                    raw_low=_missing_to_none(row["Low"]),
                    raw_close=_missing_to_none(row["Close"]),
                    raw_settle=_missing_to_none(row["Settle"]),
                    raw_change=_missing_to_none(row["Change"]),
                    raw_volume=_missing_to_none(row["Total Volume"]),
                    raw_efp=_missing_to_none(row["EFP"]),
                    raw_open_interest=_missing_to_none(row["Open Interest"]),
                )
            )
    return records


def _validate_manifest_path(path: Path, manifest_record: SourceManifestRecord) -> None:
    if path.resolve() != manifest_record.local_path.resolve():
        raise ValueError("manifest local_path does not match parser path")


def _require_columns(fieldnames: Iterable[str], required: Iterable[str]) -> None:
    present = set(fieldnames)
    missing = [name for name in required if name not in present]
    if missing:
        raise ValueError("missing required source columns: " + ", ".join(missing))


def _parse_trade_date(value: str, row_id: str) -> date:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid Trade Date at {row_id}: {value}")


def _missing_to_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped

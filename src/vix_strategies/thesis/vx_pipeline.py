from __future__ import annotations

import csv
import json
from dataclasses import dataclass, fields
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from vix_strategies.thesis.data_sources import (
    SourceManifestRecord,
    SourceSpec,
    build_manifest_record,
)
from vix_strategies.thesis.vx_calendar import ContractCalendarEntry
from vix_strategies.thesis.vx_canonical import CanonicalVxRecord, canonicalize_raw_record
from vix_strategies.thesis.vx_raw import (
    RAW_VX_PARSER_VERSION,
    RawVxRecord,
    parse_archive_contract_file,
    parse_current_detail_file,
)
from vix_strategies.thesis.vx_validation import (
    CanonicalConflict,
    development_rows,
    validate_canonical_records,
)


class RawParserKind(str, Enum):
    ARCHIVE_CONTRACT = "archive_contract"
    CURRENT_DETAIL = "current_detail"


@dataclass(frozen=True)
class G2B1SourceInput:
    local_path: Path
    source_spec: SourceSpec
    source_url: str
    retrieval_timestamp: datetime
    parser_kind: RawParserKind
    calendar_entry: ContractCalendarEntry


@dataclass(frozen=True)
class G2B1OutputPaths:
    source_manifest: Path
    canonical_records: Path
    conflict_report: Path
    run_metadata: Path


@dataclass(frozen=True)
class G2B1PipelineResult:
    status: str
    manifest_records: Tuple[SourceManifestRecord, ...]
    raw_records: Tuple[RawVxRecord, ...]
    records: Tuple[CanonicalVxRecord, ...]
    development_records: Tuple[CanonicalVxRecord, ...]
    conflicts: Tuple[CanonicalConflict, ...]
    output_paths: G2B1OutputPaths


def run_g2b1_pipeline(
    sources: Iterable[G2B1SourceInput],
    *,
    output_dir: Path,
    run_timestamp: Optional[datetime] = None,
) -> G2B1PipelineResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_timestamp = run_timestamp or datetime.now(timezone.utc)

    manifest_records: List[SourceManifestRecord] = []
    raw_records: List[RawVxRecord] = []
    canonical_records: List[CanonicalVxRecord] = []

    for source in sources:
        manifest = build_manifest_record(
            source_spec=source.source_spec,
            source_url=source.source_url,
            retrieval_timestamp=source.retrieval_timestamp,
            local_path=source.local_path,
            parser_version=RAW_VX_PARSER_VERSION,
            ingest_status="local_available",
        )
        manifest_records.append(manifest)
        parsed = _parse_source_file(source.parser_kind, source.local_path, manifest)
        raw_records.extend(parsed)
        canonical_records.extend(
            canonicalize_raw_record(record, calendar_entry=source.calendar_entry)
            for record in parsed
        )

    validation = validate_canonical_records(canonical_records)
    status = "accepted" if validation.accepted else "not_accepted"
    output_paths = G2B1OutputPaths(
        source_manifest=output_dir / "source_manifest.json",
        canonical_records=output_dir / "canonical_vx_contract_dates.csv",
        conflict_report=output_dir / "canonical_conflicts.json",
        run_metadata=output_dir / "run_metadata.json",
    )

    _write_json(output_paths.source_manifest, [_manifest_to_dict(row) for row in manifest_records])
    _write_canonical_csv(output_paths.canonical_records, validation.records)
    _write_json(output_paths.conflict_report, [_conflict_to_dict(conflict) for conflict in validation.conflicts])
    _write_json(
        output_paths.run_metadata,
        {
            "pipeline": "g2b1_vx_canonical_panel",
            "status": status,
            "run_timestamp": run_timestamp.isoformat(),
            "source_count": len(manifest_records),
            "raw_record_count": len(raw_records),
            "canonical_record_count": len(validation.records),
            "conflict_count": len(validation.conflicts),
            "parser_version": RAW_VX_PARSER_VERSION,
        },
    )

    return G2B1PipelineResult(
        status=status,
        manifest_records=tuple(manifest_records),
        raw_records=tuple(raw_records),
        records=validation.records,
        development_records=development_rows(validation.records),
        conflicts=validation.conflicts,
        output_paths=output_paths,
    )


def _parse_source_file(
    parser_kind: RawParserKind,
    path: Path,
    manifest_record: SourceManifestRecord,
) -> List[RawVxRecord]:
    if parser_kind == RawParserKind.ARCHIVE_CONTRACT:
        return parse_archive_contract_file(path, manifest_record=manifest_record)
    if parser_kind == RawParserKind.CURRENT_DETAIL:
        return parse_current_detail_file(path, manifest_record=manifest_record)
    raise ValueError(f"unsupported parser_kind: {parser_kind}")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_canonical_csv(path: Path, records: Iterable[CanonicalVxRecord]) -> None:
    fieldnames = [field.name for field in fields(CanonicalVxRecord)]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({name: _serialize(getattr(record, name)) for name in fieldnames})


def _manifest_to_dict(record: SourceManifestRecord) -> dict:
    return {
        "source_family": record.source_family.value,
        "source_url": record.source_url,
        "retrieval_timestamp": record.retrieval_timestamp.isoformat(),
        "local_path": str(record.local_path),
        "source_sha256": record.source_sha256,
        "source_filename": record.source_filename,
        "parser_version": record.parser_version,
        "ingest_status": record.ingest_status,
    }


def _conflict_to_dict(conflict: CanonicalConflict) -> dict:
    return {
        "key": [
            conflict.key[0].isoformat(),
            conflict.key[1],
            conflict.key[2].value,
        ],
        "reason": conflict.reason,
        "records": [_canonical_to_dict(record) for record in conflict.records],
    }


def _canonical_to_dict(record: CanonicalVxRecord) -> dict:
    return {
        field.name: _serialize(getattr(record, field.name))
        for field in fields(CanonicalVxRecord)
    }


def _serialize(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, tuple):
        return list(value)
    return value

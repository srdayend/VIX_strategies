from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from typing import Dict, Iterable, List, Tuple

from vix_strategies.thesis.vx_canonical import (
    CanonicalVxRecord,
    ObservationType,
    SampleRole,
)


CanonicalKey = Tuple[date, str, ObservationType]


@dataclass(frozen=True)
class CanonicalConflict:
    key: CanonicalKey
    reason: str
    records: Tuple[CanonicalVxRecord, ...]


@dataclass(frozen=True)
class CanonicalValidationResult:
    records: Tuple[CanonicalVxRecord, ...]
    conflicts: Tuple[CanonicalConflict, ...]

    @property
    def accepted(self) -> bool:
        return not self.conflicts


def canonical_key(record: CanonicalVxRecord) -> CanonicalKey:
    return (record.trade_date, record.contract_id, record.observation_type)


def validate_canonical_records(
    records: Iterable[CanonicalVxRecord],
) -> CanonicalValidationResult:
    grouped: Dict[CanonicalKey, List[CanonicalVxRecord]] = {}
    for record in records:
        grouped.setdefault(canonical_key(record), []).append(record)

    accepted_records: List[CanonicalVxRecord] = []
    conflicts: List[CanonicalConflict] = []
    for key in sorted(grouped):
        group = sorted(grouped[key], key=_provenance_sort_key)
        if len(group) == 1:
            accepted_records.append(group[0])
        elif _all_same_canonical_values(group):
            accepted_records.append(_with_quality_flag(group[0], "exact_duplicate_collapsed"))
        else:
            conflicts.append(
                CanonicalConflict(
                    key=key,
                    reason="conflicting_duplicate",
                    records=tuple(group),
                )
            )

    return CanonicalValidationResult(
        records=tuple(accepted_records),
        conflicts=tuple(conflicts),
    )


def development_rows(
    records: Iterable[CanonicalVxRecord],
    *,
    include_holdout: bool = False,
) -> Tuple[CanonicalVxRecord, ...]:
    if include_holdout:
        return tuple(records)
    return tuple(
        record
        for record in records
        if record.sample_role == SampleRole.DEVELOPMENT_CONTAMINATED
    )


def _provenance_sort_key(record: CanonicalVxRecord) -> Tuple[str, str, str]:
    return (record.source_file, record.source_row_id, record.source_sha256)


def _all_same_canonical_values(records: List[CanonicalVxRecord]) -> bool:
    first = _canonical_value_tuple(records[0])
    return all(_canonical_value_tuple(record) == first for record in records[1:])


def _canonical_value_tuple(record: CanonicalVxRecord) -> Tuple[object, ...]:
    return (
        record.trade_date,
        record.contract_id,
        record.contract_month,
        record.source_symbol,
        record.final_settlement_date,
        record.settlement_rule_regime,
        record.settlement_date_source,
        record.settlement_date_validation_status,
        record.listing_type,
        record.observation_type,
        record.price_scale_regime,
        record.source_multiplier,
        record.normalization_factor,
        record.open_norm,
        record.high_norm,
        record.low_norm,
        record.close_norm,
        record.settle_norm,
        record.volume,
        record.open_interest,
        record.sample_role,
    )


def _with_quality_flag(record: CanonicalVxRecord, flag: str) -> CanonicalVxRecord:
    if flag in record.quality_flags:
        return record
    return replace(record, quality_flags=tuple([*record.quality_flags, flag]))

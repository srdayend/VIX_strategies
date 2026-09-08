from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class SourceFamily(str, Enum):
    CFE_HISTORICAL_ARCHIVE = "cfe_historical_archive"
    CFE_CURRENT_DETAIL = "cfe_current_detail"


@dataclass(frozen=True)
class SourceSpec:
    source_family: SourceFamily
    name: str
    registry_url: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if not self.registry_url:
            raise ValueError("registry_url is required")


CBOE_HISTORICAL_ARCHIVE_SOURCE = SourceSpec(
    source_family=SourceFamily.CFE_HISTORICAL_ARCHIVE,
    name="CFE Historical Archive VX Price and Volume Detail",
    registry_url=(
        "https://www.cboe.com/markets/us/futures/market-statistics/"
        "historical-data/settlement-archive"
    ),
)

CBOE_CURRENT_DETAIL_SOURCE = SourceSpec(
    source_family=SourceFamily.CFE_CURRENT_DETAIL,
    name="CFE Price and Volume Detail for VX Futures",
    registry_url=(
        "https://www.cboe.com/markets/us/futures/market-statistics/"
        "historical-data/futures/"
    ),
)


@dataclass(frozen=True)
class SourceManifestRecord:
    source_family: SourceFamily
    source_url: str
    retrieval_timestamp: datetime
    local_path: Path
    source_sha256: str
    source_filename: str
    parser_version: str
    ingest_status: str

    def __post_init__(self) -> None:
        if not self.source_url:
            raise ValueError("source_url is required")
        if self.retrieval_timestamp is None:
            raise ValueError("retrieval_timestamp is required")
        if self.local_path is None:
            raise ValueError("local_path is required")
        if not self.source_sha256:
            raise ValueError("source_sha256 is required")
        if not self.source_filename:
            raise ValueError("source_filename is required")
        if not self.parser_version:
            raise ValueError("parser_version is required")
        if not self.ingest_status:
            raise ValueError("ingest_status is required")
        if sha256_file(self.local_path) != self.source_sha256:
            raise ValueError("source_sha256 does not match local_path")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest_record(
    *,
    source_spec: SourceSpec,
    source_url: str,
    retrieval_timestamp: datetime,
    local_path: Path,
    parser_version: str,
    ingest_status: str,
) -> SourceManifestRecord:
    return SourceManifestRecord(
        source_family=source_spec.source_family,
        source_url=source_url,
        retrieval_timestamp=retrieval_timestamp,
        local_path=local_path,
        source_sha256=sha256_file(local_path),
        source_filename=local_path.name,
        parser_version=parser_version,
        ingest_status=ingest_status,
    )

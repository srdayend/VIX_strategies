from datetime import datetime, timezone

import pytest

from vix_strategies.thesis.data_sources import (
    CBOE_CURRENT_DETAIL_SOURCE,
    CBOE_HISTORICAL_ARCHIVE_SOURCE,
    SourceFamily,
    SourceManifestRecord,
    build_manifest_record,
    sha256_file,
)


def test_sha256_file_hashes_fixture_bytes(tmp_path):
    fixture = tmp_path / "vx_fixture.csv"
    fixture.write_bytes(b"Cboe VX fixture\n")

    assert sha256_file(fixture) == (
        "5246655078cad977c08cf754441297104944aa13b15a804e147aa74c593b43a6"
    )


def test_manifest_record_requires_complete_source_lineage(tmp_path):
    fixture = tmp_path / "VX_2004_05.csv"
    fixture.write_text("Trade Date,Settle\n2004-03-26,180.50\n", encoding="utf-8")
    retrieved_at = datetime(2026, 9, 8, 12, 30, tzinfo=timezone.utc)

    record = build_manifest_record(
        source_spec=CBOE_HISTORICAL_ARCHIVE_SOURCE,
        source_url="https://www.cboe.com/example/VX_2004_05.csv",
        retrieval_timestamp=retrieved_at,
        local_path=fixture,
        parser_version="raw-v1",
        ingest_status="downloaded",
    )

    assert record.source_family == SourceFamily.CFE_HISTORICAL_ARCHIVE
    assert record.source_url == "https://www.cboe.com/example/VX_2004_05.csv"
    assert record.retrieval_timestamp == retrieved_at
    assert record.local_path == fixture
    assert record.source_filename == "VX_2004_05.csv"
    assert record.source_sha256 == sha256_file(fixture)
    assert record.parser_version == "raw-v1"
    assert record.ingest_status == "downloaded"


def test_manifest_record_rejects_checksum_mismatch(tmp_path):
    fixture = tmp_path / "VX_current.csv"
    fixture.write_text("Trade Date,Settle\n2026-05-04,18.25\n", encoding="utf-8")

    with pytest.raises(ValueError, match="source_sha256 does not match local_path"):
        SourceManifestRecord(
            source_family=CBOE_CURRENT_DETAIL_SOURCE.source_family,
            source_url="https://www.cboe.com/example/VX_current.csv",
            retrieval_timestamp=datetime(2026, 9, 8, tzinfo=timezone.utc),
            local_path=fixture,
            source_sha256="0" * 64,
            source_filename="VX_current.csv",
            parser_version="raw-v1",
            ingest_status="downloaded",
        )


@pytest.mark.parametrize(
    "missing_field, kwargs",
    [
        ("source_url", {"source_url": ""}),
        ("parser_version", {"parser_version": ""}),
        ("ingest_status", {"ingest_status": ""}),
    ],
)
def test_manifest_record_rejects_missing_required_metadata(
    tmp_path, missing_field, kwargs
):
    fixture = tmp_path / "VX_current.csv"
    fixture.write_text("Trade Date,Settle\n2026-05-04,18.25\n", encoding="utf-8")

    base_kwargs = {
        "source_family": SourceFamily.CFE_CURRENT_DETAIL,
        "source_url": "https://www.cboe.com/example/VX_current.csv",
        "retrieval_timestamp": datetime(2026, 9, 8, tzinfo=timezone.utc),
        "local_path": fixture,
        "source_sha256": sha256_file(fixture),
        "source_filename": "VX_current.csv",
        "parser_version": "raw-v1",
        "ingest_status": "downloaded",
    }
    base_kwargs.update(kwargs)

    with pytest.raises(ValueError, match=f"{missing_field} is required"):
        SourceManifestRecord(**base_kwargs)

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_TERM_STRUCTURE_PATH = Path.home() / "Downloads" / "VIX_futures_term_structure.xlsx"
DEFAULT_FUTURES_BY_MATURITY_PATH = Path.home() / "Downloads" / "VIX_futures_by_maturity (1).xlsx"


@dataclass(frozen=True)
class SourcePaths:
    term_structure: Path
    futures_by_maturity: Path
    vix_index: Path


def _env_path(name: str) -> Path | None:
    raw = os.environ.get(name)
    return Path(raw).expanduser() if raw else None


def find_vix_index_path() -> Path:
    env_path = _env_path("VIX_INDEX_PATH")
    if env_path:
        return env_path

    one_drive = Path.home() / "OneDrive"
    if one_drive.exists():
        matches = list(one_drive.rglob("CBOE_VIX_Index_Daily_OHLC.xlsx"))
        if matches:
            return matches[0]

    return Path.home() / "Downloads" / "CBOE_VIX_Index_Daily_OHLC.xlsx"


def get_source_paths() -> SourcePaths:
    return SourcePaths(
        term_structure=_env_path("VIX_TERM_STRUCTURE_PATH") or DEFAULT_TERM_STRUCTURE_PATH,
        futures_by_maturity=_env_path("VIX_FUTURES_BY_MATURITY_PATH") or DEFAULT_FUTURES_BY_MATURITY_PATH,
        vix_index=find_vix_index_path(),
    )


def validate_source_paths(paths: SourcePaths) -> None:
    missing = [str(path) for path in (paths.term_structure, paths.futures_by_maturity, paths.vix_index) if not path.exists()]
    if missing:
        joined = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing source file(s):\n{joined}")

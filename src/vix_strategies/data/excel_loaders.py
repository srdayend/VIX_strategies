from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .source_paths import get_source_paths, validate_source_paths


SETTLE_COLUMNS = [f"M{i} Settle" for i in range(1, 10)]


def load_term_structure(path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.term_structure
    df = pd.read_excel(source, sheet_name="Term Structure")

    updates: dict[str, pd.Series] = {"Trade Date": pd.to_datetime(df["Trade Date"])}
    for col in SETTLE_COLUMNS:
        if col in df.columns:
            updates[col] = pd.to_numeric(df[col], errors="coerce")
    if "Complete 9-Maturity Curve" in df.columns:
        updates["Complete 9-Maturity Curve"] = df["Complete 9-Maturity Curve"].fillna(False).astype(bool)

    return df.assign(**updates).sort_values("Trade Date").reset_index(drop=True)


def load_vix_index(path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.vix_index
    df = pd.read_excel(source, sheet_name="VIX_Index_Daily")

    updates: dict[str, pd.Series] = {"Date": pd.to_datetime(df["Date"])}
    for col in ["Open", "High", "Low", "Close"]:
        updates[col] = pd.to_numeric(df[col], errors="coerce")

    return df.assign(**updates).sort_values("Date").reset_index(drop=True)


def load_trading_periods(path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.futures_by_maturity
    df = pd.read_excel(source, sheet_name="Trading Periods")

    updates: dict[str, pd.Series] = {col: pd.to_datetime(df[col]) for col in ["First Trade Date", "Last Trade Date"]}
    return df.assign(**updates)


def load_maturity_sheet(sheet_name: str, path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.futures_by_maturity
    df = pd.read_excel(source, sheet_name=sheet_name)

    updates: dict[str, pd.Series] = {"Trade Date": pd.to_datetime(df["Trade Date"])}
    for col in ["Open", "High", "Low", "Close", "Settle", "Change", "Total Volume", "EFP", "Open Interest"]:
        if col in df.columns:
            updates[col] = pd.to_numeric(df[col], errors="coerce")

    return df.assign(**updates).sort_values("Trade Date").reset_index(drop=True)


def add_term_structure_features(term: pd.DataFrame) -> pd.DataFrame:
    near = term["M1 Settle"]
    updates: dict[str, pd.Series] = {}
    for far in [2, 3, 4, 5, 6, 7, 8, 9]:
        far_col = f"M{far} Settle"
        if far_col in term.columns:
            updates[f"m1_m{far}_spread"] = term[far_col] - near
            updates[f"m1_m{far}_pct"] = term[far_col] / near - 1
    df = term.assign(**updates)
    front_state = np.select(
        [df["m1_m2_spread"] > 0, df["m1_m2_spread"] < 0],
        ["contango", "backwardation"],
        default="flat",
    )
    return df.assign(front_state=front_state)


def build_analysis_frame() -> pd.DataFrame:
    paths = get_source_paths()
    validate_source_paths(paths)

    term = add_term_structure_features(load_term_structure(paths.term_structure))
    vix = load_vix_index(paths.vix_index)[["Date", "Close"]].rename(columns={"Close": "VIX Close"})
    return term.merge(vix, left_on="Trade Date", right_on="Date", how="left").drop(columns=["Date"])

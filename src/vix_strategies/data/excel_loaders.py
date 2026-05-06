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
    df["Trade Date"] = pd.to_datetime(df["Trade Date"])

    for col in SETTLE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Complete 9-Maturity Curve" in df.columns:
        df["Complete 9-Maturity Curve"] = df["Complete 9-Maturity Curve"].fillna(False).astype(bool)

    return df.sort_values("Trade Date").reset_index(drop=True)


def load_vix_index(path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.vix_index
    df = pd.read_excel(source, sheet_name="VIX_Index_Daily")
    df["Date"] = pd.to_datetime(df["Date"])
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("Date").reset_index(drop=True)


def load_trading_periods(path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.futures_by_maturity
    df = pd.read_excel(source, sheet_name="Trading Periods")
    for col in ["First Trade Date", "Last Trade Date"]:
        df[col] = pd.to_datetime(df[col])
    return df


def load_maturity_sheet(sheet_name: str, path: Path | None = None) -> pd.DataFrame:
    paths = get_source_paths()
    source = path or paths.futures_by_maturity
    df = pd.read_excel(source, sheet_name=sheet_name)
    df["Trade Date"] = pd.to_datetime(df["Trade Date"])
    for col in ["Open", "High", "Low", "Close", "Settle", "Change", "Total Volume", "EFP", "Open Interest"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("Trade Date").reset_index(drop=True)


def add_term_structure_features(term: pd.DataFrame) -> pd.DataFrame:
    df = term.copy()

    for far in [2, 3, 4, 5, 6, 7, 8, 9]:
        near_col = "M1 Settle"
        far_col = f"M{far} Settle"
        if far_col in df.columns:
            df[f"m1_m{far}_spread"] = df[far_col] - df[near_col]
            df[f"m1_m{far}_pct"] = df[far_col] / df[near_col] - 1

    df["front_state"] = np.select(
        [df["m1_m2_spread"] > 0, df["m1_m2_spread"] < 0],
        ["contango", "backwardation"],
        default="flat",
    )
    return df


def build_analysis_frame() -> pd.DataFrame:
    paths = get_source_paths()
    validate_source_paths(paths)

    term = add_term_structure_features(load_term_structure(paths.term_structure))
    vix = load_vix_index(paths.vix_index)[["Date", "Close"]].rename(columns={"Close": "VIX Close"})
    return term.merge(vix, left_on="Trade Date", right_on="Date", how="left").drop(columns=["Date"])

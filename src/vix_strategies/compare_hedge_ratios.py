from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from .hedged_rolldown import HedgedRollDownConfig, run_hedged_rolldown
from .loaders import load_vix_index


TRADING_DAYS = 252


def _combined_regime(vix: float, slope: float, basis: float) -> str:
    if pd.isna(vix) or pd.isna(slope) or pd.isna(basis):
        return "Missing"
    if vix >= 30 or slope < 0:
        return "Crisis / No Carry"
    if vix < 15 and slope >= 0.08 and basis < 0.10:
        return "Strong Carry"
    if vix < 20 and slope >= 0.08 and basis >= 0.10:
        return "High Basis Carry"
    if vix < 20 and slope >= 0.03 and basis < 0.10:
        return "Normal Carry"
    if vix < 20 and slope >= 0.03 and basis >= 0.10:
        return "Low-quality Carry"
    return "Transition"


def _bucket_basis(basis: float) -> str:
    if pd.isna(basis):
        return "Missing"
    if basis < 0:
        return "<0%"
    if basis < 0.05:
        return "0-5%"
    if basis < 0.10:
        return "5-10%"
    return ">=10%"


def _summarize(grouped: pd.core.groupby.DataFrameGroupBy) -> pd.DataFrame:
    rows = []
    for name, group in grouped:
        held = group[group["both_held"]]
        if held.empty:
            continue
        sd65 = held["ret_065"].std()
        sd80 = held["ret_080"].std()
        rows.append(
            {
                "group": name,
                "both_held_days": len(held),
                "avg_vix_lag": held["VIX_lag"].mean(),
                "avg_slope_lag": held["front_slope_lag"].mean(),
                "avg_basis_lag": held["front_basis_lag"].mean(),
                "avg_ret_065": held["ret_065"].mean(),
                "avg_ret_080": held["ret_080"].mean(),
                "avg_diff": held["diff"].mean(),
                "sum_ret_065": held["ret_065"].sum(),
                "sum_ret_080": held["ret_080"].sum(),
                "sum_diff": held["diff"].sum(),
                "sharpe_065_simple": (held["ret_065"].mean() * TRADING_DAYS) / (sd65 * math.sqrt(TRADING_DAYS)),
                "sharpe_080_simple": (held["ret_080"].mean() * TRADING_DAYS) / (sd80 * math.sqrt(TRADING_DAYS)),
                "win_065": (held["ret_065"] > 0).mean(),
                "win_080": (held["ret_080"] > 0).mean(),
                "worst_065": held["ret_065"].min(),
                "worst_080": held["ret_080"].min(),
                "best_065": held["ret_065"].max(),
                "best_080": held["ret_080"].max(),
            }
        )
    return pd.DataFrame(rows)


def build_comparison() -> pd.DataFrame:
    res65 = run_hedged_rolldown(HedgedRollDownConfig(hedge_ratio=0.65))
    res80 = run_hedged_rolldown(HedgedRollDownConfig(hedge_ratio=0.80))

    vix = load_vix_index()[["Date", "Close"]].rename(columns={"Close": "VIX"})
    res65 = res65.merge(vix, on="Date", how="left")
    res65["front_slope"] = np.log(res65["VX2"] / res65["VX1"])
    res65["front_basis"] = res65["VX1"] / res65["VIX"] - 1

    merged = res65[["Date", "VX1", "VX2", "VIX", "front_slope", "front_basis", "ret", "raw_ret", "held", "equity", "drawdown"]].rename(
        columns={"ret": "ret_065", "raw_ret": "raw_065", "held": "held_065", "equity": "equity_065", "drawdown": "dd_065"}
    ).merge(
        res80[["Date", "ret", "raw_ret", "held", "equity", "drawdown"]].rename(
            columns={"ret": "ret_080", "raw_ret": "raw_080", "held": "held_080", "equity": "equity_080", "drawdown": "dd_080"}
        ),
        on="Date",
        how="inner",
    )

    merged["diff"] = merged["ret_080"] - merged["ret_065"]
    merged["both_held"] = merged["held_065"].eq(1) & merged["held_080"].eq(1)
    for col in ["VIX", "front_slope", "front_basis"]:
        merged[f"{col}_lag"] = merged[col].shift(1)
    merged["regime_lag"] = [
        _combined_regime(vix, slope, basis)
        for vix, slope, basis in zip(merged["VIX_lag"], merged["front_slope_lag"], merged["front_basis_lag"])
    ]
    merged["basis_bucket_lag"] = merged["front_basis_lag"].map(_bucket_basis)
    return merged


def main() -> None:
    output_dir = Path("reports/generated/hedge_ratio_065_vs_080")
    output_dir.mkdir(parents=True, exist_ok=True)

    comparison = build_comparison()
    comparison.to_csv(output_dir / "daily_compare_065_080.csv", index=False)
    _summarize(comparison.groupby("regime_lag")).to_csv(output_dir / "regime_summary.csv", index=False)
    _summarize(comparison.groupby("basis_bucket_lag")).to_csv(output_dir / "basis_summary.csv", index=False)

    held = comparison[comparison["both_held"]]
    quantiles = pd.DataFrame(
        {
            "quantile": [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99],
            "ret_065": held["ret_065"].quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).to_numpy(),
            "ret_080": held["ret_080"].quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).to_numpy(),
            "diff_080_minus_065": held["diff"].quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).to_numpy(),
        }
    )
    quantiles.to_csv(output_dir / "held_day_quantiles.csv", index=False)


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..backtests.hedged_vx1_vx2_rolldown import HedgedRollDownConfig, performance_stats, run_hedged_rolldown
from ..data.excel_loaders import load_term_structure


PROFILE_CONFIGS = [
    HedgedRollDownConfig(hedge_ratio=0.65, entry_slope=0.07, exit_slope=0.05, vx1_cap=25.0, stop_loss=None, stop_clip=False, avoid_roll=True),
    HedgedRollDownConfig(hedge_ratio=0.60, entry_slope=0.08, exit_slope=0.05, vx1_cap=30.0, stop_loss=-0.02, stop_clip=False, avoid_roll=True),
    HedgedRollDownConfig(hedge_ratio=0.45, entry_slope=0.08, exit_slope=0.05, vx1_cap=30.0, stop_loss=-0.02, stop_clip=False, avoid_roll=True),
]
PROFILE_NAMES = ["conservative_065", "balanced_060", "aggressive_045"]
HEDGE_SCAN_RATIOS = [0.45, 0.50, 0.55, 0.60, 0.625, 0.65, 0.675, 0.70, 0.725, 0.75, 0.80]


def _profile_rows() -> pd.DataFrame:
    rows = []
    for name, config in zip(PROFILE_NAMES, PROFILE_CONFIGS):
        result = run_hedged_rolldown(config)
        rows.append({"profile": name, **config.__dict__, **performance_stats(result)})
    return pd.DataFrame(rows)


def _hedge_ratio_scan_rows() -> pd.DataFrame:
    rows = []
    for ratio in HEDGE_SCAN_RATIOS:
        config = HedgedRollDownConfig(hedge_ratio=ratio, entry_slope=0.08, exit_slope=0.05, vx1_cap=30.0, stop_loss=-0.02, stop_clip=False, avoid_roll=True)
        result = run_hedged_rolldown(config)
        rows.append({"ratio": ratio, **performance_stats(result)})
    return pd.DataFrame(rows)


def _term_frame_with_vx3() -> pd.DataFrame:
    term = load_term_structure()
    out = term[["Trade Date", "M1 Settle", "M2 Settle", "M3 Settle", "M1 Month"]].copy()
    out = out.rename(columns={"Trade Date": "Date", "M1 Settle": "VX1", "M2 Settle": "VX2", "M3 Settle": "VX3"})
    out = out.dropna(subset=["Date", "VX1", "VX2", "VX3"]).sort_values("Date").reset_index(drop=True)
    return out


def _shock_beta_rows() -> pd.DataFrame:
    data = _term_frame_with_vx3()[["Date", "VX1", "VX2", "VX3"]].copy()
    data["dVX1"] = data["VX1"].diff()
    data["dVX2"] = data["VX2"].diff()
    data["dVX3"] = data["VX3"].diff()
    data = data.dropna()
    rows = []
    for quantile in [0.95, 0.975, 0.99, 0.995]:
        cutoff = data["dVX1"].quantile(quantile)
        spike = data[data["dVX1"] >= cutoff].copy()
        rows.append({
            "threshold": f"top {(1 - quantile) * 100:.1f}%",
            "dVX1_cutoff": cutoff,
            "count": len(spike),
            "dVX1_mean": spike["dVX1"].mean(),
            "dVX2_mean": spike["dVX2"].mean(),
            "dVX3_mean": spike["dVX3"].mean(),
            "dVX1_median": spike["dVX1"].median(),
            "dVX2_median": spike["dVX2"].median(),
            "dVX3_median": spike["dVX3"].median(),
            "beta2_median": (spike["dVX2"] / spike["dVX1"]).median(),
            "beta3_median": (spike["dVX3"] / spike["dVX1"]).median(),
        })
    return pd.DataFrame(rows)


def _front_slope_stationarity_rows() -> pd.DataFrame:
    data = _term_frame_with_vx3()[["Date", "VX1", "VX2"]].copy()
    data["front_slope"] = np.log(data["VX2"] / data["VX1"])
    periods = [
        ("full_sample", data["Date"].min(), data["Date"].max()),
        ("pre_gfc", pd.Timestamp("2004-03-26"), pd.Timestamp("2007-12-31")),
        ("gfc_to_pre_covid", pd.Timestamp("2008-01-01"), pd.Timestamp("2019-12-31")),
        ("covid_after", pd.Timestamp("2020-01-01"), data["Date"].max()),
    ]
    rows = []
    for name, start, end in periods:
        sub = data[(data["Date"] >= start) & (data["Date"] <= end)].copy()
        slope = sub["front_slope"].dropna()
        ar1 = slope.autocorr(lag=1)
        half_life = np.log(0.5) / np.log(ar1) if ar1 and 0 < ar1 < 1 else np.nan
        rows.append({"period": name, "start": sub["Date"].min(), "end": sub["Date"].max(), "nobs": len(slope), "mean": slope.mean(), "std": slope.std(), "ar1_phi": ar1, "half_life_days": half_life})
    return pd.DataFrame(rows)


def main() -> None:
    output_dir = Path("reports/generated/reproduce_peer_research")
    output_dir.mkdir(parents=True, exist_ok=True)
    profiles = _profile_rows()
    hedge_scan = _hedge_ratio_scan_rows()
    shock_beta = _shock_beta_rows()
    stationarity = _front_slope_stationarity_rows()
    profiles.to_csv(output_dir / "peer_profiles.csv", index=False)
    hedge_scan.to_csv(output_dir / "peer_hedge_ratio_scan.csv", index=False)
    shock_beta.to_csv(output_dir / "peer_shock_beta.csv", index=False)
    stationarity.to_csv(output_dir / "peer_front_slope_stationarity.csv", index=False)
    print("Profiles")
    print(profiles[["profile", "hedge_ratio", "entry_slope", "exit_slope", "vx1_cap", "cagr", "annual_vol", "sharpe", "mdd", "exposure", "stops"]].to_string(index=False))
    print("\nHedge ratio scan")
    print(hedge_scan[["ratio", "cagr", "annual_vol", "sharpe", "mdd", "worst_day", "stops"]].to_string(index=False))
    print("\nShock beta")
    print(shock_beta.to_string(index=False))


if __name__ == "__main__":
    main()

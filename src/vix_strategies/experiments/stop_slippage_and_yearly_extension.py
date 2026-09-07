"""Stop-slippage sensitivity + yearly attribution at high-r anchors.

Closes two PDF backlog items:

- §2.7 / §4.5 (PDF): "stop slippage -2.25%, -2.50%, -3.00% 민감도는 필수 후속 검증"
- §1.8 / §2.4 implicit: yearly attribution at high-r (only 0.65-vs-0.80 done before)

Outputs go to two separate folders so they don't co-mingle with the earlier
``compare_065_vs_080_hedge_ratios`` and ``high_r_hedge_ratio_extension`` runs:

- ``reports/generated/stop_slippage_sensitivity/``
- ``reports/generated/yearly_attribution_high_r/``
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..backtests.hedged_vx1_vx2_rolldown import (
    HedgedRollDownConfig,
    performance_stats,
    run_hedged_rolldown,
)
from ..charts import make_line_chart, make_bar_chart, FIXERS_COLORS


OUT_SLIP = Path("reports/generated/stop_slippage_sensitivity")
OUT_YEAR = Path("reports/generated/yearly_attribution_high_r")

RATIOS_FULL = [round(0.45 + 0.05 * i, 2) for i in range(20)]
RATIOS_DEEP = [0.65, 0.80, 1.00, 1.20, 1.40]
SLIPPAGES = [0.0, 0.0025, 0.005, 0.01]


def _stamp(t0: float, msg: str) -> None:
    elapsed = time.perf_counter() - t0
    print(f"[+{elapsed:6.1f}s] {msg}", flush=True)


def _config(r: float, stop_clip: bool, slip: float) -> HedgedRollDownConfig:
    return HedgedRollDownConfig(
        hedge_ratio=r,
        entry_slope=0.08,
        exit_slope=0.05,
        vx1_cap=30.0,
        stop_loss=-0.02,
        stop_clip=stop_clip,
        stop_slippage=slip,
        avoid_roll=True,
    )


def run_slippage_sweep(t0: float) -> pd.DataFrame:
    OUT_SLIP.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_SLIP / "slippage_sweep.csv"

    rows: list[dict] = []
    for r in RATIOS_FULL:
        for slip in SLIPPAGES:
            stats = performance_stats(run_hedged_rolldown(_config(r, stop_clip=True, slip=slip)))
            rows.append({"ratio": r, "stop_slippage": slip, **stats})
        pd.DataFrame(rows).to_csv(csv_path, index=False)
        _stamp(t0, f"  slippage sweep r={r:.2f} done ({len(rows)}/{len(RATIOS_FULL) * len(SLIPPAGES)})")
    return pd.DataFrame(rows)


def slippage_summary(sweep: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for r in RATIOS_DEEP:
        sub = sweep[sweep["ratio"].eq(r)].set_index("stop_slippage").sort_index()
        row = {"ratio": r}
        for slip in SLIPPAGES:
            row[f"sharpe_slip{int(slip * 1e4)}bp"] = sub.loc[slip, "sharpe"]
            row[f"cagr_slip{int(slip * 1e4)}bp"] = sub.loc[slip, "cagr"]
            row[f"mdd_slip{int(slip * 1e4)}bp"] = sub.loc[slip, "mdd"]
        s0 = sub.loc[0.0, "sharpe"]
        row["sharpe_decay_50bp"] = sub.loc[0.005, "sharpe"] - s0
        row["sharpe_decay_100bp"] = sub.loc[0.01, "sharpe"] - s0
        c0 = sub.loc[0.0, "cagr"]
        row["cagr_decay_50bp"] = sub.loc[0.005, "cagr"] - c0
        row["cagr_decay_100bp"] = sub.loc[0.01, "cagr"] - c0
        rows.append(row)
    return pd.DataFrame(rows)


def run_yearly_attribution(t0: float) -> tuple[pd.DataFrame, pd.DataFrame, dict[float, pd.DataFrame]]:
    OUT_YEAR.mkdir(parents=True, exist_ok=True)
    yearly_csv = OUT_YEAR / "yearly_returns.csv"
    diff_csv = OUT_YEAR / "yearly_diff_vs_065.csv"

    daily_per_ratio: dict[float, pd.DataFrame] = {}
    for r in RATIOS_DEEP:
        result = run_hedged_rolldown(_config(r, stop_clip=False, slip=0.0))
        daily_per_ratio[r] = result[["Date", "ret", "held", "equity"]].copy()
        _stamp(t0, f"  yearly daily series r={r:.2f} ({len(result):,} rows)")

    base = daily_per_ratio[0.65][["Date"]].copy()
    base["year"] = pd.to_datetime(base["Date"]).dt.year
    yearly = pd.DataFrame({"year": sorted(base["year"].unique())})

    sum_ret_by_year: dict[float, pd.Series] = {}
    for r in RATIOS_DEEP:
        df = daily_per_ratio[r].copy()
        df["year"] = pd.to_datetime(df["Date"]).dt.year
        sum_ret_by_year[r] = df.groupby("year")["ret"].sum()
        yearly[f"r={r:.2f}"] = yearly["year"].map(sum_ret_by_year[r])

    yearly.to_csv(yearly_csv, index=False)
    _stamp(t0, f"  yearly_returns.csv written ({len(yearly)} years)")

    diff = pd.DataFrame({"year": yearly["year"]})
    for r in [r for r in RATIOS_DEEP if r != 0.65]:
        diff[f"diff_{r:.2f}_vs_0.65"] = yearly[f"r={r:.2f}"] - yearly["r=0.65"]
    diff.to_csv(diff_csv, index=False)
    _stamp(t0, "  yearly_diff_vs_065.csv written")

    return yearly, diff, daily_per_ratio


def _render_slippage_charts(sweep: pd.DataFrame, t0: float) -> None:
    pivot_sharpe = sweep.pivot(index="ratio", columns="stop_slippage", values="sharpe").reset_index()
    cols_label = [f"slip {int(s * 1e4)}bp" for s in SLIPPAGES]
    rename = {s: lab for s, lab in zip(SLIPPAGES, cols_label)}
    pivot_sharpe = pivot_sharpe.rename(columns=rename)
    make_line_chart(
        pivot_sharpe, x_col="ratio", y_cols=cols_label,
        title="헤지 비율별 Sharpe — Stop Slippage 민감도",
        subtitle="entry 8% / exit 5% / stop -2% (intraday clip with slippage)",
        x_label="헤지 비율 r",
        legend_labels=cols_label,
        accent_index=cols_label.index("slip 100bp"),
        save_path=OUT_SLIP / "fixers_sharpe_by_slippage.png",
    )
    _stamp(t0, "  fixers_sharpe_by_slippage.png written")

    pivot_cagr = sweep.pivot(index="ratio", columns="stop_slippage", values="cagr").reset_index()
    pivot_cagr = pivot_cagr.rename(columns=rename)
    make_line_chart(
        pivot_cagr, x_col="ratio", y_cols=cols_label,
        title="헤지 비율별 CAGR — Stop Slippage 민감도",
        subtitle="entry 8% / exit 5% / stop -2% (intraday clip with slippage)",
        x_label="헤지 비율 r",
        y_unit="%",
        legend_labels=cols_label,
        accent_index=cols_label.index("slip 100bp"),
        save_path=OUT_SLIP / "fixers_cagr_by_slippage.png",
    )
    _stamp(t0, "  fixers_cagr_by_slippage.png written")


def _render_yearly_charts(yearly: pd.DataFrame, daily_per_ratio: dict[float, pd.DataFrame], t0: float) -> None:
    chart_df = pd.DataFrame({
        "year": yearly["year"],
        "r=0.65": yearly["r=0.65"],
        "r=1.40": yearly["r=1.40"],
    })
    make_line_chart(
        chart_df, x_col="year", y_cols=["r=0.65", "r=1.40"],
        title="연도별 누적 수익률 — r=0.65 vs r=1.40",
        subtitle="entry 8% / exit 5% / stop -2% (close-only)",
        x_label="연도",
        y_unit="%",
        legend_labels=["r=0.65 (anchor)", "r=1.40 (front-vol-tilted)"],
        accent_index=1,
        save_path=OUT_YEAR / "fixers_yearly_065_vs_140.png",
    )
    _stamp(t0, "  fixers_yearly_065_vs_140.png written")

    base_dates = daily_per_ratio[0.65][["Date"]].copy()
    overlay = base_dates.copy()
    for r in RATIOS_DEEP:
        overlay[f"r={r:.2f}"] = daily_per_ratio[r]["equity"].to_numpy() - 1.0
    make_line_chart(
        overlay, x_col="Date", y_cols=[f"r={r:.2f}" for r in RATIOS_DEEP],
        title="헤지 비율별 누적 수익률 — high-r 확장",
        subtitle="2004 ~ 2026, entry 8% / exit 5% / stop -2% (close-only)",
        y_unit="%",
        x_kind="datetime", date_format="yyyy",
        legend_labels=[f"r={r:.2f}" for r in RATIOS_DEEP],
        accent_index=4,
        figsize=(9.5, 4.8),
        save_path=OUT_YEAR / "fixers_equity_curves_5_ratios.png",
    )
    _stamp(t0, "  fixers_equity_curves_5_ratios.png written")


def main() -> None:
    t0 = time.perf_counter()
    _stamp(t0, "phase 1/4: stop slippage sweep (20 ratios × 4 slippage levels)")
    sweep = run_slippage_sweep(t0)

    _stamp(t0, "phase 2/4: slippage summary table")
    summary = slippage_summary(sweep)
    summary.to_csv(OUT_SLIP / "slippage_summary.csv", index=False)
    _stamp(t0, f"  slippage_summary.csv written ({len(summary)} anchors)")

    _stamp(t0, "phase 3/4: yearly attribution at 5 anchor ratios")
    yearly, diff, daily_per_ratio = run_yearly_attribution(t0)

    _stamp(t0, "phase 4/4: rendering FIXERS charts")
    _render_slippage_charts(sweep, t0)
    _render_yearly_charts(yearly, daily_per_ratio, t0)

    total = time.perf_counter() - t0
    print(f"\n[done in {total:.1f}s]")
    print(f"  Stop slippage:  {OUT_SLIP.resolve()}")
    print(f"  Yearly attrib:  {OUT_YEAR.resolve()}")


if __name__ == "__main__":
    main()

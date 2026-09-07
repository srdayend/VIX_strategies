"""Render a tight 9-chart summary deck of the current research storyline.

All inputs come from previously-generated CSVs (no new backtests required for
chart 1–4, 6–9). Chart 5 (equity curve overlay) re-runs five backtests to get
the daily equity series — about 5 seconds total.

Outputs land in ``reports/generated/summary_charts/`` so the deck can be
distributed independently of any single experiment folder.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from ..backtests.hedged_vx1_vx2_rolldown import HedgedRollDownConfig, run_hedged_rolldown
from ..charts import make_bar_chart, make_line_chart


OUT = Path("reports/generated/summary_charts")

DIST_DIR = Path("reports/generated/vix_distribution_rolldown_hedge_ratio")
HIGH_R_DIR = Path("reports/generated/high_r_hedge_ratio_extension")
SLIP_DIR = Path("reports/generated/stop_slippage_sensitivity")
YEAR_DIR = Path("reports/generated/yearly_attribution_high_r")


def _stamp(t0: float, msg: str) -> None:
    print(f"[+{time.perf_counter() - t0:5.1f}s] {msg}", flush=True)


def chart_01_vix_distribution() -> None:
    df = pd.read_csv(DIST_DIR / "vix_spot_percentile_curve.csv")
    make_line_chart(
        df, x_col="percentile", y_cols=["historical_vix_close", "latest_3y_vix_close"],
        title="VIX 분포 — Historical vs Latest 3Y",
        subtitle="VIX spot 종가 percentile curve, 1990 ~ 2026",
        x_label="분위 (%)",
        legend_labels=["Historical (1990 ~ 2026)", "Latest 3Y (2023 ~ 2026)"],
        accent_index=1,
        save_path=OUT / "01_vix_distribution.png",
    )


def chart_02_term_contango() -> None:
    df = pd.read_csv(DIST_DIR / "term_structure_contango_backwardation_summary.csv")
    measures = ["M2/M1", "M3/M1", "M4/M1", "M6/M1", "M9/M1"]
    sub = df[df["curve_measure"].isin(measures)].copy()
    make_bar_chart(
        sub, x_col="curve_measure", y_col="contango_rate_pct",
        title="VIX 선물 — Contango 발생 빈도",
        subtitle="2004 ~ 2026, 종가 기준 M(n) > M1 인 일자 비중",
        y_unit="%",
        save_path=OUT / "02_term_contango.png",
    )


def chart_03_spike_shock_beta() -> None:
    df = pd.read_csv(DIST_DIR / "vix_spike_hedge_ratio_summary.csv")
    df["threshold"] = df["threshold"].str.replace(" VIX up days", "")
    make_bar_chart(
        df, x_col="threshold", y_col="vx2_vx1_median",
        title="Spike Day median dVX2/dVX1 — r=0.65 anchor 의 근거",
        subtitle="VIX spot 상위 spike 일별로 측정된 shock-beta",
        save_path=OUT / "03_spike_shock_beta.png",
    )


def chart_04_hedge_ratio_sharpe() -> None:
    sc = pd.read_csv(HIGH_R_DIR / "hedge_ratio_scan_close_only.csv")
    make_line_chart(
        sc, x_col="ratio", y_cols=["sharpe"],
        title="헤지 비율별 Sharpe",
        subtitle="entry 8% / exit 5% / stop -2% (close-only), r ∈ [0.45, 1.40]",
        x_label="헤지 비율 r",
        save_path=OUT / "04_hedge_ratio_sharpe.png",
    )


def chart_05_equity_curve_overlay(t0: float) -> None:
    ratios = [0.65, 0.80, 1.00, 1.20, 1.40]
    recent_start = pd.Timestamp("2016-01-01")
    cfgs = [
        HedgedRollDownConfig(hedge_ratio=r, entry_slope=0.08, exit_slope=0.05, vx1_cap=30.0, stop_loss=-0.02, stop_clip=False, avoid_roll=True)
        for r in ratios
    ]
    series: dict[float, pd.DataFrame] = {}
    for r, cfg in zip(ratios, cfgs):
        full = run_hedged_rolldown(cfg)[["Date", "ret"]]
        series[r] = full[full["Date"] >= recent_start].reset_index(drop=True)
        _stamp(t0, f"  equity series r={r:.2f}")
    base = series[ratios[0]][["Date"]].copy()
    for r in ratios:
        base[f"r={r:.2f}"] = (1.0 + series[r]["ret"].fillna(0.0)).cumprod().to_numpy()
    make_line_chart(
        base, x_col="Date", y_cols=[f"r={r:.2f}" for r in ratios],
        title="헤지 비율별 누적 자본 — 5 anchor 비교",
        subtitle="2016 ~ 2026 재기준, entry 8% / exit 5% / stop -2% (close-only)",
        y_unit="배",
        x_kind="datetime", date_format="yyyy",
        legend_labels=[f"r={r:.2f}" for r in ratios],
        accent_index=4,
        figsize=(9.5, 4.8),
        save_path=OUT / "05_equity_curve_5_ratios.png",
    )


def chart_06_held_day_quantiles() -> None:
    df = pd.read_csv(HIGH_R_DIR / "held_day_quantiles.csv")
    df["quantile_pct"] = df["quantile"] * 100
    cols = [c for c in df.columns if c.startswith("r=")]
    make_line_chart(
        df, x_col="quantile_pct", y_cols=cols,
        title="보유일 일별 수익률 분위 — 비율별",
        subtitle="held days only, close-only stop, entry 8% / exit 5%",
        x_label="분위 (%)",
        y_unit="%",
        legend_labels=cols,
        accent_index=cols.index("r=1.40") if "r=1.40" in cols else None,
        save_path=OUT / "06_held_day_quantiles.png",
    )


def chart_07_yearly_diff() -> None:
    df = pd.read_csv(YEAR_DIR / "yearly_diff_vs_065.csv")
    df["year_label"] = df["year"].apply(lambda y: f"'{int(y) % 100:02d}")
    accent_mask = [val < 0 for val in df["diff_1.40_vs_0.65"]]
    make_bar_chart(
        df, x_col="year_label", y_col="diff_1.40_vs_0.65",
        title="연도별 r=1.40 vs r=0.65 누적수익률 차이",
        subtitle="entry 8% / exit 5% / stop -2% (close-only)",
        y_unit="%",
        accent_mask=accent_mask,
        xaxis_at_zero=True,
        figsize=(10.0, 4.5),
        save_path=OUT / "07_yearly_diff_high_r.png",
    )


def chart_08_stop_slippage() -> None:
    sweep = pd.read_csv(SLIP_DIR / "slippage_sweep.csv")
    pivot = sweep.pivot(index="ratio", columns="stop_slippage", values="sharpe").reset_index()
    slip_levels = sorted(sweep["stop_slippage"].unique())
    cols_label = [f"slip {int(s * 1e4)}bp" for s in slip_levels]
    pivot = pivot.rename(columns={s: lab for s, lab in zip(slip_levels, cols_label)})
    make_line_chart(
        pivot, x_col="ratio", y_cols=cols_label,
        title="헤지 비율별 Sharpe — Stop Slippage 민감도",
        subtitle="entry 8% / exit 5% / stop -2% (intraday clip with slippage)",
        x_label="헤지 비율 r",
        legend_labels=cols_label,
        accent_index=cols_label.index("slip 100bp"),
        save_path=OUT / "08_stop_slippage.png",
    )


def chart_09_basis_attribution() -> None:
    df = pd.read_csv(HIGH_R_DIR / "basis_attribution.csv")
    df = df[df["basis_bucket"].ne("Missing")].copy()
    df["bucket_order"] = df["basis_bucket"].map({"<0%": 0, "0-5%": 1, "5-10%": 2, ">=10%": 3})
    df = df.sort_values("bucket_order")
    accent_mask = [val < 0 for val in df["diff_1.40_vs_0.65"]]
    make_bar_chart(
        df, x_col="basis_bucket", y_col="diff_1.40_vs_0.65",
        title="Front Basis 구간별 — r=1.40 vs r=0.65 일평균 수익 차이",
        subtitle="basis = VX1/VIX - 1, both-held days only, close-only stop",
        y_unit="%",
        accent_mask=accent_mask,
        xaxis_at_zero=True,
        save_path=OUT / "09_basis_attribution.png",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    _stamp(t0, "01 VIX 분포")
    chart_01_vix_distribution()

    _stamp(t0, "02 Term contango")
    chart_02_term_contango()

    _stamp(t0, "03 Spike-day shock beta")
    chart_03_spike_shock_beta()

    _stamp(t0, "04 Hedge ratio Sharpe")
    chart_04_hedge_ratio_sharpe()

    _stamp(t0, "05 Equity curve overlay (5 backtests)")
    chart_05_equity_curve_overlay(t0)

    _stamp(t0, "06 Held-day quantiles")
    chart_06_held_day_quantiles()

    _stamp(t0, "07 Yearly diff (r=1.40 vs 0.65)")
    chart_07_yearly_diff()

    _stamp(t0, "08 Stop slippage sensitivity")
    chart_08_stop_slippage()

    _stamp(t0, "09 Basis bucket attribution")
    chart_09_basis_attribution()

    total = time.perf_counter() - t0
    print(f"\n[done in {total:.1f}s]  9 charts at {OUT.resolve()}")


if __name__ == "__main__":
    main()

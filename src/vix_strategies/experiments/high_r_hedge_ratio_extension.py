"""High-r hedge ratio extension experiments.

Extends the original peer hedge-ratio scan (0.45–0.80) into the front-vol-heavy
zone (0.85–1.40), addressing the open items in PDF section 1.8:

- Full r ∈ [0.45, 1.40] step 0.05, both close-only and stop-clipped stop modes
- Held-day return quantile distribution at selected ratios
- Regime / basis attribution at selected high-r anchors
- Entry × exit grid extension for selected high-r ratios
- Basis filter overlay extension for selected high-r ratios

Outputs land in ``reports/generated/high_r_hedge_ratio_extension/`` so they do
not co-mingle with the original coworker artifacts.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..backtests.hedged_vx1_vx2_rolldown import (
    HedgedRollDownConfig,
    performance_stats,
    run_hedged_rolldown,
)
from ..charts import make_line_chart
from ..data.excel_loaders import load_vix_index
from ..experiments.compare_065_vs_080_hedge_ratios import (
    _bucket_basis,
    _combined_regime,
)
from ..experiments.regime_overlay_grid import (
    RegimeBacktestConfig,
    performance_stats as regime_performance_stats,
    run_regime_backtest,
)


OUTPUT_DIR = Path("reports/generated/high_r_hedge_ratio_extension")
TRADING_DAYS = 252

RATIOS_FULL = [round(0.45 + 0.05 * i, 2) for i in range(20)]
RATIOS_DEEP = [0.65, 0.80, 1.00, 1.20, 1.40]


def _base_config(r: float, stop_clip: bool) -> HedgedRollDownConfig:
    return HedgedRollDownConfig(
        hedge_ratio=r,
        entry_slope=0.08,
        exit_slope=0.05,
        vx1_cap=30.0,
        stop_loss=-0.02,
        stop_clip=stop_clip,
        avoid_roll=True,
    )


def hedge_ratio_scan(stop_clip: bool) -> pd.DataFrame:
    rows = []
    for r in RATIOS_FULL:
        result = run_hedged_rolldown(_base_config(r, stop_clip))
        rows.append({"ratio": r, **performance_stats(result)})
    return pd.DataFrame(rows)


def held_day_quantiles() -> pd.DataFrame:
    levels = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    out = pd.DataFrame({"quantile": levels})
    for r in RATIOS_DEEP:
        result = run_hedged_rolldown(_base_config(r, stop_clip=False))
        held = result.loc[result["held"].eq(1), "ret"]
        out[f"r={r:.2f}"] = held.quantile(levels).to_numpy()
    return out


def _annotate_regime(base: pd.DataFrame) -> pd.DataFrame:
    vix = load_vix_index()[["Date", "Close"]].rename(columns={"Close": "VIX"})
    df = base.merge(vix, on="Date", how="left")
    df["front_slope_log"] = np.log(df["VX2"] / df["VX1"])
    df["front_basis"] = df["VX1"] / df["VIX"] - 1
    for col in ["VIX", "front_slope_log", "front_basis"]:
        df[f"{col}_lag"] = df[col].shift(1)
    df["regime_lag"] = [
        _combined_regime(v, s, b)
        for v, s, b in zip(df["VIX_lag"], df["front_slope_log_lag"], df["front_basis_lag"])
    ]
    df["basis_bucket_lag"] = df["front_basis_lag"].map(_bucket_basis)
    return df


def attribution_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = _annotate_regime(run_hedged_rolldown(_base_config(0.65, stop_clip=False)))
    daily = daily[["Date", "ret", "held", "regime_lag", "basis_bucket_lag"]].rename(
        columns={"ret": "ret_0.65", "held": "held_0.65"}
    )
    for r in [r for r in RATIOS_DEEP if r != 0.65]:
        sub = run_hedged_rolldown(_base_config(r, stop_clip=False))[["Date", "ret", "held"]]
        sub = sub.rename(columns={"ret": f"ret_{r:.2f}", "held": f"held_{r:.2f}"})
        daily = daily.merge(sub, on="Date", how="inner")

    held_cols = ["held_0.65"] + [f"held_{r:.2f}" for r in RATIOS_DEEP if r != 0.65]
    daily["both_held"] = daily[held_cols].eq(1).all(axis=1)
    held = daily[daily["both_held"]].copy()

    def _agg(grouped, by_name: str) -> pd.DataFrame:
        rows = []
        for name, group in grouped:
            row = {by_name: name, "days": len(group), "avg_ret_0.65": group["ret_0.65"].mean()}
            for r in [r for r in RATIOS_DEEP if r != 0.65]:
                col = f"ret_{r:.2f}"
                row[f"avg_ret_{r:.2f}"] = group[col].mean()
                row[f"diff_{r:.2f}_vs_0.65"] = (group[col] - group["ret_0.65"]).mean()
            rows.append(row)
        return pd.DataFrame(rows)

    regime_summary = _agg(held.groupby("regime_lag"), "regime")
    basis_summary = _agg(held.groupby("basis_bucket_lag"), "basis_bucket")
    return regime_summary, basis_summary


ENTRY_SLOPES = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
EXIT_SLOPES = [0.03, 0.04, 0.05, 0.06, 0.07]


def entry_exit_grid_high_r() -> pd.DataFrame:
    rows = []
    for r in RATIOS_DEEP:
        for entry in ENTRY_SLOPES:
            for exit_ in EXIT_SLOPES:
                if exit_ >= entry:
                    continue
                cfg = HedgedRollDownConfig(
                    hedge_ratio=r,
                    entry_slope=entry,
                    exit_slope=exit_,
                    vx1_cap=30.0,
                    stop_loss=-0.02,
                    stop_clip=True,
                    avoid_roll=True,
                )
                result = run_hedged_rolldown(cfg)
                rows.append({"ratio": r, "entry_slope": entry, "exit_slope": exit_, **performance_stats(result)})
    return pd.DataFrame(rows)


OVERLAY_SIGNALS = ["none", "basis_ge_5", "basis_ge_10", "basis_ge_15"]
OVERLAY_ACTIONS = ["none", "no_entry", "exit", "scale_half"]


def basis_overlay_high_r() -> pd.DataFrame:
    rows = []
    for r in RATIOS_DEEP:
        for entry, exit_ in [(0.08, 0.05), (0.08, 0.07)]:
            for signal in OVERLAY_SIGNALS:
                for action in OVERLAY_ACTIONS:
                    if (signal == "none" and action != "none") or (signal != "none" and action == "none"):
                        continue
                    cfg = RegimeBacktestConfig(
                        hedge_ratio=r,
                        entry_slope=entry,
                        exit_slope=exit_,
                        vx1_cap=30.0,
                        stop_loss=-0.02,
                        stop_clip=True,
                        avoid_roll=True,
                        signal=signal,
                        action=action,
                    )
                    result = run_regime_backtest(cfg)
                    stats = regime_performance_stats(result)
                    rows.append({
                        "ratio": r,
                        "entry_slope": entry,
                        "exit_slope": exit_,
                        "signal": signal,
                        "action": action,
                        **stats,
                    })
    return pd.DataFrame(rows)


def _render_charts(scan_close: pd.DataFrame, scan_clip: pd.DataFrame, qtl: pd.DataFrame) -> None:
    sharpe_compare = pd.DataFrame({
        "ratio": scan_close["ratio"],
        "close-only": scan_close["sharpe"],
        "stop-clipped": scan_clip["sharpe"],
    })
    make_line_chart(
        sharpe_compare, x_col="ratio", y_cols=["close-only", "stop-clipped"],
        title="헤지 비율별 Sharpe — stop 모드 비교",
        subtitle="entry 8% / exit 5% / stop -2%, r ∈ [0.45, 1.40]",
        x_label="헤지 비율 r",
        legend_labels=["close-only", "stop-clipped"],
        accent_index=1,
        save_path=OUTPUT_DIR / "fixers_sharpe_by_ratio.png",
    )

    cagr_compare = pd.DataFrame({
        "ratio": scan_close["ratio"],
        "close-only": scan_close["cagr"],
        "stop-clipped": scan_clip["cagr"],
    })
    make_line_chart(
        cagr_compare, x_col="ratio", y_cols=["close-only", "stop-clipped"],
        title="헤지 비율별 CAGR — stop 모드 비교",
        subtitle="entry 8% / exit 5% / stop -2%, r ∈ [0.45, 1.40]",
        x_label="헤지 비율 r",
        y_unit="%",
        legend_labels=["close-only", "stop-clipped"],
        accent_index=1,
        save_path=OUTPUT_DIR / "fixers_cagr_by_ratio.png",
    )

    mdd_compare = pd.DataFrame({
        "ratio": scan_close["ratio"],
        "close-only": scan_close["mdd"],
        "stop-clipped": scan_clip["mdd"],
    })
    make_line_chart(
        mdd_compare, x_col="ratio", y_cols=["close-only", "stop-clipped"],
        title="헤지 비율별 Max Drawdown — stop 모드 비교",
        subtitle="entry 8% / exit 5% / stop -2%, r ∈ [0.45, 1.40]",
        x_label="헤지 비율 r",
        y_unit="%",
        legend_labels=["close-only", "stop-clipped"],
        accent_index=1,
        save_path=OUTPUT_DIR / "fixers_mdd_by_ratio.png",
    )

    qtl_long = qtl.copy()
    qtl_long["quantile_pct"] = qtl_long["quantile"] * 100
    cols = [c for c in qtl.columns if c.startswith("r=")]
    make_line_chart(
        qtl_long, x_col="quantile_pct", y_cols=cols,
        title="보유일 일별 수익률 분위 — 비율별",
        subtitle="held days only, close-only stop, entry 8% / exit 5%",
        x_label="분위 (%)",
        y_unit="%",
        legend_labels=cols,
        accent_index=cols.index("r=1.40") if "r=1.40" in cols else None,
        save_path=OUTPUT_DIR / "fixers_held_day_quantiles.png",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/5] full hedge ratio scan (close-only + stop-clipped) …")
    scan_close = hedge_ratio_scan(stop_clip=False)
    scan_clip = hedge_ratio_scan(stop_clip=True)
    scan_close.to_csv(OUTPUT_DIR / "hedge_ratio_scan_close_only.csv", index=False)
    scan_clip.to_csv(OUTPUT_DIR / "hedge_ratio_scan_stop_clipped.csv", index=False)

    print("[2/5] held-day quantile distribution …")
    qtl = held_day_quantiles()
    qtl.to_csv(OUTPUT_DIR / "held_day_quantiles.csv", index=False)

    print("[3/5] regime / basis attribution …")
    regime_summary, basis_summary = attribution_tables()
    regime_summary.to_csv(OUTPUT_DIR / "regime_attribution.csv", index=False)
    basis_summary.to_csv(OUTPUT_DIR / "basis_attribution.csv", index=False)

    print("[4/5] entry × exit grid (stop-clipped, selected anchors) …")
    grid = entry_exit_grid_high_r()
    grid.to_csv(OUTPUT_DIR / "entry_exit_grid_anchors.csv", index=False)
    top10 = grid.sort_values("sharpe", ascending=False).head(10)
    top10.to_csv(OUTPUT_DIR / "entry_exit_grid_top10_by_sharpe.csv", index=False)

    print("[5/5] basis overlay grid (selected anchors) …")
    overlay = basis_overlay_high_r()
    overlay.to_csv(OUTPUT_DIR / "basis_overlay_anchors.csv", index=False)

    print("rendering FIXERS charts …")
    _render_charts(scan_close, scan_clip, qtl)

    print(f"\nDone. Outputs in {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()

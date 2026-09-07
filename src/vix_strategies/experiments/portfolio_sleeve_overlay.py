"""60/40 SPY-IEF + VIX sleeve portfolio overlay.

Reproduces the peer's portfolio sleeve table (PDF §3.2) and renders the four
portfolios' equity curves as one log-scale overlay chart, in the same visual
style as ``summary_charts/05_equity_curve_5_ratios.png``.

Data sources:

- SPY / IEF: ``VIX_Index and futures/{SPY,IEF}_daily.csv`` (yfinance Adj Close)
- VIX strategy: rank-based hedged calendar spread (r=0.65), engine in
  ``backtests.hedged_vx1_vx2_rolldown``

Outputs to ``reports/generated/portfolio_sleeve_overlay/``.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..backtests.hedged_vx1_vx2_rolldown import HedgedRollDownConfig, run_hedged_rolldown
from ..charts import make_line_chart
from ..data.source_paths import DATA_DIR
from ..experiments.regime_overlay_grid import RegimeBacktestConfig, run_regime_backtest


OUT = Path("reports/generated/portfolio_sleeve_overlay")
TRADING_DAYS = 252
RECENT_START = pd.Timestamp("2016-01-01")
RATIOS = [0.65, 0.80, 1.00, 1.20, 1.40]
OVERLAY_SIGNAL = "basis_ge_5"
OVERLAY_ACTION = "scale_half"


def _stamp(t0: float, msg: str) -> None:
    print(f"[+{time.perf_counter() - t0:5.1f}s] {msg}", flush=True)


def _load_etf_returns(symbol: str) -> pd.DataFrame:
    path = DATA_DIR / f"{symbol}_daily.csv"
    df = pd.read_csv(path, skiprows=[1, 2])
    df = df.rename(columns={df.columns[0]: "Date"})
    df["Date"] = pd.to_datetime(df["Date"])
    px = pd.to_numeric(df["Adj Close"], errors="coerce")
    rets = px.pct_change()
    return pd.DataFrame({"Date": df["Date"], f"ret_{symbol}": rets})


def _portfolio_stats(daily_ret: pd.Series, name: str) -> dict:
    eq = (1.0 + daily_ret.fillna(0.0)).cumprod()
    years = (daily_ret.index.max() - daily_ret.index.min()).days / 365.25
    annual_vol = float(daily_ret.std() * np.sqrt(TRADING_DAYS))
    cagr = float(eq.iloc[-1] ** (1.0 / years) - 1.0)
    sharpe = (float(daily_ret.mean()) * TRADING_DAYS) / annual_vol if annual_vol > 0 else float("nan")
    peak = eq.cummax()
    mdd = float((eq / peak - 1.0).min())
    return {
        "portfolio": name,
        "cagr": cagr,
        "annual_vol": annual_vol,
        "sharpe": sharpe,
        "mdd": mdd,
        "worst_day": float(daily_ret.min()),
    }


def _build_panel_for_ratio(etf: pd.DataFrame, r: float) -> pd.DataFrame:
    fixed_cfg = HedgedRollDownConfig(hedge_ratio=r, entry_slope=0.08, exit_slope=0.05, vx1_cap=30.0, stop_loss=-0.02, stop_clip=False, avoid_roll=True)
    fixed_res = run_hedged_rolldown(fixed_cfg)[["Date", "ret"]].rename(columns={"ret": "ret_VIX_fixed"})
    overlay_cfg = RegimeBacktestConfig(
        hedge_ratio=r, entry_slope=0.08, exit_slope=0.05, vx1_cap=30.0,
        stop_loss=-0.02, stop_clip=False, avoid_roll=True,
        signal=OVERLAY_SIGNAL, action=OVERLAY_ACTION,
    )
    overlay_res = run_regime_backtest(overlay_cfg)[["Date", "ret"]].rename(columns={"ret": "ret_VIX_overlay"})
    panel = (
        etf.merge(fixed_res, on="Date", how="inner")
        .merge(overlay_res, on="Date", how="inner")
        .set_index("Date").sort_index()
    )
    panel = panel[panel.index >= RECENT_START]
    panel["p_6040"] = 0.60 * panel["ret_SPY"] + 0.40 * panel["ret_IEF"]
    panel["p_20_fixed"] = 0.80 * panel["p_6040"] + 0.20 * panel["ret_VIX_fixed"]
    panel["p_30_fixed"] = 0.70 * panel["p_6040"] + 0.30 * panel["ret_VIX_fixed"]
    panel["p_30_overlay"] = 0.70 * panel["p_6040"] + 0.30 * panel["ret_VIX_overlay"]
    return panel


def _render_for_ratio(panel: pd.DataFrame, r: float) -> dict:
    portfolios = {
        "60/40 SPY-IEF": panel["p_6040"],
        f"+20% fixed r={r:.2f} sleeve": panel["p_20_fixed"],
        f"+30% fixed r={r:.2f} sleeve": panel["p_30_fixed"],
        f"+30% overlay r={r:.2f} sleeve": panel["p_30_overlay"],
    }
    stats_rows = [_portfolio_stats(s, name) for name, s in portfolios.items()]
    for row in stats_rows:
        row["ratio"] = r

    eq_df = pd.DataFrame({"Date": panel.index})
    eq_df["60/40 SPY-IEF"] = (1.0 + panel["p_6040"].fillna(0.0)).cumprod().to_numpy()
    eq_df["+20% fixed"] = (1.0 + panel["p_20_fixed"].fillna(0.0)).cumprod().to_numpy()
    eq_df["+30% fixed"] = (1.0 + panel["p_30_fixed"].fillna(0.0)).cumprod().to_numpy()
    eq_df["+30% overlay"] = (1.0 + panel["p_30_overlay"].fillna(0.0)).cumprod().to_numpy()

    tag = f"r{int(round(r * 100)):03d}"
    eq_df.to_csv(OUT / f"portfolio_equity_curves_{tag}.csv", index=False)

    make_line_chart(
        eq_df, x_col="Date",
        y_cols=["60/40 SPY-IEF", "+20% fixed", "+30% fixed", "+30% overlay"],
        title=f"포트폴리오 누적 자본 — 60/40 SPY-IEF + VIX sleeve (r={r:.2f})",
        subtitle=(
            f"VIX sleeve = r={r:.2f} hedged calendar spread (close-only), "
            f"overlay = basis>=5% scale_half, "
            f"{panel.index.min().year} ~ {panel.index.max().year} 재기준"
        ),
        y_unit="배",
        x_kind="datetime", date_format="yyyy",
        legend_labels=["60/40 SPY-IEF", "+20% fixed sleeve", "+30% fixed sleeve", "+30% overlay sleeve"],
        accent_index=2,
        figsize=(9.5, 4.8),
        save_path=OUT / f"fixers_portfolio_sleeve_{tag}.png",
    )
    return {"ratio": r, "stats": stats_rows}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    _stamp(t0, "phase 1/3: load SPY / IEF daily returns")
    spy = _load_etf_returns("SPY")
    ief = _load_etf_returns("IEF")
    etf = spy.merge(ief, on="Date", how="inner").dropna()
    _stamp(t0, f"  ETF rows = {len(etf):,}")

    _stamp(t0, f"phase 2/3: build + render 4-portfolio overlay for {len(RATIOS)} r anchors")
    all_stats: list[dict] = []
    for r in RATIOS:
        panel = _build_panel_for_ratio(etf, r)
        result = _render_for_ratio(panel, r)
        all_stats.extend(result["stats"])
        _stamp(t0, f"  r={r:.2f} done — chart + csv saved")

    _stamp(t0, "phase 3/3: combined cross-r summary")
    summary = pd.DataFrame(all_stats)[["ratio", "portfolio", "cagr", "annual_vol", "sharpe", "mdd", "worst_day"]]
    summary.to_csv(OUT / "portfolio_sleeve_summary_all_ratios.csv", index=False)
    print(summary.to_string(index=False))

    total = time.perf_counter() - t0
    print(f"\n[done in {total:.1f}s]  {OUT.resolve()}")


if __name__ == "__main__":
    main()

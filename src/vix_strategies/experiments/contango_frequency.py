"""VIX futures contango/backwardation frequency — multiple cuts.

The original ``term_structure_contango_backwardation_summary.csv`` only has
the global average across the full sample. This module re-cuts the same
underlying data five ways:

1. Daily time-series of state (contango / backwardation / flat) for each
   front-to-far pair (M2/M1 ... M9/M1)
2. Yearly breakdown — contango rate by calendar year
3. VIX regime breakdown — contango rate when VIX <15 / 15-20 / 20-30 / 30+
4. Monthly seasonality — contango rate by calendar month
5. Recent windows comparison — last 5Y / 10Y vs full sample
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..charts import make_bar_chart, make_line_chart
from ..data.excel_loaders import build_analysis_frame


OUT = Path("reports/generated/contango_frequency")
PAIRS = [(2, 1), (3, 1), (4, 1), (6, 1), (9, 1)]
PAIR_LABELS = [f"M{far}/M{near}" for far, near in PAIRS]


def _stamp(t0: float, msg: str) -> None:
    print(f"[+{time.perf_counter() - t0:5.1f}s] {msg}", flush=True)


def _vix_bucket(v: float) -> str:
    if pd.isna(v):
        return "Missing"
    if v < 15:
        return "<15"
    if v < 20:
        return "15-20"
    if v < 30:
        return "20-30"
    return "30+"


def _state(ratio: float) -> str:
    if pd.isna(ratio):
        return "Missing"
    if ratio > 1.0:
        return "contango"
    if ratio < 1.0:
        return "backwardation"
    return "flat"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    _stamp(t0, "phase 1/5: load merged term-structure + VIX index frame")
    df = build_analysis_frame()
    df = df[["Trade Date", "VIX Close"] + [f"M{i} Settle" for i in range(1, 10) if f"M{i} Settle" in df.columns]].copy()
    df = df.dropna(subset=["Trade Date"]).sort_values("Trade Date").reset_index(drop=True)
    df["year"] = pd.to_datetime(df["Trade Date"]).dt.year
    df["month"] = pd.to_datetime(df["Trade Date"]).dt.month
    df["vix_bucket"] = df["VIX Close"].map(_vix_bucket)
    _stamp(t0, f"  {len(df):,} rows, {df['year'].min()}–{df['year'].max()}")

    daily = df[["Trade Date", "VIX Close", "vix_bucket", "year", "month"]].copy()
    for far, near in PAIRS:
        far_col = f"M{far} Settle"
        near_col = f"M{near} Settle"
        if far_col not in df.columns or near_col not in df.columns:
            continue
        ratio = df[far_col] / df[near_col]
        daily[f"M{far}/M{near}_ratio"] = ratio
        daily[f"M{far}/M{near}_state"] = ratio.map(_state)
    daily.to_csv(OUT / "daily_state_timeseries.csv", index=False)
    _stamp(t0, "  daily_state_timeseries.csv written")

    yearly_rows: list[dict] = []
    for year, group in daily.groupby("year"):
        row = {"year": int(year), "days": len(group)}
        for far, near in PAIRS:
            col = f"M{far}/M{near}_state"
            if col not in group.columns:
                continue
            valid = group[col].ne("Missing")
            row[f"M{far}/M{near}_contango_rate"] = (group.loc[valid, col].eq("contango")).mean()
        yearly_rows.append(row)
    yearly = pd.DataFrame(yearly_rows)
    yearly.to_csv(OUT / "yearly_contango_rate.csv", index=False)
    _stamp(t0, f"  yearly_contango_rate.csv written ({len(yearly)} years)")

    vix_rows: list[dict] = []
    for bucket in ["<15", "15-20", "20-30", "30+"]:
        sub = daily[daily["vix_bucket"].eq(bucket)]
        row = {"vix_bucket": bucket, "days": len(sub)}
        for far, near in PAIRS:
            col = f"M{far}/M{near}_state"
            if col not in sub.columns:
                continue
            valid = sub[col].ne("Missing")
            row[f"M{far}/M{near}_contango_rate"] = (sub.loc[valid, col].eq("contango")).mean()
        vix_rows.append(row)
    by_vix = pd.DataFrame(vix_rows)
    by_vix.to_csv(OUT / "contango_rate_by_vix_regime.csv", index=False)
    _stamp(t0, "  contango_rate_by_vix_regime.csv written")

    monthly_rows: list[dict] = []
    for month in range(1, 13):
        sub = daily[daily["month"].eq(month)]
        row = {"month": month, "days": len(sub)}
        for far, near in PAIRS:
            col = f"M{far}/M{near}_state"
            if col not in sub.columns:
                continue
            valid = sub[col].ne("Missing")
            row[f"M{far}/M{near}_contango_rate"] = (sub.loc[valid, col].eq("contango")).mean()
        monthly_rows.append(row)
    monthly = pd.DataFrame(monthly_rows)
    monthly.to_csv(OUT / "monthly_seasonality.csv", index=False)
    _stamp(t0, "  monthly_seasonality.csv written")

    _stamp(t0, "phase 5/5: recent windows + charts")
    last_date = pd.to_datetime(daily["Trade Date"].max())
    windows = {
        "Full": daily,
        "Latest 10Y": daily[pd.to_datetime(daily["Trade Date"]) >= last_date - pd.DateOffset(years=10)],
        "Latest 5Y": daily[pd.to_datetime(daily["Trade Date"]) >= last_date - pd.DateOffset(years=5)],
    }
    window_rows: list[dict] = []
    for name, sub in windows.items():
        row = {"window": name, "days": len(sub)}
        for far, near in PAIRS:
            col = f"M{far}/M{near}_state"
            if col not in sub.columns:
                continue
            valid = sub[col].ne("Missing")
            row[f"M{far}/M{near}_contango_rate"] = (sub.loc[valid, col].eq("contango")).mean()
        window_rows.append(row)
    by_window = pd.DataFrame(window_rows)
    by_window.to_csv(OUT / "contango_rate_by_window.csv", index=False)
    _stamp(t0, "  contango_rate_by_window.csv written")

    yearly_plot = yearly[yearly["days"] >= 200][["year", "M2/M1_contango_rate"]].copy()
    make_line_chart(
        yearly_plot, x_col="year", y_cols=["M2/M1_contango_rate"],
        title="연도별 M2/M1 Contango 빈도",
        subtitle="VIX 선물 종가 기준, M2 > M1 인 일자 비중",
        x_label="연도",
        y_unit="%",
        y_min=0.0,
        save_path=OUT / "fixers_yearly_contango_rate.png",
    )

    by_vix_chart = by_vix[["vix_bucket", "M2/M1_contango_rate"]].copy()
    make_bar_chart(
        by_vix_chart, x_col="vix_bucket", y_col="M2/M1_contango_rate",
        title="VIX 레짐별 M2/M1 Contango 빈도",
        subtitle="VIX spot 종가 구간별 / 같은 일자의 M2 > M1 비중",
        y_unit="%",
        value_labels=True,
        save_path=OUT / "fixers_contango_by_vix_regime.png",
    )

    monthly_chart = monthly[["month", "M2/M1_contango_rate"]].copy()
    monthly_chart["month_label"] = monthly_chart["month"].apply(lambda m: f"{m:02d}월")
    make_bar_chart(
        monthly_chart, x_col="month_label", y_col="M2/M1_contango_rate",
        title="월별 M2/M1 Contango 빈도",
        subtitle="달력월 평균, 2004 ~ 2026",
        y_unit="%",
        value_labels=True,
        save_path=OUT / "fixers_contango_monthly_seasonality.png",
    )

    print(f"\n[done in {time.perf_counter() - t0:.1f}s]  {OUT.resolve()}")


if __name__ == "__main__":
    main()

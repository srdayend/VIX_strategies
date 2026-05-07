from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from ..data.excel_loaders import SETTLE_COLUMNS, build_analysis_frame, load_vix_index


OUTPUT_DIR = Path("reports/generated/vix_distribution_rolldown_hedge_ratio")
FONT_PATH = Path("C:/Windows/Fonts/NanumSquareR.ttf")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size=size)
    return ImageFont.load_default()


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def _save_simple_line(data: pd.DataFrame, path: Path, title: str, x_col: str, y_cols: list[str], y_label: str) -> None:
    width, height = 1400, 820
    ml, mr, mt, mb = 130, 70, 90, 120
    pw, ph = width - ml - mr, height - mt - mb
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font, label_font, tick_font = _font(32), _font(22), _font(18)
    colors = [(32, 105, 160), (205, 96, 52), (65, 135, 92), (132, 90, 160)]
    x = data[x_col].astype(float).to_numpy()
    vals = data[y_cols].astype(float).to_numpy()
    xmin, xmax = float(np.nanmin(x)), float(np.nanmax(x))
    ymin, ymax = float(np.nanmin(vals)), float(np.nanmax(vals))
    if ymin > 0:
        ymin = 0.0
    pad = (ymax - ymin) * 0.12 or 1.0
    ymin, ymax = ymin - pad if ymin < 0 else ymin, ymax + pad

    def xp(v: float) -> float:
        return ml + (v - xmin) / (xmax - xmin) * pw if xmax != xmin else ml

    def yp(v: float) -> float:
        return mt + (ymax - v) / (ymax - ymin) * ph if ymax != ymin else mt

    draw.text((ml, 32), title, fill=(30, 35, 42), font=title_font)
    draw.line((ml, mt, ml, mt + ph), fill=(70, 76, 84), width=2)
    draw.line((ml, yp(0), ml + pw, yp(0)), fill=(70, 76, 84), width=2)
    for j, col in enumerate(y_cols):
        pts = [(xp(float(a)), yp(float(b))) for a, b in zip(x, data[col])]
        if len(pts) > 1:
            draw.line(pts, fill=colors[j % len(colors)], width=4)
        for px, py in pts:
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=colors[j % len(colors)])
        draw.text((ml + pw - 260, 40 + j * 28), col, fill=colors[j % len(colors)], font=tick_font)
    for v in np.linspace(xmin, xmax, 6):
        draw.text((xp(v) - 18, mt + ph + 18), f"{v:.2f}" if xmax <= 2 else f"{v:.0f}", fill=(45, 50, 56), font=tick_font)
    for v in np.linspace(ymin, ymax, 5):
        draw.text((30, yp(v) - 10), _pct(v) if abs(ymax) < 2 else f"{v:.2f}", fill=(45, 50, 56), font=tick_font)
    draw.text((ml, height - 62), x_col, fill=(45, 50, 56), font=label_font)
    draw.text((30, mt), y_label, fill=(45, 50, 56), font=label_font)
    image.save(path)


def _save_simple_bar(data: pd.DataFrame, path: Path, title: str, x_col: str, y_col: str, y_label: str) -> None:
    width, height = 1400, 820
    ml, mr, mt, mb = 130, 70, 90, 140
    pw, ph = width - ml - mr, height - mt - mb
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font, label_font, tick_font = _font(32), _font(22), _font(17)
    vals = data[y_col].astype(float).to_numpy()
    ymin, ymax = min(0.0, float(np.nanmin(vals))), max(0.0, float(np.nanmax(vals)))
    pad = (ymax - ymin) * 0.12 or 1.0
    ymin, ymax = ymin - pad if ymin < 0 else ymin, ymax + pad

    def yp(v: float) -> float:
        return mt + (ymax - v) / (ymax - ymin) * ph

    draw.text((ml, 32), title, fill=(30, 35, 42), font=title_font)
    draw.line((ml, mt, ml, mt + ph), fill=(70, 76, 84), width=2)
    draw.line((ml, yp(0), ml + pw, yp(0)), fill=(70, 76, 84), width=2)
    group_w = pw / len(data)
    bar_w = group_w * 0.55
    for i, row in data.reset_index(drop=True).iterrows():
        x0 = ml + i * group_w + (group_w - bar_w) / 2
        x1 = x0 + bar_w
        y0, y1 = yp(max(float(row[y_col]), 0)), yp(min(float(row[y_col]), 0))
        draw.rectangle((x0, y0, x1, y1), fill=(32, 105, 160))
        label = str(row[x_col])
        draw.text((x0, mt + ph + 18), label[:12], fill=(45, 50, 56), font=tick_font)
    for v in np.linspace(ymin, ymax, 5):
        draw.text((30, yp(v) - 10), _pct(v) if abs(ymax) < 2 else f"{v:.2f}", fill=(45, 50, 56), font=tick_font)
    draw.text((ml, height - 62), x_col, fill=(45, 50, 56), font=label_font)
    draw.text((30, mt), y_label, fill=(45, 50, 56), font=label_font)
    image.save(path)


def _vix_distribution(vix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    s = vix.dropna(subset=["Close"]).copy()
    latest_start = s["Date"].max() - pd.DateOffset(years=3)
    rows = []
    for label, sample in [("Historical", s), ("Latest 3Y", s[s["Date"] >= latest_start])]:
        close = sample["Close"]
        rows.append({
            "sample": label,
            "start": sample["Date"].min().date(),
            "end": sample["Date"].max().date(),
            "days": len(sample),
            "mean": close.mean(),
            "median": close.median(),
            "p75": close.quantile(0.75),
            "p95": close.quantile(0.95),
            "lt_15_rate": (close < 15).mean(),
            "15_20_rate": close.between(15, 20, inclusive="left").mean(),
            "20_30_rate": close.between(20, 30, inclusive="left").mean(),
            "gte_30_rate": (close >= 30).mean(),
        })
    stats = pd.DataFrame(rows)
    bucket = pd.DataFrame({
        "bucket": ["<15", "15-20", "20-30", "30+"],
        "historical_rate": [stats.loc[0, "lt_15_rate"], stats.loc[0, "15_20_rate"], stats.loc[0, "20_30_rate"], stats.loc[0, "gte_30_rate"]],
        "latest_3y_rate": [stats.loc[1, "lt_15_rate"], stats.loc[1, "15_20_rate"], stats.loc[1, "20_30_rate"], stats.loc[1, "gte_30_rate"]],
    })
    pct_points = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    pct = pd.DataFrame({"percentile": pct_points, "vix_close": [s["Close"].quantile(p / 100) for p in pct_points]})
    dvix = s["Close"].diff()
    spike = pd.DataFrame([
        {"metric": "VIX close", "days": len(s), "median": s["Close"].median(), "mean": s["Close"].mean(), "p75": s["Close"].quantile(.75), "p90": s["Close"].quantile(.90), "p95": s["Close"].quantile(.95), "p99": s["Close"].quantile(.99), "max": s["Close"].max(), "key_share_1": (s["Close"] < 20).mean(), "key_share_2": (s["Close"] >= 40).mean()},
        {"metric": "Daily VIX change", "days": int(dvix.notna().sum()), "median": dvix.median(), "mean": dvix.mean(), "p75": dvix.quantile(.75), "p90": dvix.quantile(.90), "p95": dvix.quantile(.95), "p99": dvix.quantile(.99), "max": dvix.max(), "key_share_1": (dvix >= 3).mean(), "key_share_2": (dvix >= 5).mean()},
    ])
    return stats, bucket, pct, spike


def _term_structure(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for far in [2, 3, 4, 6, 9]:
        sub = df[["M1 Settle", f"M{far} Settle"]].dropna()
        ratio = sub[f"M{far} Settle"] / sub["M1 Settle"]
        rows.append({"curve_measure": f"M{far}/M1", "days": len(sub), "contango_rate": (ratio > 1).mean(), "backwardation_rate": (ratio < 1).mean(), "mean_pct_slope": (ratio - 1).mean(), "median_pct_slope": (ratio - 1).median(), "mean_log_slope": np.log(ratio).mean(), "median_log_slope": np.log(ratio).median()})
    complete = df[SETTLE_COLUMNS].dropna()
    adj = complete[[f"M{i + 1} Settle" for i in range(1, 9)]].to_numpy() / complete[[f"M{i} Settle" for i in range(1, 9)]].to_numpy()
    rows.append({"curve_measure": "All adjacent M1-M9", "days": len(complete), "contango_rate": (adj > 1).all(axis=1).mean(), "backwardation_rate": (adj < 1).all(axis=1).mean(), "mean_pct_slope": np.nan, "median_pct_slope": np.nan, "mean_log_slope": np.nan, "median_log_slope": np.nan})
    return pd.DataFrame(rows)


def _rolldown(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    m1_vix = df[["M1 Settle", "VIX Close"]].dropna()
    prem = m1_vix["M1 Settle"] / m1_vix["VIX Close"] - 1
    rows.append({"roll_pair": "M1->VIX", "days": len(prem), "mean_premium": prem.mean(), "median_premium": prem.median(), "positive_premium_rate": (prem > 0).mean(), "p25": prem.quantile(.25), "p75": prem.quantile(.75)})
    for near in range(1, 9):
        sub = df[[f"M{near} Settle", f"M{near + 1} Settle"]].dropna()
        prem = sub[f"M{near + 1} Settle"] / sub[f"M{near} Settle"] - 1
        rows.append({"roll_pair": f"M{near + 1}->M{near}", "days": len(prem), "mean_premium": prem.mean(), "median_premium": prem.median(), "positive_premium_rate": (prem > 0).mean(), "p25": prem.quantile(.25), "p75": prem.quantile(.75)})
    roll = pd.DataFrame(rows)
    m1_cost = roll.loc[roll["roll_pair"] == "M1->VIX"].iloc[0]
    m2_gain = roll.loc[roll["roll_pair"] == "M2->M1"].iloc[0]
    ratios = [0.45, 0.60, 0.65, 0.70, 0.75, 0.80, 1.00, 1.325, 1.40]
    carry = pd.DataFrame({
        "vx1_ratio_per_short_vx2": ratios,
        "mean_short_vx2_premium": m2_gain["mean_premium"],
        "mean_long_vx1_cost": [r * m1_cost["mean_premium"] for r in ratios],
        "mean_net_premium": [m2_gain["mean_premium"] - r * m1_cost["mean_premium"] for r in ratios],
        "median_short_vx2_premium": m2_gain["median_premium"],
        "median_long_vx1_cost": [r * m1_cost["median_premium"] for r in ratios],
        "median_net_premium": [m2_gain["median_premium"] - r * m1_cost["median_premium"] for r in ratios],
    })
    return roll, carry


def _spike_hedge(df: pd.DataFrame) -> pd.DataFrame:
    x = df[["Trade Date", "VIX Close", "M1 Settle", "M2 Settle"]].dropna().copy()
    x["dVIX"] = x["VIX Close"].diff()
    x["dVX1"] = x["M1 Settle"].diff()
    x["dVX2"] = x["M2 Settle"].diff()
    rows = []
    for q in [.95, .975, .99, .995]:
        cutoff = x["dVIX"].quantile(q)
        sub = x[x["dVIX"] >= cutoff].copy()
        pos = sub[sub["dVX1"] > 0].copy()
        ratio = pos["dVX2"] / pos["dVX1"]
        rows.append({"vix_spike_definition": f"Top {(1 - q) * 100:.1f}% VIX up days", "dvix_cutoff": cutoff, "days": len(sub), "days_with_dvx1_gt_0": len(pos), "median_dvix": sub["dVIX"].median(), "median_dvx1": pos["dVX1"].median(), "median_dvx2": pos["dVX2"].median(), "median_dvx2_over_dvx1": ratio.median()})
    return pd.DataFrame(rows)


def _advanced_pnl_grid(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = df[["Trade Date", "VIX Close", "M1 Settle", "M2 Settle"]].dropna().copy()
    x["dVIX"] = x["VIX Close"].diff()
    x["dVX1"] = x["M1 Settle"].diff()
    x["dVX2"] = x["M2 Settle"].diff()
    x["prev_vix"] = x["VIX Close"].shift(1)
    x["prev_m1"] = x["M1 Settle"].shift(1)
    x["prev_m2"] = x["M2 Settle"].shift(1)
    x["prev_front_slope"] = x["prev_m2"] / x["prev_m1"] - 1
    x = x.dropna().copy()
    top5_cut = x["dVIX"].quantile(.95)
    carry_regime = (x["prev_front_slope"] > 0) & (x["prev_vix"] < 30) & (x["dVIX"] < top5_cut)
    rows = []
    for r in np.round(np.arange(.45, 1.426, .025), 3):
        point_pnl = r * x["dVX1"] - x["dVX2"]
        ret = point_pnl / (r * x["prev_m1"] + x["prev_m2"])
        row = {"r": r, "carry_mean_daily_return": ret[carry_regime].mean(), "carry_median_daily_return": ret[carry_regime].median(), "carry_positive_day_rate": (ret[carry_regime] > 0).mean()}
        for q, label in [(.95, "top5"), (.975, "top2_5"), (.99, "top1")]:
            spike = x["dVIX"] >= x["dVIX"].quantile(q)
            row[f"{label}_spike_median_point_pnl"] = point_pnl[spike].median()
            row[f"{label}_spike_p25_point_pnl"] = point_pnl[spike].quantile(.25)
        rows.append(row)
    grid = pd.DataFrame(rows)
    summary = pd.DataFrame([
        {"criterion": "Top 5% spike-day median PnL >= 0", "implied_r": grid.loc[grid["top5_spike_median_point_pnl"] >= 0, "r"].min()},
        {"criterion": "Top 5% spike-day 25th percentile PnL >= 0", "implied_r": grid.loc[grid["top5_spike_p25_point_pnl"] >= 0, "r"].min()},
        {"criterion": "Top 2.5% spike-day median PnL >= 0", "implied_r": grid.loc[grid["top2_5_spike_median_point_pnl"] >= 0, "r"].min()},
        {"criterion": "Top 1% spike-day median PnL >= 0", "implied_r": grid.loc[grid["top1_spike_median_point_pnl"] >= 0, "r"].min()},
        {"criterion": "Carry-regime mean daily return remains positive", "implied_r": grid.loc[grid["carry_mean_daily_return"] > 0, "r"].max()},
        {"criterion": "Carry-regime median daily return remains positive", "implied_r": grid.loc[grid["carry_median_daily_return"] > 0, "r"].max()},
    ])
    return grid, summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = build_analysis_frame()
    vix = load_vix_index()

    stats, bucket, pct_curve, spike_shape = _vix_distribution(vix)
    term = _term_structure(frame)
    roll, carry = _rolldown(frame)
    hedge = _spike_hedge(frame)
    grid, grid_summary = _advanced_pnl_grid(frame)

    outputs = {
        "vix_spot_distribution_stats.csv": stats,
        "vix_spot_bucket_distribution.csv": bucket,
        "vix_spot_percentile_curve.csv": pct_curve,
        "vix_spike_structure_summary.csv": spike_shape,
        "term_structure_contango_backwardation_summary.csv": term,
        "adjacent_maturity_rolldown_summary.csv": roll,
        "front_carry_by_hedge_ratio.csv": carry,
        "vix_spike_hedge_ratio_summary.csv": hedge,
        "advanced_pnl_weight_grid.csv": grid,
        "advanced_pnl_weight_summary.csv": grid_summary,
    }
    for name, data in outputs.items():
        data.to_csv(OUTPUT_DIR / name, index=False)

    _save_simple_line(pct_curve, OUTPUT_DIR / "vix_spot_percentile_curve.png", "VIX Spot Percentile Curve", "percentile", ["vix_close"], "VIX index points")
    _save_simple_bar(roll, OUTPUT_DIR / "adjacent_maturity_average_rolldown.png", "Average Roll-Down Premium", "roll_pair", "mean_premium", "Premium")
    _save_simple_line(carry, OUTPUT_DIR / "front_carry_by_hedge_ratio_curve.png", "Front Carry By VX1 Ratio", "vx1_ratio_per_short_vx2", ["mean_net_premium", "median_net_premium"], "Net premium")
    _save_simple_bar(term.dropna(subset=["median_pct_slope"]), OUTPUT_DIR / "term_structure_slope_profile.png", "Median Maturity Slope Versus M1", "curve_measure", "median_pct_slope", "Slope")
    _save_simple_bar(term, OUTPUT_DIR / "term_structure_contango_heatmap.png", "Contango Rate By Curve Measure", "curve_measure", "contango_rate", "Contango rate")
    _save_simple_bar(hedge, OUTPUT_DIR / "vix_spike_vx2_vx1_hedge_ratio.png", "Spike-Day dVX2/dVX1 Hedge Ratio", "vix_spike_definition", "median_dvx2_over_dvx1", "Hedge ratio")
    _save_simple_line(grid, OUTPUT_DIR / "advanced_pnl_weight_grid_returns.png", "Carry-Regime Returns By r", "r", ["carry_mean_daily_return", "carry_median_daily_return"], "Daily return")
    _save_simple_line(grid, OUTPUT_DIR / "advanced_spike_pnl_by_weight.png", "Spike-Day Point PnL By r", "r", ["top5_spike_median_point_pnl", "top5_spike_p25_point_pnl"], "Point PnL")

    print(f"Wrote {len(outputs)} CSV files and 8 charts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

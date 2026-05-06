from __future__ import annotations

import json

import pandas as pd

from .loaders import SETTLE_COLUMNS, build_analysis_frame


def summarize_term_structure(df: pd.DataFrame) -> dict:
    summary: dict[str, object] = {
        "rows": int(len(df)),
        "coverage": {
            "start": str(df["Trade Date"].min().date()),
            "end": str(df["Trade Date"].max().date()),
        },
        "complete_9_maturity_rows": int(df.get("Complete 9-Maturity Curve", pd.Series(dtype=bool)).sum()),
        "front_contango_rate": float((df["m1_m2_spread"] > 0).mean()),
        "front_backwardation_rate": float((df["m1_m2_spread"] < 0).mean()),
        "settle_distribution": {},
        "slope_distribution": {},
        "vix_regimes": {},
    }

    for col in [c for c in SETTLE_COLUMNS if c in df.columns]:
        s = df[col].dropna()
        summary["settle_distribution"][col] = {
            "count": int(s.count()),
            "mean": float(s.mean()),
            "p05": float(s.quantile(0.05)),
            "median": float(s.median()),
            "p95": float(s.quantile(0.95)),
        }

    for col in ["m1_m2_pct", "m1_m4_pct", "m1_m7_pct", "m1_m9_pct"]:
        if col in df.columns:
            s = df[col].dropna()
            summary["slope_distribution"][col] = {
                "count": int(s.count()),
                "mean": float(s.mean()),
                "p05": float(s.quantile(0.05)),
                "median": float(s.median()),
                "p95": float(s.quantile(0.95)),
            }

    bucket = pd.cut(
        df["VIX Close"],
        bins=[0, 15, 20, 25, 30, 100],
        labels=["<15", "15-20", "20-25", "25-30", "30+"],
        right=False,
    )
    regime = df.assign(vix_bucket=bucket).groupby("vix_bucket", observed=True).agg(
        days=("Trade Date", "count"),
        contango_rate=("m1_m2_spread", lambda x: float((x > 0).mean())),
        avg_m1_m2_pct=("m1_m2_pct", "mean"),
        avg_m1_m4_pct=("m1_m4_pct", "mean"),
    )
    summary["vix_regimes"] = regime.round(6).to_dict(orient="index")
    return summary


def main() -> None:
    df = build_analysis_frame()
    print(json.dumps(summarize_term_structure(df), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from ..data.excel_loaders import build_analysis_frame


@dataclass(frozen=True)
class SimpleCarryBacktestConfig:
    front: str = "M1 Settle"
    hedge: str = "M2 Settle"
    hedge_ratio: float = 1.0
    signal: str = "m1_m2_pct"
    min_signal: float = 0.03
    max_vix: float | None = 30.0
    exposure_fraction: float = 0.10
    vol_target: float | None = None
    transaction_cost_bps: float = 0.0


def run_simple_m1_m2_carry_backtest(df: pd.DataFrame, config: SimpleCarryBacktestConfig) -> pd.DataFrame:
    data = df[["Trade Date", config.front, config.hedge, config.signal, "VIX Close"]].copy()
    data = data.dropna().sort_values("Trade Date").reset_index(drop=True)
    data = data[(data[config.front] > 0) & (data[config.hedge] > 0)].reset_index(drop=True)

    active = data[config.signal] >= config.min_signal
    if config.max_vix is not None:
        active &= data["VIX Close"] <= config.max_vix

    data["position"] = active.astype(float).shift(1).fillna(0.0) * config.exposure_fraction
    data["front_return"] = data[config.front].pct_change()
    data["hedge_return"] = data[config.hedge].pct_change()

    pair_return = -data["front_return"] + config.hedge_ratio * data["hedge_return"]
    data["gross_return"] = data["position"] * pair_return
    turnover = data["position"].diff().abs().fillna(data["position"].abs())
    data["cost"] = turnover * config.transaction_cost_bps / 10000.0
    data["net_return"] = data["gross_return"] - data["cost"]

    if config.vol_target:
        realized = data["net_return"].rolling(21).std() * np.sqrt(252)
        scale = (config.vol_target / realized).clip(upper=3.0).shift(1).fillna(1.0)
        data["net_return"] = data["net_return"] * scale
        data["vol_scale"] = scale

    data["equity"] = (1 + data["net_return"].fillna(0.0)).cumprod()
    data["drawdown"] = data["equity"] / data["equity"].cummax() - 1
    return data


def summarize_backtest(result: pd.DataFrame) -> dict:
    returns = result["net_return"].dropna()
    if returns.empty:
        return {}
    ann_return = (result["equity"].iloc[-1] ** (252 / len(returns))) - 1
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_return / ann_vol if ann_vol else np.nan
    return {
        "start": str(result["Trade Date"].min().date()),
        "end": str(result["Trade Date"].max().date()),
        "days": int(len(result)),
        "active_rate": float((result["position"] > 0).mean()),
        "ann_return": float(ann_return),
        "ann_vol": float(ann_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(result["drawdown"].min()),
        "ending_equity": float(result["equity"].iloc[-1]),
    }


def main() -> None:
    config = SimpleCarryBacktestConfig()
    df = build_analysis_frame()
    result = run_simple_m1_m2_carry_backtest(df, config)
    output = {"config": asdict(config), "summary": summarize_backtest(result)}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

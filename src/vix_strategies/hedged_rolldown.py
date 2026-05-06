from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .loaders import load_term_structure


TRADING_DAYS = 252


@dataclass(frozen=True)
class HedgedRollDownConfig:
    hedge_ratio: float = 0.80
    entry_slope: float = 0.08
    exit_slope: float = 0.05
    vx1_cap: float = 30.0
    stop_loss: float | None = -0.02
    stop_clip: bool = False
    avoid_roll: bool = True


def prepare_vx1_vx2_frame() -> pd.DataFrame:
    term = load_term_structure()
    df = term[["Trade Date", "M1 Settle", "M2 Settle", "M1 Month", "M2 Month"]].copy()
    df = df.rename(
        columns={
            "Trade Date": "Date",
            "M1 Settle": "VX1",
            "M2 Settle": "VX2",
            "M1 Month": "VX1_Month",
            "M2 Month": "VX2_Month",
        }
    )
    df = df.dropna(subset=["Date", "VX1", "VX2"]).sort_values("Date").reset_index(drop=True)
    df = df[(df["VX1"] > 0) & (df["VX2"] > 0)].reset_index(drop=True)
    return df


def run_hedged_rolldown(config: HedgedRollDownConfig = HedgedRollDownConfig()) -> pd.DataFrame:
    data = prepare_vx1_vx2_frame()
    data["front_slope"] = np.log(data["VX2"] / data["VX1"])
    data["roll_day"] = (
        data["VX1_Month"].ne(data["VX1_Month"].shift(1))
        | data["VX2_Month"].ne(data["VX2_Month"].shift(1))
    ).fillna(False)

    denom = config.hedge_ratio * data["VX1"].shift(1) + data["VX2"].shift(1)
    data["raw_ret"] = (config.hedge_ratio * data["VX1"].diff() - data["VX2"].diff()) / denom
    data["raw_ret"] = data["raw_ret"].fillna(0.0)

    held = np.zeros(len(data), dtype=int)
    stop_hit = np.zeros(len(data), dtype=int)
    position = False

    for i in range(len(data)):
        held[i] = 1 if position else 0

        if position:
            exit_now = False
            if data.loc[i, "front_slope"] < config.exit_slope:
                exit_now = True
            if data.loc[i, "VX1"] > config.vx1_cap:
                exit_now = True
            if config.avoid_roll and data.loc[i, "roll_day"]:
                exit_now = True
            if config.stop_loss is not None and data.loc[i, "raw_ret"] <= config.stop_loss:
                exit_now = True
                stop_hit[i] = 1
            if exit_now:
                position = False

        if not position:
            enter_now = (
                data.loc[i, "front_slope"] > config.entry_slope
                and data.loc[i, "VX1"] < config.vx1_cap
                and (not config.avoid_roll or not data.loc[i, "roll_day"])
            )
            if enter_now:
                position = True

    data["held"] = held
    data["stop_hit"] = stop_hit
    data["unclipped_ret"] = data["raw_ret"] * data["held"]
    if config.stop_clip and config.stop_loss is not None:
        data["ret"] = data["unclipped_ret"].clip(lower=config.stop_loss)
    else:
        data["ret"] = data["unclipped_ret"]
    data["equity"] = (1.0 + data["ret"]).cumprod()
    data["peak"] = data["equity"].cummax()
    data["drawdown"] = data["equity"] / data["peak"] - 1.0
    return data


def performance_stats(result: pd.DataFrame) -> dict[str, Any]:
    ret = result["ret"].fillna(0.0)
    years = (pd.to_datetime(result["Date"].iloc[-1]) - pd.to_datetime(result["Date"].iloc[0])).days / 365.25
    total_return = result["equity"].iloc[-1] - 1.0
    cagr = result["equity"].iloc[-1] ** (1.0 / years) - 1.0
    annual_vol = ret.std() * np.sqrt(TRADING_DAYS)
    sharpe = (ret.mean() * TRADING_DAYS) / annual_vol if annual_vol > 0 else np.nan
    entries = int((result["held"].eq(1) & result["held"].shift(1).fillna(0).eq(0)).sum())
    stops = int(result.get("stop_hit", pd.Series(dtype=int)).sum())
    return {
        "start_date": result["Date"].iloc[0],
        "end_date": result["Date"].iloc[-1],
        "total_return": total_return,
        "cagr": cagr,
        "mdd": result["drawdown"].min(),
        "annual_vol": annual_vol,
        "sharpe": sharpe,
        "exposure": result["held"].mean(),
        "trades": entries,
        "worst_day": ret.min(),
        "best_day": ret.max(),
        "stops": stops,
    }


def main() -> None:
    config = HedgedRollDownConfig(stop_clip=True)
    result = run_hedged_rolldown(config)
    stats = performance_stats(result)
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

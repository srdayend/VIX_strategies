from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.excel_loaders import load_term_structure, load_vix_index


TRADING_DAYS = 252


@dataclass(frozen=True)
class RegimeBacktestConfig:
    hedge_ratio: float
    entry_slope: float = 0.08
    exit_slope: float = 0.05
    vx1_cap: float = 30.0
    stop_loss: float = -0.02
    stop_clip: bool = True
    avoid_roll: bool = True
    signal: str = "none"
    action: str = "none"
    scale: float = 0.5


def _prepare_frame() -> pd.DataFrame:
    term = load_term_structure()
    vix = load_vix_index()[["Date", "Close"]].rename(columns={"Close": "VIX"})
    df = term[["Trade Date", "M1 Settle", "M2 Settle", "M1 Month", "M2 Month"]].rename(
        columns={"Trade Date": "Date", "M1 Settle": "VX1", "M2 Settle": "VX2", "M1 Month": "VX1_Month", "M2 Month": "VX2_Month"}
    )
    df = df.merge(vix, on="Date", how="left")
    df = df.dropna(subset=["Date", "VX1", "VX2"]).sort_values("Date").reset_index(drop=True)
    df = df[(df["VX1"] > 0) & (df["VX2"] > 0)].reset_index(drop=True)
    df["slope"] = np.log(df["VX2"] / df["VX1"])
    df["basis"] = df["VX1"] / df["VIX"] - 1
    df["roll_day"] = (df["VX1_Month"].ne(df["VX1_Month"].shift(1)) | df["VX2_Month"].ne(df["VX2_Month"].shift(1))).fillna(False)
    return df


def _risk_signal(data: pd.DataFrame, signal: str) -> pd.Series:
    vix = data["VIX"]
    slope = data["slope"]
    basis = data["basis"]
    signals = {
        "none": pd.Series(False, index=data.index),
        "vix_ge_25": vix >= 25,
        "vix_ge_30": vix >= 30,
        "slope_lt_0": slope < 0,
        "slope_lt_3": slope < 0.03,
        "basis_ge_5": basis >= 0.05,
        "basis_ge_10": basis >= 0.10,
        "basis_ge_15": basis >= 0.15,
        "vix_ge_25_or_slope_lt_3": (vix >= 25) | (slope < 0.03),
        "vix_ge_30_or_slope_lt_0": (vix >= 30) | (slope < 0),
        "vix_ge_25_or_basis_ge_10": (vix >= 25) | (basis >= 0.10),
        "basis_ge_10_or_slope_lt_3": (basis >= 0.10) | (slope < 0.03),
        "vix_ge_25_or_slope_lt_3_or_basis_ge_10": (vix >= 25) | (slope < 0.03) | (basis >= 0.10),
        "carry_quality_bad": (vix >= 20) | (slope < 0.08) | (basis >= 0.10),
        "strong_only_bad": ~((vix < 15) & (slope >= 0.08) & (basis < 0.10)),
    }
    if signal not in signals:
        raise ValueError(f"Unknown signal: {signal}")
    return signals[signal]


def run_regime_backtest(config: RegimeBacktestConfig) -> pd.DataFrame:
    data = _prepare_frame()
    risk = _risk_signal(data, config.signal).fillna(False)
    denom = config.hedge_ratio * data["VX1"].shift(1) + data["VX2"].shift(1)
    data["raw_ret"] = ((config.hedge_ratio * data["VX1"].diff() - data["VX2"].diff()) / denom).fillna(0.0)

    held = np.zeros(len(data), dtype=int)
    weight = np.zeros(len(data), dtype=float)
    stop_hit = np.zeros(len(data), dtype=int)
    risk_exit = np.zeros(len(data), dtype=int)
    blocked_entry = np.zeros(len(data), dtype=int)
    scaled_day = np.zeros(len(data), dtype=int)
    position = False

    for i in range(len(data)):
        if position:
            held[i] = 1
            prev_risk = bool(risk.iloc[i - 1]) if i > 0 else False
            weight[i] = config.scale if config.action == "scale_half" and prev_risk else 1.0
            scaled_day[i] = int(config.action == "scale_half" and prev_risk)

        if position:
            exit_now = data.loc[i, "slope"] < config.exit_slope or data.loc[i, "VX1"] > config.vx1_cap or (config.avoid_roll and data.loc[i, "roll_day"])
            if config.stop_loss is not None and data.loc[i, "raw_ret"] <= config.stop_loss:
                exit_now = True
                stop_hit[i] = 1
            if config.action == "exit" and bool(risk.iloc[i]):
                exit_now = True
                risk_exit[i] = 1
            if exit_now:
                position = False

        if not position:
            enter_now = data.loc[i, "slope"] > config.entry_slope and data.loc[i, "VX1"] < config.vx1_cap and (not config.avoid_roll or not data.loc[i, "roll_day"])
            if config.action in {"no_entry", "exit", "scale_half"} and bool(risk.iloc[i]):
                blocked_entry[i] = int(enter_now)
                enter_now = False
            if enter_now:
                position = True

    data["held"] = held
    data["weight"] = weight
    data["stop_hit"] = stop_hit
    data["risk_exit"] = risk_exit
    data["blocked_entry"] = blocked_entry
    data["scaled_day"] = scaled_day
    data["risk_signal"] = risk.astype(int)
    data["unclipped_ret"] = data["raw_ret"] * data["weight"]
    data["ret"] = data["unclipped_ret"].clip(lower=config.stop_loss) if config.stop_clip else data["unclipped_ret"]
    data["equity"] = (1.0 + data["ret"].fillna(0.0)).cumprod()
    data["drawdown"] = data["equity"] / data["equity"].cummax() - 1
    return data


def performance_stats(result: pd.DataFrame) -> dict[str, float | int]:
    ret = result["ret"].fillna(0.0)
    years = (result["Date"].iloc[-1] - result["Date"].iloc[0]).days / 365.25
    annual_vol = ret.std() * np.sqrt(TRADING_DAYS)
    return {
        "total_return": result["equity"].iloc[-1] - 1,
        "cagr": result["equity"].iloc[-1] ** (1 / years) - 1,
        "ann_vol": annual_vol,
        "sharpe": (ret.mean() * TRADING_DAYS) / annual_vol if annual_vol > 0 else np.nan,
        "mdd": result["drawdown"].min(),
        "exposure": result["held"].mean(),
        "avg_weight": result["weight"].mean(),
        "trades": int((result["held"].eq(1) & result["held"].shift(1).fillna(0).eq(0)).sum()),
        "stops": int(result["stop_hit"].sum()),
        "risk_days": int(result["risk_signal"].sum()),
        "held_risk_days": int(((result["held"] == 1) & (result["risk_signal"] == 1)).sum()),
        "risk_exits": int(result["risk_exit"].sum()),
        "blocked_entries": int(result["blocked_entry"].sum()),
        "scaled_days": int(result["scaled_day"].sum()),
        "worst_day": ret.min(),
        "best_day": ret.max(),
    }


def run_grid() -> pd.DataFrame:
    strategy_configs = [("peer_8_5", 0.08, 0.05), ("sharp_8_7", 0.08, 0.07)]
    ratios = [0.65, 0.80]
    signals = ["none", "vix_ge_25", "vix_ge_30", "slope_lt_0", "slope_lt_3", "basis_ge_5", "basis_ge_10", "basis_ge_15", "vix_ge_25_or_slope_lt_3", "vix_ge_30_or_slope_lt_0", "vix_ge_25_or_basis_ge_10", "basis_ge_10_or_slope_lt_3", "vix_ge_25_or_slope_lt_3_or_basis_ge_10", "carry_quality_bad", "strong_only_bad"]
    actions = ["none", "no_entry", "exit", "scale_half"]
    rows = []
    for label, entry, exit_ in strategy_configs:
        for ratio in ratios:
            for signal in signals:
                for action in actions:
                    if (signal == "none" and action != "none") or (signal != "none" and action == "none"):
                        continue
                    config = RegimeBacktestConfig(hedge_ratio=ratio, entry_slope=entry, exit_slope=exit_, signal=signal, action=action)
                    result = run_regime_backtest(config)
                    rows.append({"config": label, "ratio": ratio, "signal": signal, "action": action, **performance_stats(result)})
    grid = pd.DataFrame(rows)
    baselines = grid[grid["signal"].eq("none")][["config", "ratio", "sharpe", "cagr", "mdd", "ann_vol", "exposure"]]
    baselines = baselines.rename(columns={col: f"base_{col}" for col in ["sharpe", "cagr", "mdd", "ann_vol", "exposure"]})
    grid = grid.merge(baselines, on=["config", "ratio"], how="left")
    for metric in ["sharpe", "cagr", "mdd", "ann_vol", "exposure"]:
        grid[f"delta_{metric}"] = grid[metric] - grid[f"base_{metric}"]
    return grid


def main() -> None:
    output_dir = Path("reports/generated/regime_overlay_grid")
    output_dir.mkdir(parents=True, exist_ok=True)
    grid = run_grid()
    grid.to_csv(output_dir / "regime_overlay_grid_stopclip.csv", index=False)
    top = grid[~grid["signal"].eq("none")].sort_values(["delta_sharpe", "sharpe"], ascending=False).head(30)
    top.to_csv(output_dir / "top30_regime_improvements.csv", index=False)
    print(top[["config", "ratio", "signal", "action", "cagr", "ann_vol", "sharpe", "mdd", "delta_sharpe", "delta_cagr", "delta_mdd"]].to_string(index=False))


if __name__ == "__main__":
    main()

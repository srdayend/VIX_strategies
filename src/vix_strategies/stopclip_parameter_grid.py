from __future__ import annotations

from pathlib import Path

import pandas as pd

from .hedged_rolldown import HedgedRollDownConfig, performance_stats, run_hedged_rolldown


RATIOS = [0.65, 0.80]
ENTRY_SLOPES = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
EXIT_SLOPES = [0.03, 0.04, 0.05, 0.06, 0.07]


def run_grid() -> pd.DataFrame:
    rows = []
    for ratio in RATIOS:
        for entry in ENTRY_SLOPES:
            for exit_ in EXIT_SLOPES:
                if exit_ >= entry:
                    continue
                config = HedgedRollDownConfig(
                    hedge_ratio=ratio,
                    entry_slope=entry,
                    exit_slope=exit_,
                    vx1_cap=30.0,
                    stop_loss=-0.02,
                    stop_clip=True,
                    avoid_roll=True,
                )
                result = run_hedged_rolldown(config)
                rows.append({"ratio": ratio, "entry_slope": entry, "exit_slope": exit_, **performance_stats(result)})
    return pd.DataFrame(rows)


def main() -> None:
    output_dir = Path("reports/generated/stopclip_parameter_grid")
    output_dir.mkdir(parents=True, exist_ok=True)
    grid = run_grid()
    grid.to_csv(output_dir / "stopclip_grid_065_080.csv", index=False)

    for metric in ["sharpe", "cagr", "mdd", "exposure", "stops"]:
        for ratio in RATIOS:
            pivot = grid[grid["ratio"].eq(ratio)].pivot(index="entry_slope", columns="exit_slope", values=metric)
            pivot.to_csv(output_dir / f"pivot_{metric}_r{ratio:.2f}.csv")

    top = grid.sort_values("sharpe", ascending=False).head(20)
    top.to_csv(output_dir / "top20_by_sharpe.csv", index=False)
    print(top[["ratio", "entry_slope", "exit_slope", "cagr", "annual_vol", "sharpe", "mdd", "exposure", "trades", "stops"]].to_string(index=False))


if __name__ == "__main__":
    main()

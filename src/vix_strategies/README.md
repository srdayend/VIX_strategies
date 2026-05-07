# Code Module Guide

The package is split by responsibility so file names describe the work they do before you open them.

## `data/`

- `source_paths.py` resolves local source-file paths and environment-variable overrides.
- `excel_loaders.py` loads the Excel workbooks and builds reusable analysis frames.

## `analysis/`

- `summarize_term_structure.py` summarizes coverage, settlement distributions, slope distributions, and VIX regimes.
- `vix_distribution_rolldown_hedge_ratio.py` produces the baseline calendar-spread weight study, including VIX spot distribution, term-structure diagnostics, roll-down premia, spike hedge ratios, and realized PnL-based `r` sizing.

Run:

```bash
python -m src.vix_strategies.analysis.summarize_term_structure
python -m src.vix_strategies.analysis.vix_distribution_rolldown_hedge_ratio
```

## `backtests/`

- `simple_m1_m2_carry_backtest.py` is the earliest rank-based M1/M2 carry scaffold.
- `hedged_vx1_vx2_rolldown.py` is the main `r * VX1 - VX2` strategy engine with entry/exit hysteresis, VX1 cap, roll-day avoidance, and stop-loss options.

Run:

```bash
python -m src.vix_strategies.backtests.simple_m1_m2_carry_backtest
python -m src.vix_strategies.backtests.hedged_vx1_vx2_rolldown
```

## `experiments/`

- `stop_loss_parameter_grid.py` runs the stop-clipped entry/exit threshold grid for `0.65` and `0.80`.
- `compare_065_vs_080_hedge_ratios.py` compares `0.65` and `0.80` by regime and basis bucket.
- `regime_overlay_grid.py` tests VIX, slope, and basis regime overlays.
- `reproduce_peer_research.py` reproduces pieces of the peer research package.

Run:

```bash
python -m src.vix_strategies.experiments.stop_loss_parameter_grid
python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios
python -m src.vix_strategies.experiments.regime_overlay_grid
python -m src.vix_strategies.experiments.reproduce_peer_research
```

## Output Convention

Scripts that generate files should write under:

```text
reports/generated/<experiment_name>/
```

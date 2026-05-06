# Code Module Guide

This package contains loaders, feature engineering helpers, and research backtest scripts for the VIX strategies project.

## Stable Data Layer

- `config.py` resolves local source-file paths and environment-variable overrides.
- `loaders.py` loads the Excel workbooks and builds reusable analysis frames.

These modules are shared by the analysis and backtest scripts. Keep path handling and workbook parsing here instead of duplicating it inside experiment files.

## Analysis Scripts

- `analysis.py` summarizes term-structure coverage, settlement distributions, slope distributions, and VIX regimes.

Run:

```bash
python -m src.vix_strategies.analysis
```

## Backtest And Experiment Scripts

- `backtest.py` is the earliest generic hedged-carry scaffold using rank-based M1/M2 returns.
- `hedged_rolldown.py` implements the main `r * VX1 - VX2` hedged roll-down strategy with entry/exit hysteresis, VX1 cap, roll-day avoidance, and stop-loss options.
- `stopclip_parameter_grid.py` runs the entry/exit threshold grid for `0.65` and `0.80` after stop clipping.
- `compare_hedge_ratios.py` compares `0.65` and `0.80` by regime and basis bucket.
- `regime_backtest_grid.py` tests VIX, slope, and basis regime overlays.
- `peer_research_reproduction.py` reproduces pieces of the peer research package.

Example runs:

```bash
python -m src.vix_strategies.hedged_rolldown
python -m src.vix_strategies.stopclip_parameter_grid
python -m src.vix_strategies.compare_hedge_ratios
python -m src.vix_strategies.regime_backtest_grid
```

## Output Convention

Scripts that generate files should write under:

```text
reports/generated/<experiment_name>/
```

This keeps generated CSVs separate from handwritten research notes.

## Cleanup Backlog

Potential future package split:

```text
src/vix_strategies/data/          config and workbook loaders
src/vix_strategies/analysis/      summaries and diagnostics
src/vix_strategies/backtests/     strategy engines and parameter grids
src/vix_strategies/experiments/   one-off research reproductions
```

Do this only after the current scripts are stable enough to tolerate import-path changes.

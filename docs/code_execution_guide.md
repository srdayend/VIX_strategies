# Code Execution Guide

This guide connects each research question and result note to the code that produces or supports it.

Run commands from the repository root after installing `requirements.txt`.

## Environment

```bash
pip install -r requirements.txt
```

The loaders expect the default local Excel paths described in [`01_data/source_data_inventory.md`](01_data/source_data_inventory.md), or these environment variables:

```text
VIX_TERM_STRUCTURE_PATH
VIX_FUTURES_BY_MATURITY_PATH
VIX_INDEX_PATH
```

## Data Loading And Summary

| Research purpose | Code | Command | Main output |
|---|---|---|---|
| Load source paths | `src/vix_strategies/data/source_paths.py` | Imported by other modules | Validated source workbook paths |
| Load Excel data | `src/vix_strategies/data/excel_loaders.py` | Imported by other modules | Term structure, VIX index, maturity sheets |
| Summarize term structure | `src/vix_strategies/analysis/summarize_term_structure.py` | `python -m src.vix_strategies.analysis.summarize_term_structure` | JSON summary printed to console |

Related docs:

- [`01_data/source_data_inventory.md`](01_data/source_data_inventory.md)
- [`01_data/initial_data_findings.md`](01_data/initial_data_findings.md)

## Backtest Engines

| Research purpose | Code | Command | Main output |
|---|---|---|---|
| Simple M1/M2 carry diagnostic | `src/vix_strategies/backtests/simple_m1_m2_carry_backtest.py` | `python -m src.vix_strategies.backtests.simple_m1_m2_carry_backtest` | JSON backtest summary printed to console |
| Main hedged VX1/VX2 roll-down strategy | `src/vix_strategies/backtests/hedged_vx1_vx2_rolldown.py` | `python -m src.vix_strategies.backtests.hedged_vx1_vx2_rolldown` | Performance stats printed to console |

Related docs:

- [`02_strategy/peer_research_baseline.md`](02_strategy/peer_research_baseline.md)
- [`02_strategy/peer_080_crosscheck.md`](02_strategy/peer_080_crosscheck.md)
- [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md)

## Experiment Scripts

| Result note | Code | Command | Output directory |
|---|---|---|---|
| [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md) | `src/vix_strategies/experiments/compare_065_vs_080_hedge_ratios.py` | `python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios` | `reports/generated/compare_065_vs_080_hedge_ratios/` |
| [`03_results/stop_loss_parameter_grid.md`](03_results/stop_loss_parameter_grid.md) | `src/vix_strategies/experiments/stop_loss_parameter_grid.py` | `python -m src.vix_strategies.experiments.stop_loss_parameter_grid` | `reports/generated/stop_loss_parameter_grid/` |
| [`03_results/regime_overlay_grid.md`](03_results/regime_overlay_grid.md) | `src/vix_strategies/experiments/regime_overlay_grid.py` | `python -m src.vix_strategies.experiments.regime_overlay_grid` | `reports/generated/regime_overlay_grid/` |
| [`02_strategy/peer_research_baseline.md`](02_strategy/peer_research_baseline.md) and [`02_strategy/peer_080_crosscheck.md`](02_strategy/peer_080_crosscheck.md) | `src/vix_strategies/experiments/reproduce_peer_research.py` | `python -m src.vix_strategies.experiments.reproduce_peer_research` | `reports/generated/reproduce_peer_research/` |

## What Each Experiment Produces

### `compare_065_vs_080_hedge_ratios.py`

Purpose:

- Compare fixed `0.65VX1 - VX2` and fixed `0.80VX1 - VX2` under identical trading windows.
- Attribute the performance gap by regime and VX1/VIX basis bucket.

Generated files:

```text
reports/generated/compare_065_vs_080_hedge_ratios/
  daily_compare_065_080.csv
  regime_summary.csv
  basis_summary.csv
  held_day_quantiles.csv
```

### `stop_loss_parameter_grid.py`

Purpose:

- Test entry/exit threshold sensitivity for `0.65` and `0.80`.
- Use stop-clipped loss assumption: `ret = max(unclipped_ret, -2%)`.

Generated files:

```text
reports/generated/stop_loss_parameter_grid/
  stop_clipped_grid_065_080.csv
  pivot_sharpe_r0.65.csv
  pivot_sharpe_r0.80.csv
  pivot_cagr_r0.65.csv
  pivot_cagr_r0.80.csv
  pivot_mdd_r0.65.csv
  pivot_mdd_r0.80.csv
  pivot_exposure_r0.65.csv
  pivot_exposure_r0.80.csv
  pivot_stops_r0.65.csv
  pivot_stops_r0.80.csv
  top20_by_sharpe.csv
```

### `regime_overlay_grid.py`

Purpose:

- Test whether VIX-level, slope, and VX1/VIX basis overlays improve `0.65` and `0.80`.
- Compare `no_entry`, `exit`, and `scale_half` actions.

Generated files:

```text
reports/generated/regime_overlay_grid/
  regime_overlay_grid_stopclip.csv
  top30_regime_improvements.csv
```

### `reproduce_peer_research.py`

Purpose:

- Reproduce peer profile results, hedge-ratio scans, shock-beta diagnostics, and front-slope stationarity checks.

Generated files:

```text
reports/generated/reproduce_peer_research/
  peer_profiles.csv
  peer_hedge_ratio_scan.csv
  peer_shock_beta.csv
  peer_front_slope_stationarity.csv
```

## Maintenance Rule

Whenever a new result document is added under `docs/03_results/`, add a row to the experiment table above with:

1. The result note path.
2. The exact code file path.
3. The exact `python -m ...` command.
4. The generated output directory.

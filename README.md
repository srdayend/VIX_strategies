# VIX Strategies Research Lab

Research workspace for VIX futures term-structure analysis and hedged roll-down carry strategies.

The repository currently uses local Excel workbooks as source data. It is a research lab, not yet a production trading system: the goal is to make the data, assumptions, experiments, and conclusions easy to audit as the strategy evolves.

## Current Thesis

The working strategy family is a hedged VIX futures roll-down carry trade:

```text
Position = r * VX1 - VX2
front_slope = ln(VX2 / VX1)
```

Core research view:

- `0.65VX1 - VX2` is the economically anchored hedge-ratio baseline, based on observed VX2/VX1 shock beta.
- `0.80VX1 - VX2` is the empirical high-Sharpe benchmark in the current rank-based tests.
- VX1/VIX basis is the main candidate filter for improving strategy quality, especially for higher hedge ratios.
- Contract-level testing, realistic costs, and stop-loss modeling are the next major robustness checks.

## Repository Map

```text
src/vix_strategies/      Python loaders, analysis scripts, and backtest experiments
docs/                    Human-written research notes, plans, and conclusions
reports/                 Generated analysis outputs and result tables
requirements.txt         Minimal Python dependencies
```

Start here:

- [`docs/README.md`](docs/README.md): ordered map of all research notes.
- [`src/vix_strategies/README.md`](src/vix_strategies/README.md): code module guide and execution commands.
- [`reports/README.md`](reports/README.md): generated-output conventions.

## Research Notes

Recommended reading order:

1. [`docs/peer_research_onepage.md`](docs/peer_research_onepage.md) - peer strategy baseline and economic framing.
2. [`docs/initial_findings.md`](docs/initial_findings.md) - first-pass data facts and naive backtest diagnostic.
3. [`docs/regime_framework.md`](docs/regime_framework.md) - VIX level, front slope, and VX1/VIX basis regime framework.
4. [`docs/hedge_ratio_065_vs_080_analysis.md`](docs/hedge_ratio_065_vs_080_analysis.md) - deep dive on `0.65` versus `0.80`.
5. [`docs/stopclip_parameter_grid_analysis.md`](docs/stopclip_parameter_grid_analysis.md) - entry/exit grid after stop-loss clipping.
6. [`docs/regime_backtest_grid_analysis.md`](docs/regime_backtest_grid_analysis.md) - regime overlay grid and interpretation.

Planning notes:

- [`docs/data_sources.md`](docs/data_sources.md)
- [`docs/analysis_plan.md`](docs/analysis_plan.md)
- [`docs/backtesting_plan.md`](docs/backtesting_plan.md)
- [`docs/peer_strategy_crosscheck_080.md`](docs/peer_strategy_crosscheck_080.md)

## Source Data

Default local paths:

- `C:\Users\user\Downloads\VIX_futures_term_structure.xlsx`
- `C:\Users\user\Downloads\VIX_futures_by_maturity (1).xlsx`
- `C:\Users\user\OneDrive\바탕 화면\outputs\vix_cboe\CBOE_VIX_Index_Daily_OHLC.xlsx`

Environment variables can override these paths:

- `VIX_TERM_STRUCTURE_PATH`
- `VIX_FUTURES_BY_MATURITY_PATH`
- `VIX_INDEX_PATH`

## Quick Start

Install dependencies in a Python environment with `pandas`, `numpy`, and `openpyxl`, then run from the repository root:

```bash
python -m src.vix_strategies.analysis
python -m src.vix_strategies.hedged_rolldown
python -m src.vix_strategies.stopclip_parameter_grid
python -m src.vix_strategies.regime_backtest_grid
```

Generated CSV outputs should be written under `reports/generated/`.

## Current Data Snapshot

The latest documented first pass used source data with:

- VIX futures term structure coverage: `2004-03-26` to `2026-05-01`
- Term structure rows: `5,578`
- Complete 9-maturity curves: `3,578` rows, about `64.1%`
- VIX index coverage: `1990-01-02` to `2026-05-05`
- M2 > M1 contango days: about `79.0%`
- M2 < M1 backwardation days: about `15.9%`

VIX regime snapshot:

| VIX close bucket | Days | Contango rate | Avg M1-M2 % | Avg M1-M4 % |
|---|---:|---:|---:|---:|
| <15 | 2,137 | 94.6% | 9.00% | 20.46% |
| 15-20 | 1,710 | 84.9% | 6.38% | 13.77% |
| 20-25 | 865 | 68.6% | 4.18% | 7.18% |
| 25-30 | 416 | 59.9% | 1.41% | 0.59% |
| 30+ | 448 | 19.9% | -5.08% | -11.40% |

## Cleanup Backlog

The next cleanup pass should decide whether to physically split the code into stable modules and experiment scripts, for example:

```text
src/vix_strategies/data/
src/vix_strategies/research/
src/vix_strategies/backtests/
```

For now, this branch keeps file paths stable and adds navigation so existing scripts and links continue to work.

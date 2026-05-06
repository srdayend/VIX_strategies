# VIX Strategies Research Lab

Research workspace for VIX futures term-structure analysis and hedged roll-down carry strategies.

The repository uses local Excel workbooks as source data. It is a research lab, not yet a production trading system: the goal is to keep the data, assumptions, experiments, and conclusions easy to audit.

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
src/vix_strategies/
  data/           Source path resolution and Excel workbook loaders
  analysis/       Data summaries and diagnostics
  backtests/      Reusable strategy engines and baseline backtests
  experiments/    Parameter grids, peer reproductions, and one-off comparisons

docs/             Human-written research notes, plans, and conclusions
reports/          Generated analysis outputs and result tables
requirements.txt  Minimal Python dependencies
```

Start here:

- [`docs/README.md`](docs/README.md): ordered map of all research notes.
- [`src/vix_strategies/README.md`](src/vix_strategies/README.md): code module guide and execution commands.
- [`reports/README.md`](reports/README.md): generated-output conventions.

## Quick Start

Install dependencies in a Python environment with `pandas`, `numpy`, and `openpyxl`, then run from the repository root:

```bash
python -m src.vix_strategies.analysis.summarize_term_structure
python -m src.vix_strategies.backtests.hedged_vx1_vx2_rolldown
python -m src.vix_strategies.experiments.stop_loss_parameter_grid
python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios
python -m src.vix_strategies.experiments.regime_overlay_grid
```

Generated CSV outputs should be written under `reports/generated/`.

## Source Data

Default local paths:

- `C:\Users\user\Downloads\VIX_futures_term_structure.xlsx`
- `C:\Users\user\Downloads\VIX_futures_by_maturity (1).xlsx`
- `C:\Users\user\OneDrive\바탕 화면\outputs\vix_cboe\CBOE_VIX_Index_Daily_OHLC.xlsx`

Environment variables can override these paths:

- `VIX_TERM_STRUCTURE_PATH`
- `VIX_FUTURES_BY_MATURITY_PATH`
- `VIX_INDEX_PATH`

## Research Notes

Recommended reading order:

1. [`docs/peer_research_onepage.md`](docs/peer_research_onepage.md) - peer strategy baseline and economic framing.
2. [`docs/initial_findings.md`](docs/initial_findings.md) - first-pass data facts and naive backtest diagnostic.
3. [`docs/regime_framework.md`](docs/regime_framework.md) - VIX level, front slope, and VX1/VIX basis regime framework.
4. [`docs/hedge_ratio_065_vs_080_analysis.md`](docs/hedge_ratio_065_vs_080_analysis.md) - deep dive on `0.65` versus `0.80`.
5. [`docs/stopclip_parameter_grid_analysis.md`](docs/stopclip_parameter_grid_analysis.md) - entry/exit grid after stop-loss clipping.
6. [`docs/regime_backtest_grid_analysis.md`](docs/regime_backtest_grid_analysis.md) - regime overlay grid and interpretation.

## Current Data Snapshot

The latest documented first pass used source data with:

- VIX futures term structure coverage: `2004-03-26` to `2026-05-01`
- Term structure rows: `5,578`
- Complete 9-maturity curves: `3,578` rows, about `64.1%`
- VIX index coverage: `1990-01-02` to `2026-05-05`
- M2 > M1 contango days: about `79.0%`
- M2 < M1 backwardation days: about `15.9%`

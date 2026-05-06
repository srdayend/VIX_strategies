# VIX Strategies Research Lab

This repository is the working lab for analyzing VIX futures term structure data and testing roll-down carry / hedged strategies.

The project intentionally starts from existing local Excel source files instead of rebuilding the data collection pipeline.

## Source files

Current local source files:

- `C:\Users\user\Downloads\VIX_futures_term_structure.xlsx`
- `C:\Users\user\Downloads\VIX_futures_by_maturity (1).xlsx`
- `C:\Users\user\OneDrive\바탕 화면\outputs\vix_cboe\CBOE_VIX_Index_Daily_OHLC.xlsx`

Environment variables can override these paths:

- `VIX_TERM_STRUCTURE_PATH`
- `VIX_FUTURES_BY_MATURITY_PATH`
- `VIX_INDEX_PATH`

## Initial data facts

Quick inspection of the current files showed:

- VIX futures term structure coverage: `2004-03-26` to `2026-05-01`
- Term structure rows: `5,578`
- Complete 9-maturity curves: `3,578` rows, about `64.1%`
- VIX index coverage: `1990-01-02` to `2026-05-05`
- M2 > M1 contango days: about `79.0%`
- M2 < M1 backwardation days: about `15.9%`

VIX regime snapshot from the first pass:

| VIX close bucket | Days | Contango rate | Avg M1-M2 % | Avg M1-M4 % |
|---|---:|---:|---:|---:|
| <15 | 2,137 | 94.6% | 9.00% | 20.46% |
| 15-20 | 1,710 | 84.9% | 6.38% | 13.77% |
| 20-25 | 865 | 68.6% | 4.18% | 7.18% |
| 25-30 | 416 | 59.9% | 1.41% | 0.59% |
| 30+ | 448 | 19.9% | -5.08% | -11.40% |

## Project axes

### 1. Data analysis

Analyze the data itself before forcing strategies onto it:

- Distribution of M1-M9 settlements
- Distribution of slopes: M2/M1, M4/M1, M7/M1
- Contango and backwardation frequency
- VIX-index regime behavior
- Term-structure shape clustering
- Volatility spike and normalization windows
- Volume and open-interest quality checks by maturity

### 2. Strategy backtesting

Backtest roll-down carry and hedged variants:

- Short front / long deferred futures carry
- Slope-gated carry strategies
- VIX-regime filtered strategies
- Backwardation avoidance rules
- Crisis hedge overlays
- Dynamic hedge ratios
- Transaction-cost and roll-friction sensitivity

## Repository structure

```text
src/vix_strategies/
  config.py      # Local source path resolution
  loaders.py     # Excel loaders and feature engineering helpers
  analysis.py    # Data analysis CLI
  backtest.py    # Strategy backtest framework

docs/
  data_sources.md
  analysis_plan.md
  backtesting_plan.md

reports/
  README.md
```

## Quick start

Install dependencies in a Python environment with `pandas`, `numpy`, and `openpyxl`, then run:

```bash
python -m src.vix_strategies.analysis
python -m src.vix_strategies.backtest
```

On this machine, Codex can also run these scripts using its bundled Python runtime.

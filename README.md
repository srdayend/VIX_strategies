# VIX Strategies Research Lab

Research workspace for VIX futures calendar-spread strategies.

The project studies a hedged VIX futures roll-down trade:

```text
Position = r * VX1 - 1.00 * VX2
front_slope = ln(VX2 / VX1)
```

The core idea is to short the deferred VIX future (`VX2`) to harvest roll-down carry, while buying the front future (`VX1`) to hedge volatility spikes. The main research question is how much VX1 should be held against one unit of short VX2.

## Current View

- VIX spot has a low-base, right-tail spike structure.
- VIX futures are usually in contango, especially at the front of the curve.
- A simple `1.00VX1 - 1.00VX2` spread is not the cleanest baseline because it buys more VX1 than the observed median spike hedge requires.
- The economic anchor is around `0.65VX1 - VX2`, based on spike-day `dVX2 / dVX1`.
- The more rigorous realized-PnL sizing points to `0.70VX1 - VX2` as the cleaner baseline.
- `0.80VX1 - VX2` is a stronger spike-hedge / high-Sharpe candidate, but it is more front-volatility tilted.
- The next major robustness steps are basis-aware ratio rules, contract-level testing, transaction costs, and stop-slippage assumptions.

## Best Reading Path

For a quick handoff, read these in order:

1. [`docs/00_research_summary.md`](docs/00_research_summary.md) - current synthesis and conclusions.
2. [`docs/03_results/vix_distribution_rolldown_hedge_ratio.md`](docs/03_results/vix_distribution_rolldown_hedge_ratio.md) - baseline weight study and latest sizing logic.
3. [`docs/03_results/hedge_ratio_065_vs_080.md`](docs/03_results/hedge_ratio_065_vs_080.md) - why `0.65` and `0.80` behave differently.
4. [`docs/03_results/stop_loss_parameter_grid.md`](docs/03_results/stop_loss_parameter_grid.md) - entry/exit and stop-loss sensitivity.
5. [`docs/03_results/regime_overlay_grid.md`](docs/03_results/regime_overlay_grid.md) - VIX, slope, and basis regime overlays.

The full document index is in [`docs/README.md`](docs/README.md).

## Repository Map

```text
docs/
  00_research_summary.md       Current synthesis
  01_data/                     Source data notes and first-pass findings
  02_strategy/                 Strategy framing and peer research baseline
  03_results/                  Main result notes and interpretation
  04_backlog/                  Open research tasks
  code_execution_guide.md      Code-to-result map

src/vix_strategies/
  data/                        Excel loaders and source path resolution
  analysis/                    Data diagnostics and baseline weight study
  backtests/                   Reusable strategy engines
  experiments/                 Parameter grids and peer reproduction scripts

reports/generated/             Reproducible CSV and chart outputs
```

## Source Data

The repository does not store the Excel source workbooks. By default, the code expects:

```text
C:\Users\user\Downloads\VIX_futures_term_structure.xlsx
C:\Users\user\Downloads\VIX_futures_by_maturity (1).xlsx
C:\Users\user\OneDrive\바탕 화면\outputs\vix_cboe\CBOE_VIX_Index_Daily_OHLC.xlsx
```

Override paths with:

```text
VIX_TERM_STRUCTURE_PATH
VIX_FUTURES_BY_MATURITY_PATH
VIX_INDEX_PATH
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the latest baseline weight study:

```bash
python -m src.vix_strategies.analysis.vix_distribution_rolldown_hedge_ratio
```

Run the main strategy experiments:

```bash
python -m src.vix_strategies.experiments.reproduce_peer_research
python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios
python -m src.vix_strategies.experiments.stop_loss_parameter_grid
python -m src.vix_strategies.experiments.regime_overlay_grid
```

Generated outputs are written under `reports/generated/`.

# Research Notes

This folder is the research trail for the VIX calendar-spread project. The goal is to keep the logic auditable without making a new reader dig through every intermediate note.

## Start Here

1. [`00_research_summary.md`](00_research_summary.md) - current synthesis and latest conclusions.
2. [`03_results/vix_distribution_rolldown_hedge_ratio.md`](03_results/vix_distribution_rolldown_hedge_ratio.md) - baseline weight study and PnL-based `r` sizing.
3. [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md) - attribution between the economic anchor and high-Sharpe variant.
4. [`03_results/stop_loss_parameter_grid.md`](03_results/stop_loss_parameter_grid.md) - stop-loss and threshold sensitivity.
5. [`03_results/regime_overlay_grid.md`](03_results/regime_overlay_grid.md) - VIX, slope, and basis overlay tests.

## Folder Map

```text
docs/
  00_research_summary.md
  code_execution_guide.md
  content_map.md
  01_data/        Source data notes and first-pass observations
  02_strategy/    Strategy framing and peer baseline
  03_results/     Main result notes and interpretation
  04_backlog/     Plans, open checks, and next research tasks
```

## Axis-Based Index

### Data

- [`01_data/source_data_inventory.md`](01_data/source_data_inventory.md): source workbook inventory and schemas.
- [`01_data/initial_data_findings.md`](01_data/initial_data_findings.md): first-pass data coverage and regime observations.

### Strategy Framing

- [`02_strategy/peer_research_baseline.md`](02_strategy/peer_research_baseline.md): peer strategy baseline and economic rationale.
- [`02_strategy/peer_080_crosscheck.md`](02_strategy/peer_080_crosscheck.md): cross-check of the peer `0.80` benchmark.
- [`02_strategy/regime_framework.md`](02_strategy/regime_framework.md): VIX level, front slope, and VX1/VIX basis framework.

### Results

- [`03_results/vix_distribution_rolldown_hedge_ratio.md`](03_results/vix_distribution_rolldown_hedge_ratio.md): baseline calendar-spread weight study.
- [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md): performance and regime attribution for `0.65` versus `0.80`.
- [`03_results/stop_loss_parameter_grid.md`](03_results/stop_loss_parameter_grid.md): entry/exit grid with stop-loss clipping.
- [`03_results/regime_overlay_grid.md`](03_results/regime_overlay_grid.md): regime overlay grid and interpretation.

### Backlog

- [`04_backlog/data_analysis_plan.md`](04_backlog/data_analysis_plan.md): data analysis plan.
- [`04_backlog/strategy_backtesting_plan.md`](04_backlog/strategy_backtesting_plan.md): strategy backtesting plan.
- [`04_backlog/research_backlog.md`](04_backlog/research_backlog.md): remaining research tasks.

## Support Files

- [`code_execution_guide.md`](code_execution_guide.md): maps result notes to scripts, commands, and generated outputs.
- [`content_map.md`](content_map.md): audit trail from the earlier document reorganization.

## Current Working Conclusions

- The strategy family is `r * VX1 - VX2`, not a plain one-for-one spread by default.
- `0.65` remains the original economic anchor from spike beta.
- `0.70` is the cleaner current PnL-based baseline.
- `0.80` is a stronger spike hedge / high-Sharpe candidate, but it is more front-volatility tilted.
- VX1/VIX basis is the main candidate filter for higher-ratio variants.
- Contract-level tests, transaction costs, roll mechanics, and stop slippage are the next robustness layer.

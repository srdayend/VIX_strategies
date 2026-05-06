# Research Notes

This folder is organized as a research trail. The detailed original notes are grouped by research axis, and navigation files sit at the top level.

No detailed note was intentionally summarized away during this cleanup. Use [`content_map.md`](content_map.md) to see where every original document moved.

## Start Here

- [`00_research_summary.md`](00_research_summary.md) - current synthesis, working conclusions, favorite candidates, and next decisions.
- [`content_map.md`](content_map.md) - exact old-to-new document map, used to audit that no content was dropped.
- [`code_execution_guide.md`](code_execution_guide.md) - which code produces or supports each result note.

## Folder Map

```text
docs/
  00_research_summary.md
  content_map.md
  code_execution_guide.md
  01_data/        Source data notes and first-pass observations
  02_strategy/    Strategy framing, peer baseline, and regime framework
  03_results/     Experiment results and interpretation
  04_backlog/     Plans, open checks, and next research tasks
```

## Recommended Reading Order

1. [`00_research_summary.md`](00_research_summary.md)
2. [`code_execution_guide.md`](code_execution_guide.md)
3. [`01_data/source_data_inventory.md`](01_data/source_data_inventory.md)
4. [`01_data/initial_data_findings.md`](01_data/initial_data_findings.md)
5. [`02_strategy/peer_research_baseline.md`](02_strategy/peer_research_baseline.md)
6. [`02_strategy/regime_framework.md`](02_strategy/regime_framework.md)
7. [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md)
8. [`03_results/stop_loss_parameter_grid.md`](03_results/stop_loss_parameter_grid.md)
9. [`03_results/regime_overlay_grid.md`](03_results/regime_overlay_grid.md)
10. [`04_backlog/research_backlog.md`](04_backlog/research_backlog.md)

## Axis-Based Index

### Data

- [`01_data/source_data_inventory.md`](01_data/source_data_inventory.md)
- [`01_data/initial_data_findings.md`](01_data/initial_data_findings.md)

### Strategy Framing

- [`02_strategy/peer_research_baseline.md`](02_strategy/peer_research_baseline.md)
- [`02_strategy/peer_080_crosscheck.md`](02_strategy/peer_080_crosscheck.md)
- [`02_strategy/regime_framework.md`](02_strategy/regime_framework.md)

### Experiment Results

- [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md)
- [`03_results/stop_loss_parameter_grid.md`](03_results/stop_loss_parameter_grid.md)
- [`03_results/regime_overlay_grid.md`](03_results/regime_overlay_grid.md)

### Backlog And Plans

- [`04_backlog/data_analysis_plan.md`](04_backlog/data_analysis_plan.md)
- [`04_backlog/strategy_backtesting_plan.md`](04_backlog/strategy_backtesting_plan.md)
- [`04_backlog/research_backlog.md`](04_backlog/research_backlog.md)

## Current Working Conclusions

- `0.65VX1 - VX2` is the economic hedge-ratio anchor because it is tied to spike-day `dVX2/dVX1` behavior.
- `0.80VX1 - VX2` is the empirical high-Sharpe benchmark and deserves to stay in the candidate set.
- Stop-loss modeling materially changes the strategy profile; close-only and stop-clipped results should never be mixed without disclosure.
- VIX-level and slope overlays add little after the base rules are active.
- `VX1/VIX` basis is the most useful additional quality filter, especially for the `0.80` variant.
- The next robustness step is contract-level testing with explicit roll, cost, liquidity, and stop-slippage assumptions.

## Maintenance Rules

When adding a new note:

1. Put it in the right folder by research axis.
2. Add it to this README if it changes the research trail.
3. Add old-to-new movement details to `content_map.md` if a file is renamed or moved.
4. Add exact code and command details to `code_execution_guide.md` if it is a result note.
5. Start result notes with the conclusion and assumptions, but keep detailed tables and reasoning intact.

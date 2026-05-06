# Research Notes Index

This folder contains human-written research notes for the VIX strategies project. The files are best read as a sequence: source-data orientation, baseline research, strategy experiments, then cleanup plans.

## Recommended Reading Order

### 1. Orientation

- [`data_sources.md`](data_sources.md) - source workbook inventory and path assumptions.
- [`initial_findings.md`](initial_findings.md) - first data pass, coverage facts, and a naive baseline diagnostic.
- [`analysis_plan.md`](analysis_plan.md) - data-analysis agenda and open checks.
- [`backtesting_plan.md`](backtesting_plan.md) - backtest agenda and realism gaps.

### 2. External Baseline

- [`peer_research_onepage.md`](peer_research_onepage.md) - summary of the peer research package, including the baseline hedged roll-down rules.
- [`peer_strategy_crosscheck_080.md`](peer_strategy_crosscheck_080.md) - cross-check focused on the `0.80VX1 - VX2` variant.

### 3. Strategy Framework

- [`regime_framework.md`](regime_framework.md) - VIX level, front slope, and VX1/VIX basis regime framework.
- [`hedge_ratio_065_vs_080_analysis.md`](hedge_ratio_065_vs_080_analysis.md) - explanation of why `0.65` is the economic anchor and `0.80` is the empirical benchmark.

### 4. Parameter And Regime Experiments

- [`stopclip_parameter_grid_analysis.md`](stopclip_parameter_grid_analysis.md) - entry/exit parameter grid after stop-loss clipping.
- [`regime_backtest_grid_analysis.md`](regime_backtest_grid_analysis.md) - regime overlay results for `0.65` and `0.80` strategy variants.

## Working Conclusions

Current working interpretation:

- The peer package gives a strong baseline for `r * VX1 - VX2` hedged roll-down carry.
- The `0.65` hedge ratio is defensible because it is tied to VX2/VX1 spike-day behavior.
- The `0.80` hedge ratio performs better in the current rank-based tests, but it has more front-volatility character.
- VIX-level and slope regime overlays add limited incremental value once the base entry/exit rules are active.
- VX1/VIX basis is the most promising additional quality filter.
- The most important next robustness step is contract-level testing with explicit roll and cost assumptions.

## Maintenance Rules

When adding a new note:

1. Add it to this index.
2. State whether it is a plan, result, or interpretation note.
3. Link any generated CSV/table output under `reports/generated/`.
4. Keep final conclusions near the top of the note, with raw tables below.

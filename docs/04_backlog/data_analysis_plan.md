# Data Analysis Plan

The first phase is to understand the instrument behavior before optimizing a trading rule.

## Core distributions

- Distribution of M1-M9 settlements
- Daily changes and realized volatility by maturity rank
- Slope distributions: M2/M1 - 1, M4/M1 - 1, M7/M1 - 1, M9/M1 - 1
- Spread distributions: M2 - M1, M4 - M1, M7 - M1

## Term-structure states

- Contango: M2 > M1
- Backwardation: M2 < M1
- Flat: near-zero M2-M1 spread
- Steep contango: top quantile of M1-M2 percentage slope
- Deep backwardation: bottom quantile of M1-M2 percentage slope

## Regime framework

Primary regime document: [`regime_framework.md`](regime_framework.md)

Use two simple, interpretable axes first:

- VIX index level: `<15`, `15-20`, `20-30`, `>=30`
- Front futures slope: `M2 / M1 - 1`, bucketed as `<0%`, `0-3%`, `3-8%`, `>=8%`

Initial trading-state interpretation:

- Carry ON: `VIX < 20` and `front_slope >= 3%`
- Carry HALF / selective: `20 <= VIX < 30` and `front_slope >= 8%`
- Carry OFF: `VIX >= 30` or `front_slope < 0%`

## Hedge ratio comparison

Primary comparison document: [`hedge_ratio_065_vs_080_analysis.md`](hedge_ratio_065_vs_080_analysis.md)

Compare the economically anchored `0.65VX1 - VX2` against the highest-Sharpe `0.80VX1 - VX2` under identical rules:

- Entry: `ln(VX2/VX1) > 8%`
- Exit: `ln(VX2/VX1) < 5%`
- VX1 cap: `30`
- Stop: `-2%`
- Roll-day avoidance

The first pass shows that `0.80` wins mostly through stronger right-tail participation when VX1 is not expensive versus spot VIX, while it loses quality in high `VX1/VIX` basis zones.

## Stop-clipped threshold grid

Primary grid document: [`stopclip_parameter_grid_analysis.md`](stopclip_parameter_grid_analysis.md)

Test `0.65` and `0.80` across entry/exit thresholds after changing the stop assumption from close-only loss realization to intraday stop clipping:

- Stop logic: `ret = max(unclipped_ret, -2%)`
- Entry grid: `6%` to `12%`
- Exit grid: `3%` to `7%`
- Constraint: `exit < entry`

Initial read-through: stop clipping materially improves both ratios; `0.80` still dominates the top Sharpe region; exit thresholds around `6-7%` often improve Sharpe versus the peer `5%` exit.

## Regime backtest grid

Primary grid document: [`regime_backtest_grid_analysis.md`](regime_backtest_grid_analysis.md)

Test whether VIX-level, slope, and front-basis overlays improve `0.65` and `0.80` strategies after the stop-clipped threshold work:

- Ratios: `0.65`, `0.80`
- Baselines: entry `8%` / exit `5%`, and entry `8%` / exit `7%`
- Regime actions: block entry, force exit, or scale exposure to half
- Regime signals: VIX level, front slope, `VX1/VIX - 1` basis, and combinations

Initial read-through: VIX-level and slope overlays add little because the base rules already handle them. The useful incremental regime dimension is high `VX1/VIX` basis, especially for the `0.80` strategy.

## Regime conditioning

Analyze all distributions conditional on:

- VIX close buckets: <15, 15-20, 20-25, 25-30, 30+
- VIX 1-day / 5-day spike behavior
- Complete 9-maturity curve availability
- Calendar periods: pre-2008, GFC, 2012-2017 low-vol period, 2018 vol shock, COVID, 2022 tightening, post-2023

## Shape analysis

After the basic summary is stable:

- Normalize each curve by M1
- Cluster curve shapes
- Track transitions between clusters
- Measure forward returns of curve states
- Identify states that are friendly or hostile to carry

## Data quality checks

- Missing maturity counts by date
- Zero or suspicious settlements by contract sheet
- Volume and open-interest coverage
- Roll day behavior and discontinuities

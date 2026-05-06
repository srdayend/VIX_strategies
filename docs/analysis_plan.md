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

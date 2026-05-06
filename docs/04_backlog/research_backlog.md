# Research Backlog

This note groups the remaining work by research axis. It does not replace the original planning notes:

- [`data_analysis_plan.md`](data_analysis_plan.md)
- [`strategy_backtesting_plan.md`](strategy_backtesting_plan.md)

## Data Quality And Coverage

- Missing maturity counts by date
- Zero or suspicious settlements by contract sheet
- Volume and open-interest coverage
- Roll-day behavior and discontinuities
- Complete 9-maturity curve availability

## Term-Structure Analysis

- Distribution of M1-M9 settlements
- Daily changes and realized volatility by maturity rank
- Slope distributions: M2/M1, M4/M1, M7/M1, M9/M1
- Spread distributions: M2-M1, M4-M1, M7-M1
- Curve shape clustering after normalizing by M1
- State transitions between curve clusters

## Regime Analysis

- VIX close buckets: `<15`, `15-20`, `20-25`, `25-30`, `30+`
- VIX 1-day and 5-day spike behavior
- Calendar periods: pre-2008, GFC, 2012-2017 low-vol, 2018 vol shock, COVID, 2022 tightening, post-2023
- VX1/VIX basis thresholds: `5%`, `10%`, `15%`, and finer intermediate thresholds

## Strategy Robustness

- Stop slippage: `-2.25%`, `-2.50%`, `-3.00%`
- Close-only stop vs stop clipping vs stop slippage
- Fixed `0.65`, fixed `0.80`, and basis-aware dynamic ratio
- Volatility-scaled stops
- Exposure cooldown after large adverse moves

## Contract-Level Backtest

- Move beyond rank-based VX1/VX2 approximations
- Select actual front and deferred contracts each day
- Model roll windows
- Use volume and open-interest liquidity filters
- Apply roll-day transaction cost assumptions
- Compare contract-realistic results against rank-based prototypes

## Portfolio Sleeve Tests

- Test VIX strategy as a sleeve in a 60/40 SPY/IEF portfolio
- Compare fixed `0.65`, fixed `0.80`, and basis-aware overlays
- Check whether overlays improve portfolio efficiency or only reduce standalone volatility

# VIX Futures Calendar-Spread Research

**Can a short deferred VIX future, hedged with a long front future, earn roll-down carry without taking unacceptable volatility risk?**

This project grew out of my FIXERS derivatives research. I proposed a hedged VIX futures roll-down strategy, assembled contract-level source data, compared hedge ratios, and tested entry/exit rules and different market conditions. I also presented the work at an inter-club research session.

This repository continues a team research project. Python implementation was developed with AI coding tools; I led the research logic and analysis workflow.

## The position

```text
Position = r × VX1 − 1 × VX2
```

`VX1` is the front VIX future and `VX2` the second-month future. The short `VX2` leg seeks to benefit from a downward roll along the term structure, while the long `VX1` leg is intended to reduce sensitivity to volatility spikes.

The research question is not just which hedge ratio backtests best, but **what risk the ratio actually adds or removes**.

## Findings so far

- Around **0.65** is an initial hedge-ratio anchor based on the response of adjacent futures during VIX spikes.
- Around **0.70** emerged as a more defensible realized-PnL baseline in later daily-return analysis.
- A **0.80** hedge improved some backtest statistics, but its advantage was particularly sensitive to front-futures basis and volatility rebound days.
- Entry/exit timing, roll dates, stop assumptions, and contract-level trading costs can materially change the result.

### Illustrative historical backtest (not a live result)

| Hedge ratio | Model | Sharpe | Max drawdown |
|---|---|---:|---:|
| 0.65 | Daily-price, close-only stop | 1.100 | −12.06% |
| 0.80 | Daily-price, close-only stop | 1.400 | −11.08% |

These are historical model outputs, **not fully cost-adjusted executable returns**. The project has not yet established actual stop fills, complete transaction costs, open interest/capacity, or margin feasibility. A stop-clipped backtest is a scenario assumption, not proof of intraday execution.

## What I tested

- Hedge-ratio selection using adjacent-maturity VIX futures behavior.
- Term-structure slope and VIX-state filters.
- Fixed hedge ratios versus front-basis regimes.
- Entry and exit thresholds; rank-roll handling; sensitivity to stop assumptions.
- Return attribution by market regime and whether better results came from carry or additional front-volatility exposure.

## Repository navigation

- [`docs/00_research_summary.md`](docs/00_research_summary.md) — findings and limitations.
- [`docs/03_results/hedge_ratio_065_vs_080.md`](docs/03_results/hedge_ratio_065_vs_080.md) — comparison of alternative hedge ratios.
- [`docs/03_results/stop_loss_parameter_grid.md`](docs/03_results/stop_loss_parameter_grid.md) — stop-assumption sensitivity.
- [`src/vix_strategies/backtests/`](src/vix_strategies/backtests/) — backtesting logic.
- [`src/vix_strategies/experiments/`](src/vix_strategies/experiments/) — experiment scripts (source workbooks required).

## Running the code

```bash
pip install -r requirements.txt
python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios
```

The original third-party/CBOE-sourced Excel workbooks are **not included**. Set the appropriate data paths using the environment variables described in the [existing execution guide](docs/code_execution_guide.md). Full reproduction of reported results requires the same source datasets and preprocessing assumptions.

## Next work

Contract-expiry-aware testing; fuller transaction costs and roll/slippage modeling; more realistic stop fills; liquidity and margin checks; and a separated out-of-sample test.

**Research only. No claim of live profitability.**

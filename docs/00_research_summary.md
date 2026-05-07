# Research Summary

This is the first document to read. It summarizes the current state of the VIX calendar-spread research and points to the detailed notes.

## One-Line Conclusion

The strategy family is a hedged VIX futures calendar spread, `r * VX1 - VX2`. The original economic anchor is `r ~= 0.65`, but realized PnL-based sizing makes `0.70VX1 - VX2` the cleaner current baseline, with `0.80VX1 - VX2` kept as the stronger spike-hedge / high-Sharpe candidate.

## Strategy Definition

```text
Position = r * VX1 - 1.00 * VX2
front_slope = ln(VX2 / VX1)
```

Economic framing:

- Short `VX2` is the roll-down carry leg.
- Long `VX1` is the volatility-spike hedge.
- The main sizing question is how large `r` should be.

## Current Baseline Weight View

The latest baseline-weight study is [`03_results/vix_distribution_rolldown_hedge_ratio.md`](03_results/vix_distribution_rolldown_hedge_ratio.md).

Key findings:

- VIX spot spends most of its time in low-to-normal regimes and has a right-tail spike structure.
- The VIX futures front curve is usually in contango: `M2/M1` contango rate is about `82.9%`.
- Static roll-down premia alone allow a broad range of `r`, but they are not enough for trading-size decisions.
- Realized PnL testing is better:
  - Top 5% VIX spike-day median spread PnL turns non-negative around `r = 0.70`.
  - Top 5% VIX spike-day 25th percentile PnL turns non-negative around `r = 0.80`.
  - Carry-regime median daily return remains positive only up to about `r = 0.75`.

Working interpretation:

```text
0.65 = original shock-beta economic anchor
0.70 = current PnL-based baseline
0.80 = stronger spike hedge / high-Sharpe candidate
1.00+ = increasingly front-volatility-tilted research zone
```

## Existing Backtest View

The prior backtest work mostly compares `0.65VX1 - VX2` and `0.80VX1 - VX2`.

Under the same rank-based rules:

```text
Entry: front_slope > 8%
Exit: front_slope < 5% or 7%
VX1 cap: enter only when VX1 < 30; exit when VX1 > 30
Stop: -2%, tested as close-only and stop-clipped
Roll-day rule: avoid or exit on rank roll day
```

Main conclusions:

- `0.65` is the more defensible economic baseline.
- `0.80` earns its edge through stronger participation in right-tail VX1 rebound / spike-adjustment days.
- `0.80` is less attractive when VX1 is already expensive versus spot VIX.
- Stop-loss modeling materially changes the result and must be disclosed.

For entry `8%` / exit `5%`:

| Ratio | Stop style | CAGR | Sharpe | MDD | Worst day |
|---:|---|---:|---:|---:|---:|
| 0.65 | close-only | 11.13% | 1.100 | -12.06% | -10.54% |
| 0.65 | stop-clipped | 13.87% | 1.456 | -10.42% | -2.00% |
| 0.80 | close-only | 15.93% | 1.400 | -11.08% | -9.74% |
| 0.80 | stop-clipped | 18.17% | 1.658 | -9.87% | -2.00% |

## Regime And Basis View

The most useful additional quality signal is:

```text
front_basis = VX1 / VIX - 1
```

Why it matters:

- High basis means VX1 is expensive versus spot VIX.
- A larger VX1 long leg is less attractive in high-basis states.
- Basis filters improve the case for higher-ratio variants such as `0.80`.

Broad VIX-level overlays add less incremental value because the base rules already include front slope, VX1 cap, roll-day avoidance, and stop loss.

## Best Reading Path

1. [`03_results/vix_distribution_rolldown_hedge_ratio.md`](03_results/vix_distribution_rolldown_hedge_ratio.md) - latest baseline weight study.
2. [`02_strategy/peer_research_baseline.md`](02_strategy/peer_research_baseline.md) - peer strategy framing.
3. [`03_results/hedge_ratio_065_vs_080.md`](03_results/hedge_ratio_065_vs_080.md) - `0.65` versus `0.80` attribution.
4. [`03_results/stop_loss_parameter_grid.md`](03_results/stop_loss_parameter_grid.md) - entry/exit and stop-loss sensitivity.
5. [`03_results/regime_overlay_grid.md`](03_results/regime_overlay_grid.md) - regime overlay testing.
6. [`04_backlog/research_backlog.md`](04_backlog/research_backlog.md) - open robustness work.

## Next Research Steps

1. Run the main backtest around `r = 0.70` and compare against `0.65` and `0.80`.
2. Test basis-aware dynamic ratios, especially `0.70` baseline with `0.80` only in low-basis states.
3. Add stop slippage at `-2.25%`, `-2.50%`, and `-3.00%`.
4. Move beyond rank-based VX1/VX2 to contract-level testing.
5. Add transaction costs, roll mechanics, liquidity, open interest, and margin assumptions.

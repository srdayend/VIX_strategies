# Stop-Clipped Parameter Grid: `0.65` vs `0.80`

This note tests entry/exit threshold sensitivity for the two main hedge ratios after changing the stop-loss assumption.

## Stop-Loss Assumption

Previous implementation:

```text
If daily strategy return <= -2%, exit at that day's close.
The full close-to-close loss is still realized.
```

New implementation:

```text
If intraday strategy return reaches -2%, assume market stop execution at -2%.
Daily strategy return is clipped at -2%.
The position is then closed.
```

In code terms:

```text
ret = max(unclipped_ret, -2%) when held
```

This is more optimistic than close-only stop logic, but it is a useful scenario if the strategy can be monitored intraday and traded with market stops.

## Grid Setup

Fixed assumptions:

```text
Position: r * VX1 - VX2
r: 0.65 or 0.80
VX1 cap: 30
Roll-day avoidance: true
Stop: -2%, clipped
```

Grid:

```text
Entry slope: 6%, 7%, 8%, 9%, 10%, 11%, 12%
Exit slope: 3%, 4%, 5%, 6%, 7%
Constraint: exit < entry
Slope definition: ln(VX2 / VX1)
```

## Old Baseline vs Stop-Clipped Baseline

For the peer baseline `entry 8% / exit 5%`:

| Ratio | Stop style | CAGR | Ann. vol | Sharpe | MDD | Worst day | Stops |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.65 | close-only loss realization | 11.13% | 10.55% | 1.100 | -12.06% | -10.54% | 42 |
| 0.65 | stop-clipped at -2% | 13.87% | 9.66% | 1.456 | -10.42% | -2.00% | 42 |
| 0.80 | close-only loss realization | 15.93% | 11.53% | 1.400 | -11.08% | -9.74% | 33 |
| 0.80 | stop-clipped at -2% | 18.17% | 10.90% | 1.658 | -9.87% | -2.00% | 33 |

The stop clipping materially improves both ratios. It cuts the left tail, lowers volatility, improves drawdown, and raises Sharpe.

## Top Configurations by Sharpe

| Rank | Ratio | Entry | Exit | CAGR | Ann. vol | Sharpe | MDD | Exposure | Trades | Stops |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.80 | 8% | 7% | 18.10% | 10.54% | 1.704 | -9.87% | 36.52% | 257 | 28 |
| 2 | 0.80 | 9% | 7% | 17.55% | 10.35% | 1.687 | -9.87% | 31.67% | 210 | 25 |
| 3 | 0.80 | 7% | 6% | 18.42% | 10.92% | 1.674 | -9.87% | 44.62% | 267 | 30 |
| 4 | 0.80 | 8% | 6% | 17.96% | 10.68% | 1.673 | -9.87% | 39.32% | 220 | 29 |
| 5 | 0.80 | 6% | 5% | 19.39% | 11.50% | 1.670 | -10.14% | 51.45% | 296 | 36 |
| 6 | 0.80 | 9% | 6% | 17.41% | 10.45% | 1.659 | -9.87% | 33.66% | 191 | 25 |
| 7 | 0.80 | 8% | 5% | 18.17% | 10.90% | 1.658 | -9.87% | 40.69% | 209 | 33 |
| 8 | 0.80 | 9% | 5% | 17.70% | 10.66% | 1.653 | -9.87% | 34.67% | 187 | 29 |
| 9 | 0.80 | 7% | 5% | 18.39% | 11.17% | 1.638 | -9.87% | 46.37% | 245 | 34 |
| 10 | 0.80 | 9% | 4% | 17.46% | 10.74% | 1.622 | -11.67% | 35.22% | 185 | 33 |

The highest Sharpe region is not a single isolated point. For `0.80`, the neighborhood around entry `7-9%` and exit `5-7%` is broadly strong.

## Best `0.65` Configurations

| Rank | Ratio | Entry | Exit | CAGR | Ann. vol | Sharpe | MDD | Exposure | Trades | Stops |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.65 | 7% | 6% | 14.43% | 9.73% | 1.499 | -10.42% | 44.62% | 267 | 39 |
| 2 | 0.65 | 8% | 7% | 13.73% | 9.30% | 1.495 | -10.07% | 36.52% | 257 | 36 |
| 3 | 0.65 | 8% | 6% | 13.89% | 9.46% | 1.486 | -10.42% | 39.32% | 220 | 37 |
| 4 | 0.65 | 9% | 7% | 13.05% | 9.04% | 1.465 | -10.30% | 31.67% | 210 | 32 |
| 5 | 0.65 | 9% | 6% | 13.19% | 9.18% | 1.459 | -10.34% | 33.66% | 191 | 33 |
| 6 | 0.65 | 8% | 5% | 13.87% | 9.66% | 1.456 | -10.42% | 40.69% | 209 | 42 |

The `0.65` profile improves a lot under stop clipping, but it still does not catch the `0.80` profile.

## Sharpe Pivot: `0.65`

| Entry \ Exit | 3% | 4% | 5% | 6% | 7% |
|---:|---:|---:|---:|---:|---:|
| 6% | 1.322 | 1.389 | 1.449 |  |  |
| 7% | 1.298 | 1.371 | 1.445 | 1.499 |  |
| 8% | 1.348 | 1.408 | 1.456 | 1.486 | 1.495 |
| 9% | 1.339 | 1.400 | 1.422 | 1.459 | 1.465 |
| 10% | 1.282 | 1.323 | 1.348 | 1.374 | 1.331 |
| 11% | 1.214 | 1.244 | 1.270 | 1.278 | 1.240 |
| 12% | 1.137 | 1.171 | 1.209 | 1.248 | 1.220 |

## Sharpe Pivot: `0.80`

| Entry \ Exit | 3% | 4% | 5% | 6% | 7% |
|---:|---:|---:|---:|---:|---:|
| 6% | 1.553 | 1.608 | 1.670 |  |  |
| 7% | 1.507 | 1.562 | 1.638 | 1.674 |  |
| 8% | 1.562 | 1.615 | 1.658 | 1.673 | 1.704 |
| 9% | 1.568 | 1.622 | 1.653 | 1.659 | 1.687 |
| 10% | 1.554 | 1.589 | 1.615 | 1.619 | 1.580 |
| 11% | 1.550 | 1.569 | 1.599 | 1.589 | 1.546 |
| 12% | 1.484 | 1.508 | 1.540 | 1.560 | 1.539 |

## CAGR Pivot: `0.80`

| Entry \ Exit | 3% | 4% | 5% | 6% | 7% |
|---:|---:|---:|---:|---:|---:|
| 6% | 18.21% | 18.77% | 19.39% |  |  |
| 7% | 17.06% | 17.60% | 18.39% | 18.42% |  |
| 8% | 17.27% | 17.78% | 18.17% | 17.96% | 18.10% |
| 9% | 16.92% | 17.46% | 17.70% | 17.41% | 17.55% |
| 10% | 16.05% | 16.35% | 16.53% | 16.24% | 15.63% |
| 11% | 15.35% | 15.50% | 15.70% | 15.28% | 14.70% |
| 12% | 14.10% | 14.30% | 14.53% | 14.60% | 14.30% |

## Interpretation

### 1. Stop clipping changes the strategy profile materially

The close-only stop records the full close-to-close loss, which created very large worst days. The stop-clipped version caps daily losses at `-2%`, improving both ratios.

This is not just cosmetic. The strategy is highly sensitive to tail-loss treatment. Any final report should clearly disclose whether the stop is modeled as close-only or intraday market stop.

### 2. `0.80` remains dominant after stop clipping

Even after clipping losses for both strategies, `0.80` still dominates the top Sharpe table. The performance difference is not only a function of worse left-tail days in `0.65`; `0.80` continues to harvest more upside within the same trade windows.

### 3. The strongest threshold area is stable

For `0.80`, the best region is roughly:

```text
Entry: 7-9%
Exit: 5-7%
```

For `0.65`, the best region is similar but slightly lower-performing:

```text
Entry: 7-9%
Exit: 5-7%
```

The peer baseline `entry 8% / exit 5%` is not the absolute Sharpe-max point after stop clipping, but it remains inside a strong and defensible neighborhood.

### 4. Higher exit thresholds help Sharpe

Exit `6-7%` often improves Sharpe versus exit `5%`, because the strategy exits earlier when the curve starts weakening. The trade-off is lower exposure and sometimes slightly lower CAGR.

This suggests a cleaner interpretation:

```text
Entry should require steep contango.
Exit should happen before the curve fully decays.
```

Rather than waiting until `5%`, a `6-7%` exit may preserve quality.

## Working Recommendations

Use these as candidate sets for the next stage:

| Use case | Ratio | Entry | Exit | Why |
|---|---:|---:|---:|---|
| High-Sharpe candidate | 0.80 | 8% | 7% | Best Sharpe in the grid |
| Robust high-return candidate | 0.80 | 7% | 6% | High CAGR and high Sharpe, broader exposure |
| Peer-compatible benchmark | 0.80 | 8% | 5% | Same as peer baseline, improved by stop clipping |
| Economic-anchor candidate | 0.65 | 8% | 6-7% | Keeps shock-beta narrative, better Sharpe than 8/5 |
| Conservative candidate | 0.65 | 9% | 7% | Lower exposure, still strong Sharpe |

## Next Checks

Before treating stop-clipped results as final, test:

1. Slippage on stop execution: e.g. stop at `-2.25%` or `-2.50%` instead of exactly `-2%`.
2. Intraday feasibility: can the strategy be monitored and executed near the synthetic spread stop?
3. Contract-level backtest: rank-based VX1/VX2 can hide real roll and liquidity frictions.
4. Dynamic stop: compare fixed `-2%` with volatility-scaled stops.

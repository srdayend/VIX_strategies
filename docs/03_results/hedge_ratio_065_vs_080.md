# Hedge Ratio Deep Dive: `0.65VX1 - VX2` vs `0.80VX1 - VX2`

This note compares the economically anchored `0.65` hedge ratio against the peer package's highest-Sharpe `0.80` hedge ratio.

The goal is not just to identify which backtest line is higher. The goal is to understand what kind of risk premium each version is harvesting, where the performance gap appears, and whether the `0.80` version is still a hedged roll-down carry strategy or a front-VIX-tilted spread.

## Setup

Both strategies use the same rules. Only the VX1 hedge ratio changes.

```text
Position 0.65: 0.65 * VX1 - 1.00 * VX2
Position 0.80: 0.80 * VX1 - 1.00 * VX2

front_slope = ln(VX2 / VX1)

Entry: front_slope > 8%
Exit: front_slope < 5%
VX1 cap: enter only when VX1 < 30; exit when VX1 > 30
Stop: exit when daily strategy return <= -2%
Roll-day rule: avoid / exit on rank roll day
```

Daily return definition:

```text
ret[t] = (r * dVX1[t] - dVX2[t]) / (r * VX1[t-1] + VX2[t-1])
```

Regime attribution below uses the previous day's close state, because return on day `t` comes from the position held from `t-1 close` to `t close`.

## Headline Result

| Metric | `0.65VX1 - VX2` | `0.80VX1 - VX2` | Difference |
|---|---:|---:|---:|
| Total return | 929.1% | 2,523.6% | +1,594.5%p |
| CAGR | 11.13% | 15.93% | +4.81%p |
| Annual vol | 10.55% | 11.53% | +0.98%p |
| Sharpe | 1.100 | 1.400 | +0.300 |
| Max drawdown | -12.06% | -11.08% | +0.98%p |
| Worst day | -10.54% | -9.74% | +0.80%p |
| Exposure | 40.69% | 40.69% | 0.00%p |
| Trades | 209 | 209 | 0 |
| Stops | 42 | 33 | -9 |

The two strategies have the same exposure and trade count. The improvement is therefore not coming from more time in market; it comes from the altered daily payoff profile while in the same trade windows.

## Held-Day Distribution

| Quantile | `0.65` daily return | `0.80` daily return | `0.80 - 0.65` |
|---:|---:|---:|---:|
| 1% | -2.69% | -2.39% | -0.68% |
| 5% | -1.16% | -1.06% | -0.50% |
| 10% | -0.71% | -0.65% | -0.37% |
| 25% | -0.30% | -0.29% | -0.20% |
| 50% | 0.07% | 0.04% | -0.04% |
| 75% | 0.48% | 0.39% | 0.16% |
| 90% | 0.92% | 0.95% | 0.52% |
| 95% | 1.47% | 1.91% | 0.93% |
| 99% | 3.93% | 4.75% | 1.74% |

Interpretation:

- `0.80` is not better on the median day. Its median held-day edge is slightly worse.
- The edge comes from the right tail: top-decile and top-percentile days are materially better.
- The left tail is not worse in this sample. The 1% and 5% left-tail outcomes are actually less negative for `0.80`.

This is a very important profile: `0.80` earns its edge by increasing participation in positive VX1 convexity / front-vol rebound days, not by improving the ordinary median carry day.

## Regime Attribution

Regimes are based on previous close:

```text
Strong Carry: VIX < 15, slope >= 8%, basis < 10%
Normal Carry: VIX < 20, slope >= 3%, basis < 10%
High Basis Carry: VIX < 20, slope >= 8%, basis >= 10%
Low-quality Carry: VIX < 20, slope >= 3%, basis >= 10%
Transition: all other non-crisis states
Crisis / No Carry: VIX >= 30 or slope < 0
```

Only days when both strategies are held are shown.

| Regime | Held days | Avg return `0.65` | Avg return `0.80` | Sum diff `0.80-0.65` | Simple Sharpe `0.65` | Simple Sharpe `0.80` |
|---|---:|---:|---:|---:|---:|---:|
| Strong Carry | 635 | 0.154% | 0.245% | +57.67% | 2.21 | 2.92 |
| Normal Carry | 686 | 0.081% | 0.138% | +39.38% | 1.08 | 1.81 |
| Transition | 297 | 0.226% | 0.251% | +7.55% | 3.12 | 3.16 |
| High Basis Carry | 493 | 0.046% | 0.031% | -7.34% | 1.46 | 1.07 |
| Low-quality Carry | 50 | -0.149% | -0.167% | -0.85% | -3.65 | -5.24 |
| Crisis / No Carry | 2 | 4.570% | 4.519% | -0.10% | not meaningful | not meaningful |

Key read-through:

- `0.80` dominates in clean carry regimes, especially Strong Carry and Normal Carry.
- `0.80` underperforms when front basis is high. That is exactly where VX1 is expensive versus spot VIX, so the bigger VX1 long leg becomes a drag.
- The basis filter matters more after comparing `0.65` vs `0.80`. High-basis zones are where the high hedge ratio loses its quality.

## Basis Bucket Attribution

| Front basis bucket | Held days | Avg return `0.65` | Avg return `0.80` | Sum diff | Simple Sharpe `0.65` | Simple Sharpe `0.80` |
|---|---:|---:|---:|---:|---:|---:|
| `VX1/VIX - 1 < 0%` | 287 | 0.567% | 0.850% | +81.25% | 4.54 | 5.94 |
| `0-5%` | 609 | 0.104% | 0.162% | +35.34% | 1.50 | 2.27 |
| `5-10%` | 690 | 0.015% | -0.006% | -14.21% | 0.39 | -0.16 |
| `>=10%` | 577 | 0.014% | 0.004% | -6.09% | 0.43 | 0.12 |

This is the cleanest explanation of the performance gap.

`0.80` is powerful when VX1 is not expensive versus spot VIX. When VX1 is discounted or only modestly premium to VIX, the bigger VX1 leg captures rebounds and improves the spread. When VX1 is already 5%+ above VIX, the extra VX1 long becomes much less attractive.

## Slope Bucket Attribution

| Slope bucket | Held days | Avg return `0.65` | Avg return `0.80` | Sum diff | Simple Sharpe `0.65` | Simple Sharpe `0.80` |
|---|---:|---:|---:|---:|---:|---:|
| `3-8%` | 368 | -0.077% | -0.068% | +3.31% | -1.14 | -1.05 |
| `>=8%` | 1,796 | 0.152% | 0.204% | +92.45% | 2.35 | 2.82 |

Because the entry rule is slope > 8%, most held days naturally come from the `>=8%` bucket. The `3-8%` bucket mostly appears after entry while waiting for exit at 5%. That zone is weak for both versions.

## Yearly Attribution

Top years where `0.80` added the most simple return over `0.65`:

| Year | Sum return `0.65` | Sum return `0.80` | Difference |
|---:|---:|---:|---:|
| 2024 | 2.34% | 13.54% | +11.19% |
| 2021 | 14.79% | 25.20% | +10.41% |
| 2019 | 9.63% | 16.30% | +6.66% |
| 2016 | 6.70% | 12.68% | +5.98% |
| 2007 | 15.67% | 21.55% | +5.88% |
| 2014 | 14.71% | 20.32% | +5.61% |
| 2023 | 12.54% | 18.04% | +5.50% |
| 2013 | 17.52% | 22.76% | +5.24% |

Years where `0.80` failed to add value:

| Year | Sum return `0.65` | Sum return `0.80` | Difference |
|---:|---:|---:|---:|
| 2012 | 14.16% | 13.58% | -0.58% |
| 2010 | 13.82% | 13.48% | -0.34% |
| 2011 | 17.46% | 18.32% | +0.86% |

The relative performance edge is persistent across many years rather than isolated to one crisis. But the edge is not monotonic: 2010 and 2012 are examples where `0.65` was slightly better.

## What Actually Drives the Difference?

Correlation diagnostics on held days:

| Variable | Corr with `0.80 - 0.65` |
|---|---:|
| `dVX1` | 0.779 |
| `dVX2` | 0.687 |
| prior front slope | 0.204 |
| prior front basis | -0.210 |
| prior VIX level | -0.021 |

This is the core mechanical explanation:

- The `0.80` strategy benefits when VX1 rises relative to the denominator-adjusted spread exposure.
- The edge is strongly related to `dVX1`, meaning the higher hedge ratio is effectively buying more front-vol upside.
- Prior front basis is negatively related to the edge. High VX1 premium makes the bigger VX1 leg less useful.
- VIX level alone does not explain much of the `0.80` edge; basis and actual VX1 movement matter more.

## Interpretation

The `0.80` version should not be dismissed just because it has a stronger VX1 long tilt. The comparison shows that it is not merely taking more volatility. It improves the right tail, reduces stop count, and does not worsen max drawdown in this sample.

However, it is also not a pure carry ratio. The performance gap is mostly explained by the larger VX1 long leg helping on front-vol rebound / shock-adjustment days. That means the right framing is:

```text
0.65 = shock-beta anchored hedged carry baseline
0.80 = high-Sharpe front-vol-tilted hedged carry variant
```

The two are both useful, but they answer different questions.

## Research Takeaways

1. Keep both ratios in the research set.
2. Use `0.65` as the defensible economic anchor because spike-day median `dVX2/dVX1` is about `0.653`.
3. Use `0.80` as the empirical high-Sharpe benchmark.
4. Add `front_basis = VX1 / VIX - 1` as a required quality filter for the high-ratio strategy.
5. Test whether `0.80` with a basis filter dominates `0.65` without changing the strategy narrative too much.

## Next Tests

The most natural next experiment is:

```text
Base rule:
  entry ln(VX2/VX1) > 8%
  exit ln(VX2/VX1) < 5%
  VX1 < 30
  stop -2%
  roll-day avoidance

Compare:
  0.65 fixed
  0.80 fixed
  0.80 only when front_basis < 5%, otherwise 0.65
  0.80 only when front_basis < 10%, otherwise 0.65
  0.80 only when VIX < 20 and basis < 5%, otherwise 0.65
```

The hypothesis is that a basis-aware dynamic ratio may capture much of the `0.80` upside while avoiding high-basis zones where it underperforms.

# Baseline Weight Study For The VIX Calendar Spread

## Purpose

The strategy backbone is a VIX futures calendar spread:

```text
Position = r * VX1 - 1.00 * VX2
```

The trade shorts the deferred future and buys the front future. The short VX2 leg is intended to harvest roll-down carry when the VIX futures curve is in contango. The long VX1 leg is intended to hedge volatility spike risk because the front future reacts more strongly to shocks.

The key question is not whether the trade should be a calendar spread. The key question is whether a simple `1.00VX1 - 1.00VX2` spread is the right expression. A one-for-one spread may overpay for the hedge in normal carry regimes, while a too-small VX1 long may leave the strategy exposed during VIX spikes. This note is the baseline sizing study for choosing `r`.

The study uses three building blocks:

1. VIX spot distribution: does VIX usually stay low and occasionally spike?
2. VIX futures term structure: how often does the curve offer contango carry?
3. Roll-down and spike response: how much VX1 is needed to preserve carry while hedging VX2 shock exposure?

All roll-down percentages below are **spread premia at a point in time**, not one-day returns. For example, `M2/M1 - 1 = 5.75%` means VX2 is 5.75% above VX1 on average, not that the strategy earns 5.75% per day.

## Data And Outputs

Source data comes from the local Excel files documented in `docs/01_data/source_data_inventory.md`.

Generated files:

```text
reports/generated/vix_distribution_rolldown_hedge_ratio/
  vix_spot_distribution_stats.csv
  vix_spot_bucket_distribution.csv
  vix_spot_percentile_curve.csv
  vix_spike_structure_summary.csv
  term_structure_contango_backwardation_summary.csv
  adjacent_maturity_rolldown_summary.csv
  front_carry_by_hedge_ratio.csv
  vix_spike_hedge_ratio_summary.csv
  advanced_pnl_weight_grid.csv
  advanced_pnl_weight_summary.csv
```

The script also regenerates local PNG charts with no background gridlines, labeled axes, and NanumSquare when the font is available.

## 1. VIX Spot: Low Base, Right-Tail Spikes

VIX spot is not normally distributed around a stable mean. It spends most of its time in low-to-normal volatility states and occasionally jumps into a high-volatility right tail.

| Sample | Start | End | Days | Mean | Median | P75 | P95 | <15 | 15-20 | 20-30 | 30+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Historical | 1990-01-02 | 2026-05-05 | 9,178 | 19.46 | 17.62 | 22.74 | 32.95 | 32.23% | 30.40% | 29.34% | 8.03% |
| Latest 3Y | 2023-05-05 | 2026-05-05 | 774 | 17.13 | 16.29 | 18.60 | 24.89 | 35.01% | 47.93% | 15.12% | 1.94% |

The percentile curve is the more useful presentation chart than a simple bucket chart. It shows that most of the curve is low and gently rising, then the upper tail steepens quickly. That is exactly the structure a VIX carry strategy has to solve: long normal periods where carry matters, interrupted by a small number of large right-tail shocks.

Additional spike-shape diagnostics:

| Metric | Days | Median | Mean | P75 | P90 | P95 | P99 | Max | Key share 1 | Key share 2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VIX close | 9,178 | 17.62 | 19.46 | 22.74 | 28.58 | 32.95 | 46.74 | 82.69 | <20: 62.63% | >=40: 2.27% |
| Daily VIX change | 9,177 | -0.07 | 0.00 | 0.57 | 1.48 | 2.34 | 5.02 | 24.86 | >=3pt: 3.15% | >=5pt: 1.01% |

Read-through:

- VIX closes below `20` on about `62.6%` of historical days.
- VIX closes above `30` on only `8.0%` of historical days, and above `40` on only `2.3%`.
- Daily VIX changes have a small median move but a large right tail: top 1% up-days are `5pt+`.

This supports the basic trade design. Most days are potential carry-regime days, but the strategy must explicitly survive rare volatility spikes.

## 2. VIX Futures: Contango Is The Usual State

The carry premise requires the VIX futures curve to spend enough time in contango. This is true whether we measure the front pair, wider M1-based slopes, or log slopes.

| Curve measure | Days | Contango rate | Backwardation rate | Mean pct slope | Median pct slope | Mean log slope | Median log slope |
|---|---:|---:|---:|---:|---:|---:|---:|
| M2/M1 | 5,318 | 82.87% | 16.66% | 5.75% | 6.40% | 5.38% | 6.20% |
| M3/M1 | 5,318 | 83.19% | 16.62% | 9.56% | 10.81% | 8.65% | 10.27% |
| M4/M1 | 5,287 | 83.28% | 16.59% | 12.28% | 13.60% | 10.85% | 12.75% |
| M6/M1 | 4,684 | 81.21% | 18.53% | 14.86% | 16.19% | 12.70% | 15.00% |
| M9/M1 | 3,554 | 82.02% | 17.98% | 19.37% | 20.90% | 15.96% | 18.98% |
| All adjacent M1-M9 | 3,554 | 45.58% | 3.07% | n/a | n/a | n/a | n/a |

Two details matter for strategy design:

- `M2/M1` is already in contango about `82.9%` of the time, so the front calendar spread has a strong structural carry premise.
- Full-curve contango across all adjacent pairs is lower, about `45.6%`, which means the curve is often uneven. The front spread should be analyzed directly rather than assuming the entire curve is always smoothly upward sloping.

## 3. Roll-Down Premium: Carry Budget For The Spread

For `r * VX1 - VX2`, the relevant roll-down comparison is not only `M2->M1`. The long VX1 leg also has a roll-down cost as VX1 converges toward spot VIX.

```text
Long VX1 cost proxy = M1 / VIX - 1
Short VX2 gain proxy = M2 / M1 - 1
```

| Roll-down pair | Days | Mean premium | Median premium | Positive premium rate | P25 | P75 |
|---|---:|---:|---:|---:|---:|---:|
| M1->VIX | 5,316 | 4.11% | 3.78% | 74.74% | -0.03% | 8.44% |
| M2->M1 | 5,318 | 5.75% | 6.40% | 82.87% | 1.99% | 9.99% |
| M3->M2 | 5,318 | 3.41% | 3.80% | 81.27% | 0.98% | 6.19% |
| M4->M3 | 5,287 | 2.30% | 2.47% | 80.52% | 0.56% | 4.25% |
| M5->M4 | 4,762 | 1.58% | 1.59% | 77.68% | 0.27% | 3.07% |
| M6->M5 | 4,684 | 1.29% | 1.23% | 75.62% | 0.08% | 2.47% |
| M7->M6 | 4,671 | 1.12% | 1.01% | 76.92% | 0.15% | 2.16% |
| M8->M7 | 4,368 | 0.80% | 0.69% | 71.59% | -0.11% | 1.64% |
| M9->M8 | 3,554 | 0.76% | 0.78% | 70.88% | 0.00% | 1.69% |

The front spread has a carry budget:

- Short VX2 earns `M2->M1` premium of about `5.75%` on average.
- Long VX1 pays `M1->VIX` premium of about `4.11%` on average per `1.00` unit of VX1.
- The mean curve-only break-even ratio is about `1.40` because `5.75% / 4.11% = 1.40`.

This means roll-down carry does not force the hedge ratio to be small. Even a one-for-one spread has positive average front roll-down premium in this simplified rank-based measure. The weight decision should therefore be driven mainly by spike hedge adequacy and by whether extra VX1 exposure is worth holding.

## 4. Net Roll-Down Premium By VX1 Weight

| VX1 ratio per short VX2 | Mean short VX2 premium | Mean long VX1 cost | Mean net premium | Median short VX2 premium | Median long VX1 cost | Median net premium |
|---:|---:|---:|---:|---:|---:|---:|
| 0.45 | 5.75% | 1.85% | 3.90% | 6.40% | 1.70% | 4.70% |
| 0.60 | 5.75% | 2.47% | 3.29% | 6.40% | 2.27% | 4.13% |
| 0.65 | 5.75% | 2.67% | 3.08% | 6.40% | 2.46% | 3.94% |
| 0.70 | 5.75% | 2.88% | 2.88% | 6.40% | 2.64% | 3.75% |
| 0.75 | 5.75% | 3.08% | 2.67% | 6.40% | 2.83% | 3.56% |
| 0.80 | 5.75% | 3.29% | 2.46% | 6.40% | 3.02% | 3.37% |
| 1.00 | 5.75% | 4.11% | 1.64% | 6.40% | 3.78% | 2.62% |

This table is a carry feasibility check, not a full expected-return estimate. It says:

- `0.65`, `0.70`, and `0.80` all preserve positive net front roll-down premium.
- `0.80` is not disqualified by roll-down cost alone.
- The cost of increasing VX1 from `0.65` to `0.80` is a reduction in average net roll-down premium from `3.08%` to `2.46%`.

So the next constraint is not carry. The next constraint is spike protection.

## 5. Spike Hedge Requirement

On VIX spike days, VX1 should move more than VX2. The hedge ratio that neutralizes a short VX2 shock is approximately:

```text
Required VX1 ratio = dVX2 / dVX1
```

| VIX spike definition | dVIX cutoff | Days | Days with dVX1 > 0 | Median dVIX | Median dVX1 | Median dVX2 | Median dVX2/dVX1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top 5.0% VIX up days | 2.6530 | 266 | 260 | 3.86 | 2.57 | 1.80 | 0.686 |
| Top 2.5% VIX up days | 3.8515 | 133 | 130 | 5.47 | 3.70 | 2.45 | 0.676 |
| Top 1.0% VIX up days | 5.9558 | 54 | 52 | 8.21 | 5.11 | 3.68 | 0.652 |
| Top 0.5% VIX up days | 8.2059 | 27 | 26 | 12.52 | 7.24 | 4.50 | 0.721 |

The spike hedge estimate lands in the `0.65-0.70` zone. This also matches the earlier peer-research result based on VX1 spike days, where median `dVX2 / dVX1` was about `0.653`.

## Weight Range Interpretation

The same spread can be framed in two directions.

### Carry-Adjusted Calendar Spread

This is the conservative baseline framing:

```text
Primary return path = VX2 short roll-down carry
Adjustment = buy VX1 to offset spike risk
```

In this view, the minimum acceptable `r` is set by spike hedge adequacy. On VIX spike days, median `dVX2 / dVX1` is about `0.65-0.70`, so `r` should not be much below that range if the strategy wants to remain a hedged calendar spread rather than a mostly short-volatility carry trade.

```text
Carry-adjusted lower bound: r ~= 0.65-0.70
```

### Spike-Adjusted VIX Long

This is the more aggressive/front-vol framing:

```text
Primary return path = long VX1 participation in volatility spikes
Adjustment = short VX2 to offset VX1 roll-down cost
```

In this view, `r` can be above `1.00`. The upper bound is set by how much VX1 roll-down cost can be financed by the short VX2 leg.

Using mean roll-down premia:

```text
Short VX2 roll-down premium = 5.75%
Long VX1 roll-down cost = 4.11%
Mean roll-cost-neutral r = 5.75% / 4.11% = 1.40
```

Using median roll-down premia:

```text
Short VX2 roll-down premium = 6.40%
Long VX1 roll-down cost = 3.78%
Median roll-cost-neutral r = 6.40% / 3.78% = 1.69
```

The cleaner research upper bound is the mean estimate, `r ~= 1.40`, with the median estimate, `r ~= 1.69`, treated as an optimistic sensitivity. Above that zone, the position is no longer financed by the front calendar roll-down in this simplified measure; it becomes a more outright long-front-volatility trade.

```text
Spike-adjusted upper bound: r ~= 1.40, with 1.69 as optimistic sensitivity
```

## More Rigorous PnL-Based Sizing

The previous sections are useful for building intuition, but they are still only first-order diagnostics.

Two limitations matter:

1. `dVX2 / dVX1` on spike days is a shock-beta estimate. It says how many VX1 points are needed to offset VX2 points on that subset, but it does not directly show the realized distribution of a held position.
2. Static roll-down premium, such as `M2/M1 - 1`, is a curve snapshot. It is not a one-day return and should not be mechanically converted into a trading weight without checking realized daily PnL.

The better sizing check is to evaluate the actual daily point PnL of the proposed spread:

```text
Point PnL[t] = r * dVX1[t] - dVX2[t]
Return[t] = Point PnL[t] / (r * VX1[t-1] + VX2[t-1])
```

Then choose `r` by asking two separate questions:

```text
Spike hedge test:
  On VIX spike days, how large must r be for Point PnL to be non-negative?

Carry regime test:
  On normal contango days, how large can r be before realized carry-regime returns decay too much?
```

Definitions used here:

- Spike days: top 5%, 2.5%, and 1% VIX spot up-days.
- Carry-regime days: previous-day `M2/M1 > 0`, previous-day VIX below `30`, excluding top 5% VIX up-days.

| PnL-based sizing criterion | Implied r |
|---|---:|
| Top 5% spike-day median PnL >= 0 | 0.700 |
| Top 5% spike-day 25th percentile PnL >= 0 | 0.800 |
| Top 2.5% spike-day median PnL >= 0 | 0.700 |
| Top 1% spike-day median PnL >= 0 | 0.675 |
| Carry-regime mean daily return remains positive | up to 1.325 |
| Carry-regime median daily return remains positive | up to 0.750 |

Selected grid points:

| r | Carry mean daily return | Carry median daily return | Carry positive-day rate | Top 5% spike median point PnL | Top 5% spike P25 point PnL |
|---:|---:|---:|---:|---:|---:|
| 0.65 | 0.053% | 0.040% | 53.00% | -0.091 | -0.368 |
| 0.70 | 0.048% | 0.019% | 51.15% | 0.023 | -0.220 |
| 0.80 | 0.038% | -0.024% | 47.96% | 0.271 | 0.068 |
| 1.325 | 0.001% | -0.153% | 42.23% | 1.639 | 1.161 |

This improves the conclusion:

- The simple spike-beta method was directionally right, but slightly too loose around `0.65`. In actual spike-day PnL, `r = 0.70` is the cleaner median-neutral hedge.
- If the goal is to avoid losses on the lower quartile of top 5% spike days, `r = 0.80` is the stronger hedge threshold.
- The static roll premium method is too optimistic as a trading upper bound. Mean carry-regime return can stay positive up to about `1.325`, but the median carry-regime return turns negative after about `0.75`.
- Therefore, `r > 1.00` is feasible only under a spike-adjusted VIX-long framing. It is not a clean carry-adjusted baseline.

## Baseline Weighting Decision

The evidence points to this hierarchy:

```text
Core strategy: short VX2 roll-down carry + long VX1 spike hedge
Static carry feasibility: 0.65-1.40 is possible on roll premium alone
Realized PnL feasibility: 0.70-0.80 is the most useful hedge/carry zone
```

Recommended baseline:

```text
0.70VX1 - 1.00VX2
```

Interpretation:

- `0.65` is the original economic anchor because it is close to observed spike beta.
- `0.70` is the cleaner PnL-based baseline because it makes top 5% spike-day median spread PnL roughly neutral.
- `0.80` is a stronger hedge candidate because it also protects the lower quartile of top 5% spike days, but it starts to erode the median carry-regime day.
- `1.00` is not impossible from a roll-down standpoint, but it is no longer a partial hedge; it becomes a much more front-vol-heavy spread.
- The broad theoretical research range is `r ~= 0.65-1.40`, but the practical baseline research zone is `r ~= 0.70-0.80`.

For presentation purposes, this note should be treated as the first principles bridge:

```text
VIX has a low-base / spike-tail structure.
VIX futures are usually in contango.
The calendar spread harvests VX2 roll-down while VX1 hedges spikes.
Carry-adjusted framing gives the lower bound near 0.65-0.70.
Spike-adjusted framing gives the upper bound near 1.40.
Actual PnL testing tightens the practical baseline to 0.70-0.80.
Therefore 0.70VX1 - VX2 is the cleaner baseline expression, 0.65 is the economic anchor, and 0.80 is the stronger hedge candidate.
```

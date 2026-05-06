# VIX Regime Framework

This note defines the first simple, interpretable regime framework for the data-analysis phase.

The goal is not to optimize a strategy yet. The goal is to separate market states in a way that is economically logical, easy to audit, and aligned with the observed data.

## Two core axes

### 1. VIX index level

The VIX index level captures the current absolute stress level in the market.

Observed quantiles from the current merged VIX futures / VIX index dataset:

| Metric | VIX level |
|---|---:|
| 10% | 11.98 |
| 25% | 13.43 |
| 50% | 16.48 |
| 75% | 21.57 |
| 90% | 28.04 |
| 95% | 33.95 |

Recommended level buckets:

| Bucket | Rule | Interpretation |
|---|---|---|
| Low vol | `VIX < 15` | calm market |
| Normal | `15 <= VIX < 20` | normal volatility |
| Stress | `20 <= VIX < 30` | elevated stress |
| Crisis | `VIX >= 30` | shock / crisis zone |

These thresholds are intentionally simple. `15`, `20`, and `30` are easy to interpret and line up well with the empirical distribution.

### 2. Front VIX futures slope

Use the percentage slope between M1 and M2:

```text
front_slope = M2 / M1 - 1
```

This is preferred over a raw point spread because it is scale-aware.

Observed quantiles:

| Quantile | `M2 / M1 - 1` |
|---|---:|
| 10% | -2.37% |
| 25% | 1.99% |
| 33% | 3.55% |
| 50% | 6.40% |
| 66% | 8.48% |
| 75% | 9.99% |
| 90% | 13.42% |

Recommended slope buckets:

| Bucket | Rule | Interpretation |
|---|---|---|
| Backwardation | `front_slope < 0%` | stress / no-carry state |
| Flat or weak contango | `0% <= front_slope < 3%` | weak carry, transition risk |
| Normal contango | `3% <= front_slope < 8%` | ordinary carry zone |
| Steep contango | `front_slope >= 8%` | strong carry zone, usually calm market |

`0%` is economically meaningful because it separates contango from backwardation. `3%` is near the lower third of the sample and separates weak contango from meaningful contango. `8%` is near the upper third and works as a simple steep-contango threshold.

## Empirical cross-check

Observed behavior by VIX bucket:

| VIX bucket | Days | Contango rate | Avg front slope | Median front slope |
|---|---:|---:|---:|---:|
| `<15` | 2,041 | 99.1% | 9.00% | 8.26% |
| `15-20` | 1,633 | 88.9% | 6.38% | 6.22% |
| `20-25` | 819 | 72.4% | 4.18% | 4.55% |
| `25-30` | 394 | 63.2% | 1.41% | 1.65% |
| `30+` | 429 | 20.8% | -5.08% | -3.59% |

This supports using both axes together. VIX level alone misses whether the curve has already normalized; slope alone misses whether the market is in a dangerous high-stress state.

## First regime map

| Regime | Rule | Interpretation | Strategy stance |
|---|---|---|---|
| Strong Carry | `VIX < 15` and `front_slope >= 8%` | low-vol market with steep contango | carry-friendly, but monitor complacency |
| Normal Carry | `VIX < 20` and `front_slope >= 3%` | normal market with usable contango | carry allowed |
| Transition | `20 <= VIX < 30` or `0% <= front_slope < 3%` | elevated stress or weak curve support | reduce size, require stronger filters |
| Crisis / No Carry | `VIX >= 30` or `front_slope < 0%` | shock or backwardation | avoid short-front carry; hedge-only or flat |

## Simple trading-state rule

Initial rule for analysis and backtest segmentation:

```text
Carry ON:
  VIX < 20
  and front_slope >= 3%

Carry HALF / selective:
  20 <= VIX < 30
  and front_slope >= 8%

Carry OFF:
  VIX >= 30
  or front_slope < 0%
```

This is the first baseline regime framework. Future work should compare strategy results by these regimes before tuning individual strategy parameters.

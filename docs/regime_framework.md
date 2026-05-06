# VIX Regime Framework

This note defines the first simple, interpretable regime framework for the data-analysis phase.

The goal is not to optimize a strategy yet. The goal is to separate market states in a way that is economically logical, easy to audit, and aligned with the observed data.

## Core axes

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

### 3. M1 versus VIX spot basis

Front slope alone can overstate carry quality. A high `M2/M1` slope is useful, but if M1 itself is already far above the VIX index, part of the apparent carry can be a spot/front premium that may work against the position.

Use:

```text
front_basis = M1 / VIX - 1
```

Interpretation:

- Positive `front_basis`: M1 trades above spot VIX. For short-front carry, this can be acceptable when modest, but a large premium means the front future may already embed a lot of expected spot normalization.
- Negative `front_basis`: M1 trades below spot VIX. This often appears in stressed markets or after VIX spikes; it can coincide with backwardation and different risk dynamics.

Observed quantiles:

| Quantile | `M1 / VIX - 1` |
|---|---:|
| 10% | -3.73% |
| 25% | -0.03% |
| 50% | 3.78% |
| 66% | 6.53% |
| 75% | 8.44% |
| 80% | 9.77% |
| 90% | 13.14% |
| 95% | 16.23% |

Recommended basis buckets:

| Bucket | Rule | Interpretation |
|---|---|---|
| Discount | `front_basis < 0%` | M1 below spot; often stress-normalization state |
| Fair / modest premium | `0% <= front_basis < 5%` | cleanest carry quality zone |
| Elevated premium | `5% <= front_basis < 10%` | carry allowed but less attractive |
| Expensive front | `front_basis >= 10%` | apparent slope may be partly offset by spot/front premium |

In the initial Carry ON universe (`VIX < 20` and `front_slope >= 3%`), the basis breakdown was:

| Basis bucket | Days | Avg front slope | Avg basis | Avg net carry proxy |
|---|---:|---:|---:|---:|
| M1 discount >5% | 42 | 13.49% | -7.74% | 13.49% |
| M1 discount 0-5% | 302 | 9.90% | -1.57% | 9.90% |
| M1 premium 0-5% | 899 | 8.94% | 2.61% | 6.32% |
| M1 premium 5-10% | 939 | 9.23% | 7.32% | 1.91% |
| M1 premium 10-20% | 798 | 9.46% | 13.70% | -4.24% |
| M1 premium 20%+ | 73 | 9.96% | 23.27% | -13.31% |

The rough proxy used here is:

```text
net_carry_proxy = front_slope - max(front_basis, 0)
```

This is not a final PnL formula. It is a diagnostic to avoid calling a curve carry-friendly when the M1/spot premium is already too expensive.

## Empirical cross-check

Observed behavior by VIX bucket:

| VIX bucket | Days | Contango rate | Avg front slope | Median front slope |
|---|---:|---:|---:|---:|
| `<15` | 2,041 | 99.1% | 9.00% | 8.26% |
| `15-20` | 1,633 | 88.9% | 6.38% | 6.22% |
| `20-25` | 819 | 72.4% | 4.18% | 4.55% |
| `25-30` | 394 | 63.2% | 1.41% | 1.65% |
| `30+` | 429 | 20.8% | -5.08% | -3.59% |

This supports using VIX level and slope together. VIX level alone misses whether the curve has already normalized; slope alone misses whether the market is in a dangerous high-stress state. The M1/spot basis is a quality filter layered on top of the carry regime.

## First regime map

| Regime | Rule | Interpretation | Strategy stance |
|---|---|---|---|
| Strong Carry | `VIX < 15`, `front_slope >= 8%`, and `front_basis < 10%` | low-vol market with steep contango and acceptable M1 premium | carry-friendly, but monitor complacency |
| Normal Carry | `VIX < 20`, `front_slope >= 3%`, and `front_basis < 10%` | normal market with usable contango and no excessive front premium | carry allowed |
| Low-Quality Carry | `VIX < 20`, `front_slope >= 3%`, and `front_basis >= 10%` | curve looks steep, but M1 is expensive versus spot | reduce size or require additional confirmation |
| Transition | `20 <= VIX < 30` or `0% <= front_slope < 3%` | elevated stress or weak curve support | reduce size, require stronger filters |
| Crisis / No Carry | `VIX >= 30` or `front_slope < 0%` | shock or backwardation | avoid short-front carry; hedge-only or flat |

## Simple trading-state rule

Initial rule for analysis and backtest segmentation:

```text
Carry ON:
  VIX < 20
  and front_slope >= 3%
  and front_basis < 10%

Carry HALF / selective:
  20 <= VIX < 30
  and front_slope >= 8%
  and front_basis < 5%

Low-quality Carry:
  VIX < 20
  and front_slope >= 3%
  and front_basis >= 10%

Carry OFF:
  VIX >= 30
  or front_slope < 0%
```

This is the first baseline regime framework. Future work should compare strategy results by these regimes before tuning individual strategy parameters.

# Peer Research One-Page Summary

This page summarizes the peer research package from `VIX_strategy_0506_조의현.docx` and `VIX.zip`.

## Core Idea

The strategy uses the VIX futures front term structure to build a hedged roll-down carry trade:

```text
Position = r * VX1 - 1.00 * VX2
front_slope = ln(VX2 / VX1)
```

Economic intuition:

- Short `VX2` seeks roll-down carry when the VIX curve is in contango.
- Long `VX1` hedges volatility spike risk because VX1 reacts more strongly to shocks than VX2.
- The trade is not pure short volatility; it is a front-spread carry trade with a long-front hedge.

## Base Trading Rules

The peer baseline uses:

```text
Entry: front_slope > 8%
Exit: front_slope < 5%
VX1 cap: enter only when VX1 < 30; exit when VX1 > 30
Stop: close if daily strategy return <= -2%
Roll-day rule: avoid / exit on rank roll day
```

Return definition:

```text
ret[t] = (r * dVX1[t] - dVX2[t]) / (r * VX1[t-1] + VX2[t-1])
```

## Main Profiles

| Profile | Position | Rules | CAGR | Ann. vol | Sharpe | MDD | Exposure |
|---|---|---|---:|---:|---:|---:|---:|
| Conservative | `0.65VX1 - VX2` | Entry 7%, Exit 5%, VX1 cap 25 | 10.22% | 10.53% | 1.020 | -14.64% | 44.28% |
| Balanced | `0.60VX1 - VX2` | Entry 8%, Exit 5%, VX1 cap 30, Stop -2% | 9.28% | 10.66% | 0.925 | -15.14% | 40.64% |
| Aggressive | `0.45VX1 - VX2` | Entry 8%, Exit 5%, VX1 cap 30, Stop -2% | 3.68% | 12.69% | 0.362 | -27.44% | 40.47% |

The labels are important: `0.45` is aggressive because it has less VX1 long hedge and therefore leaves more VX2 short risk exposed.

## Hedge Ratio Logic

The strongest conceptual contribution is the `0.65` hedge ratio rationale.

On VX1 spike days, defined as top 5% daily VX1 point changes:

| Metric | Value |
|---|---:|
| VX1 spike threshold | 3.35pt |
| Spike days | 114 |
| Mean `dVX2 / dVX1` | 0.629 |
| Median `dVX2 / dVX1` | 0.653 |

Interpretation:

```text
When VX1 rises by 1 point on spike days, VX2 rises by about 0.65 points at the median.
```

Therefore `0.65VX1 - VX2` is not an arbitrary backtest parameter. It is a shock-beta anchored hedge ratio.

## Same-Condition Hedge Ratio Scan

Holding the same rules fixed:

```text
Entry 8%, Exit 5%, VX1 cap 30, Stop -2%, roll-day avoidance
```

| Ratio | CAGR | Sharpe | MDD | Worst day | Stops |
|---:|---:|---:|---:|---:|---:|
| 0.45 | 3.68% | 0.362 | -27.44% | -11.85% | 93 |
| 0.60 | 9.28% | 0.925 | -15.14% | -10.84% | 52 |
| 0.65 | 11.13% | 1.100 | -12.06% | -10.54% | 42 |
| 0.70 | 12.82% | 1.235 | -10.97% | -10.26% | 37 |
| 0.75 | 14.42% | 1.333 | -10.00% | -10.00% | 35 |
| 0.80 | 15.93% | 1.400 | -11.08% | -9.74% | 33 |

The `0.80` version is the empirical highest-Sharpe benchmark. However, the peer research avoids making it the main economic anchor because a higher VX1 long leg makes the strategy more front-volatility tilted.

## Regime Add-Ons

The peer package tested dynamic risk/regime add-ons using:

- VX1 spike signals
- front slope break signals
- 252-day rolling slope percentile signals

Two structures were tested:

```text
1. Dynamic hedge ratio switch
2. Regime overlay: no-entry, half-size, or forced exit
```

Conclusion:

- Dynamic hedge switching did not add much because the base entry/exit/VX1 cap/stop rules already avoid most danger zones.
- Regime overlay was structurally better, but the improvement over fixed `0.65` was small.
- Best overlay Sharpe was only around `1.109` versus fixed `0.65` around `1.100`.

Interpretation: regime add-ons are better framed as optional risk-control modules, not as the main alpha source.

## Asset Allocation Result

The most compelling extension was using the VIX strategy as a sleeve in a 60/40 portfolio.

Base portfolio:

```text
60% SPY + 40% IEF
```

VIX sleeve is funded by proportionally reducing SPY/IEF.

| Portfolio | CAGR | Ann. vol | Sharpe | MDD | Worst day |
|---|---:|---:|---:|---:|---:|
| 60/40 SPY-IEF | 7.87% | 10.89% | 0.783 | -32.99% | -5.72% |
| 20% fixed 0.65 VIX sleeve | 8.69% | 9.11% | 1.004 | -26.44% | -4.58% |
| 30% fixed 0.65 VIX sleeve | 9.07% | 8.46% | 1.118 | -23.02% | -4.63% |
| 30% overlay VIX sleeve | 9.06% | 8.44% | 1.119 | -23.02% | -4.63% |

This is not a pure tail hedge. The VIX sleeve does not necessarily make money on every SPY crash day. Its more accurate role is:

```text
low-correlation carry sleeve that improves portfolio efficiency
```

## What We Should Take

Take these directly into our project:

1. Use `r * VX1 - VX2` as the core hedged roll-down carry structure.
2. Use `ln(VX2/VX1)` for the tradable front-slope signal.
3. Keep entry/exit hysteresis: enter high, exit lower.
4. Keep `VX1 cap`, stop-loss, and roll-day avoidance as baseline risk controls.
5. Treat `0.65` as the economic hedge-ratio anchor.
6. Treat `0.80` as the empirical high-Sharpe benchmark.
7. Treat asset allocation sleeve usage as a serious final narrative, not an afterthought.

## What We Can Improve

Our additions should focus on areas not fully covered in the peer package:

1. `VX1/VIX` basis filter: avoid large VX1 spot premium when using a high VX1 long ratio.
2. Stop-loss modeling: compare close-only stops, stop clipping, and stop slippage.
3. Contract-level backtest: move beyond rank-based VX1/VX2 to actual maturity contracts.
4. Cost assumptions: slippage, roll cost, bid/ask, and margin efficiency.
5. Ratio selection: compare fixed `0.65`, fixed `0.80`, and basis-aware dynamic ratio.

## Current Working View

The peer research gives us a strong baseline. The best next framing is:

```text
0.65 = defensible shock-beta anchored baseline
0.80 = high-Sharpe front-vol-tilted variant
basis-aware dynamic ratio = our potential contribution
```

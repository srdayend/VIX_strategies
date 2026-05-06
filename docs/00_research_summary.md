# Research Summary

This is the current synthesis of the VIX strategies research notes. It is meant to be the first document to read before going into the detailed notes.

## One-Line Conclusion

The most promising strategy family is a hedged VIX futures roll-down carry trade, with `0.65VX1 - VX2` as the economic baseline and `0.80VX1 - VX2` as the empirical high-Sharpe benchmark. The most useful next improvement is a `VX1/VIX` basis filter, not another broad VIX-level regime rule.

## Strategy Definition

```text
Position = r * VX1 - VX2
front_slope = ln(VX2 / VX1)
```

Baseline rules used across the main tests:

```text
Entry: front_slope > 8%
Exit: front_slope < 5% or 7%
VX1 cap: enter only when VX1 < 30; exit when VX1 > 30
Stop: -2%, with both close-only and stop-clipped assumptions tested
Roll-day rule: avoid or exit on rank roll day
```

## What We Know

### 1. The data supports a carry/regime framework

The term structure is usually in contango, but behavior changes sharply in high-VIX states.

- Term-structure sample: `2004-03-26` to `2026-05-01`
- M2 > M1 contango days: about `79.0%`
- M2 < M1 backwardation days: about `15.9%`
- VIX `30+` states have materially weaker and often inverted front curves.

### 2. Naive M1/M2 carry is not enough

The early simple backtest, using `-M1 return + M2 return` with a basic slope/VIX gate, produced poor results. That made the hedged roll-down formulation and stronger entry/exit rules necessary.

### 3. `0.65` and `0.80` answer different questions

`0.65VX1 - VX2` is the economic anchor because peer research estimates spike-day median `dVX2 / dVX1` at about `0.653`.

`0.80VX1 - VX2` is the empirical high-Sharpe benchmark. It improves performance mostly through stronger right-tail participation when VX1 is not expensive versus spot VIX.

Working framing:

```text
0.65 = shock-beta anchored hedged carry baseline
0.80 = high-Sharpe front-vol-tilted hedged carry variant
basis-aware ratio/filter = possible project contribution
```

### 4. Stop modeling matters a lot

Changing the stop assumption from close-only loss realization to stop clipping at `-2%` materially improves both ratios.

For entry `8%` / exit `5%`:

| Ratio | Stop style | CAGR | Sharpe | MDD | Worst day |
|---:|---|---:|---:|---:|---:|
| 0.65 | close-only | 11.13% | 1.100 | -12.06% | -10.54% |
| 0.65 | stop-clipped | 13.87% | 1.456 | -10.42% | -2.00% |
| 0.80 | close-only | 15.93% | 1.400 | -11.08% | -9.74% |
| 0.80 | stop-clipped | 18.17% | 1.658 | -9.87% | -2.00% |

This assumption must be disclosed clearly in any final writeup.

### 5. The strongest threshold neighborhood is stable

For both `0.65` and `0.80`, the better entry/exit region is roughly:

```text
Entry: 7-9%
Exit: 5-7%
```

The peer `8% / 5%` rule remains defensible, but exit `6-7%` often improves Sharpe by exiting before the curve fully weakens.

### 6. VIX-level overlays add little; VX1/VIX basis is useful

The base rules already handle much of the VIX-level and slope risk through entry/exit, VX1 cap, roll-day avoidance, and stop loss.

The useful remaining risk-quality dimension is:

```text
front_basis = VX1 / VIX - 1
```

High basis means VX1 is expensive versus spot VIX. Since the strategy is long VX1 and short VX2, this directly affects trade quality.

For `0.80`, high-basis exit or no-entry rules improve Sharpe and drawdown, though aggressive filters reduce exposure and can reduce CAGR.

## Current Favorites

Candidate baseline set:

| Use case | Ratio | Entry | Exit | Basis rule | Notes |
|---|---:|---:|---:|---|---|
| Economic baseline | 0.65 | 8% | 6-7% | none or light `basis >= 15%` exit | Most defensible narrative |
| High-Sharpe candidate | 0.80 | 8% | 7% | test `basis >= 5%` or `10%` exit | Strongest standalone profile |
| Peer-compatible benchmark | 0.80 | 8% | 5% | optional basis filter | Useful comparison point |
| Dynamic candidate | 0.80/0.65 | 8% | 6-7% | use 0.80 only when basis is low | Main open research idea |

## Next Decisions

1. Decide whether the final strategy narrative should lead with `0.65`, `0.80`, or a basis-aware hybrid.
2. Test stop slippage at `-2.25%`, `-2.50%`, and `-3.00%`.
3. Move beyond rank-based VX1/VX2 to contract-level testing.
4. Add cost, roll, liquidity, and open-interest assumptions.
5. Test portfolio sleeve behavior, especially 60/40 plus VIX sleeve.

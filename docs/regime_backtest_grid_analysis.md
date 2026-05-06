# Regime Backtest Grid: `0.65` and `0.80`

This note tests whether regime-aware behavior improves the two main hedged roll-down strategies.

The goal is practical: if a regime is bad, should the strategy avoid entry, exit, or cut exposure?

## Setup

Primary assumptions:

```text
Position: r * VX1 - VX2
Ratios: 0.65 and 0.80
Stop: -2% stop-clipped daily return
VX1 cap: 30
Roll-day avoidance: true
```

Two threshold baselines are tested:

```text
Peer-compatible baseline: entry 8%, exit 5%
High-Sharpe threshold baseline: entry 8%, exit 7%
```

Regime actions:

| Action | Meaning |
|---|---|
| `no_entry` | Do not open a new position while the risk signal is active |
| `exit` | Exit an existing position if the risk signal is active |
| `scale_half` | Cut exposure to 50% when the previous close's risk signal was active |

Signals tested:

```text
VIX level: VIX >= 25, VIX >= 30
Slope: slope < 0%, slope < 3%
Basis: VX1/VIX - 1 >= 5%, 10%, 15%
Combinations: VIX/slope/basis mixed stress definitions
```

## Baselines

| Config | Ratio | CAGR | Ann. vol | Sharpe | MDD | Exposure | Trades | Stops |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| entry 8 / exit 5 | 0.65 | 13.87% | 9.66% | 1.456 | -10.42% | 40.69% | 209 | 42 |
| entry 8 / exit 5 | 0.80 | 18.17% | 10.90% | 1.658 | -9.87% | 40.69% | 209 | 33 |
| entry 8 / exit 7 | 0.65 | 13.73% | 9.30% | 1.495 | -10.07% | 36.52% | 257 | 36 |
| entry 8 / exit 7 | 0.80 | 18.10% | 10.54% | 1.704 | -9.87% | 36.52% | 257 | 28 |

## Main Finding

The clearest improvement does **not** come from VIX level or slope regimes. Those are mostly already handled by the base entry/exit/VX1-cap/stop rules.

The only regime family with consistent incremental value is:

```text
front_basis = VX1 / VIX - 1
```

High basis means VX1 is expensive versus spot VIX. Since both strategies are long VX1 and short VX2, high basis is a natural quality warning.

## Best Improvements: Entry 8 / Exit 5

### Ratio `0.80`

| Signal | Action | CAGR | Sharpe | MDD | Exposure | Delta Sharpe | Delta CAGR | Delta MDD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `basis >= 5%` | `exit` | 17.89% | 1.765 | -9.33% | 15.36% | +0.107 | -0.28%p | +0.54%p |
| `basis >= 5%` | `scale_half` | 17.80% | 1.743 | -9.19% | 19.10% | +0.085 | -0.37%p | +0.68%p |
| `basis >= 5%` | `no_entry` | 17.65% | 1.707 | -9.06% | 19.10% | +0.049 | -0.52%p | +0.81%p |
| `basis >= 15%` | `exit` | 18.50% | 1.697 | -9.94% | 36.20% | +0.039 | +0.33%p | -0.07%p |
| `basis >= 10%` | `exit` | 18.08% | 1.696 | -9.49% | 28.22% | +0.038 | -0.09%p | +0.38%p |

Read-through:

- `basis >= 5% exit` is best by Sharpe and drawdown, but it cuts exposure heavily and slightly reduces CAGR.
- `basis >= 10%` or `15%` exit keeps more return but improves Sharpe less.
- If the priority is clean risk-adjusted performance, `basis >= 5% exit` is the strongest overlay.
- If the priority is preserving CAGR, `basis >= 15% exit` is more balanced.

### Ratio `0.65`

| Signal | Action | CAGR | Sharpe | MDD | Exposure | Delta Sharpe | Delta CAGR | Delta MDD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `basis >= 15%` | `exit` | 13.86% | 1.471 | -10.57% | 36.20% | +0.015 | -0.01%p | -0.15%p |
| `basis >= 5%` | `exit` | 12.46% | 1.470 | -9.96% | 15.36% | +0.014 | -1.41%p | +0.46%p |
| `basis >= 15%` | `scale_half` | 13.77% | 1.462 | -10.31% | 37.40% | +0.005 | -0.10%p | +0.11%p |

Read-through:

- Regime overlays barely improve `0.65`.
- This supports the idea that `0.65` is already defensive enough.
- A mild high-basis exit can be used, but it is not a major alpha improvement.

## Best Improvements: Entry 8 / Exit 7

### Ratio `0.80`

| Signal | Action | CAGR | Sharpe | MDD | Exposure | Delta Sharpe | Delta CAGR | Delta MDD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `basis >= 5%` | `exit` | 17.45% | 1.766 | -9.33% | 14.07% | +0.062 | -0.64%p | +0.54%p |
| `basis >= 5%` | `scale_half` | 17.48% | 1.761 | -9.19% | 17.54% | +0.057 | -0.61%p | +0.68%p |
| `basis >= 5%` | `no_entry` | 17.52% | 1.743 | -9.06% | 17.54% | +0.039 | -0.58%p | +0.81%p |
| `basis >= 15%` | `exit` | 18.41% | 1.741 | -9.94% | 32.79% | +0.037 | +0.31%p | -0.07%p |

The same pattern holds: high-basis filters improve Sharpe, but the aggressive `5%` threshold reduces exposure and CAGR.

### Ratio `0.65`

| Signal | Action | CAGR | Sharpe | MDD | Exposure | Delta Sharpe | Delta CAGR | Delta MDD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `basis >= 15%` | `exit` | 13.80% | 1.518 | -10.57% | 32.79% | +0.022 | +0.07%p | -0.49%p |
| `basis >= 15%` | `scale_half` | 13.76% | 1.513 | -10.31% | 33.85% | +0.017 | +0.03%p | -0.23%p |
| `basis >= 15%` | `no_entry` | 13.72% | 1.505 | -10.05% | 33.85% | +0.010 | -0.01%p | +0.03%p |

Again, the improvement is small.

## What Did Not Work

### VIX-level signals

Examples:

```text
VIX >= 25
VIX >= 30
```

These did not materially improve results. The base rules already use `VX1 cap 30`, slope entry, stop clipping, and roll-day avoidance. By the time VIX-based risk signals matter, the strategy is often already out or close to exit.

### Slope-break signals

Examples:

```text
slope < 0
slope < 3%
```

These also add little because the base exit rule already handles slope decay. For example, with exit at `5%` or `7%`, a `slope < 3%` risk signal is usually too late to add much.

### Very strict quality regimes

Examples:

```text
carry_quality_bad = VIX >= 20 or slope < 8% or basis >= 10%
strong_only_bad = not(VIX < 15 and slope >= 8% and basis < 10%)
```

These are too restrictive. They cut too many trades and generally sacrifice CAGR without enough risk reduction.

## Interpretation

The regime backtest supports a clean conclusion:

```text
The base strategy already handles VIX-level and slope regimes well.
The remaining useful regime dimension is VX1/VIX basis.
```

That fits the economic logic:

- The strategy is long VX1 and short VX2.
- When VX1 is expensive versus spot VIX, the long leg becomes lower quality.
- A high-basis filter directly targets the part of the position that is most likely to degrade the trade.

## Working Recommendations

### For `0.80`

Use one of these depending on objective:

| Objective | Suggested rule |
|---|---|
| Max Sharpe / clean risk control | Exit or block when `VX1/VIX - 1 >= 5%` |
| Balanced return and quality | Exit when `VX1/VIX - 1 >= 10%` |
| Preserve most CAGR | Exit when `VX1/VIX - 1 >= 15%` |

Current favorite:

```text
0.80VX1 - VX2
entry 8%, exit 7%
stop clipped at -2%
exit overlay when VX1/VIX - 1 >= 5% or 10%
```

The `5%` threshold is best by Sharpe, while `10%` may be more practical if we do not want to over-filter.

### For `0.65`

Do not overcomplicate. Use either:

```text
0.65VX1 - VX2
entry 8%, exit 7%
stop clipped at -2%
no extra regime overlay
```

or a very light filter:

```text
exit when VX1/VIX - 1 >= 15%
```

The `0.65` version is already defensive; regime overlays add little.

## Next Tests

Before adopting a regime overlay, test:

1. Basis threshold robustness: `4%`, `5%`, `7.5%`, `10%`, `12.5%`, `15%`.
2. Stop slippage: `-2.0%`, `-2.25%`, `-2.5%`, `-3.0%`.
3. Contract-level execution: confirm the basis overlay still helps with actual maturities.
4. Portfolio sleeve impact: see whether the overlay improves 60/40 + VIX sleeve or merely reduces standalone volatility.

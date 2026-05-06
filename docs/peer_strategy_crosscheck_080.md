# Peer Strategy Crosscheck: `0.80VX1 - VX2`

This note cross-checks the highest-Sharpe strategy in the peer package.

## Strategy Definition

Position:

```text
0.80 * VX1 - 1.00 * VX2
```

Signal:

```text
front_slope = ln(VX2 / VX1)
```

Rules:

```text
Entry: front_slope > 8%
Exit: front_slope < 5%
VX1 cap: VX1 < 30 for entry; exit if VX1 > 30
Stop loss: exit if daily strategy return <= -2%
Roll rule: avoid / exit on rank roll day
```

Daily return definition:

```text
ret[t] = (0.80 * dVX1[t] - dVX2[t]) / (0.80 * VX1[t-1] + VX2[t-1])
```

The position is entered at today's close and becomes active from the next trading day.

## Crosscheck Result

Reimplementation output matched the peer package's saved `fixed_0.80` result.

| Metric | Recomputed | Peer CSV |
|---|---:|---:|
| CAGR | 15.9342% | 15.9342% |
| Annual vol | 11.5295% | 11.5295% |
| Sharpe | 1.399946 | 1.399946 |
| Max drawdown | -11.0838% | -11.0838% |
| Worst day | -9.7441% | -9.7441% |
| Exposure | 40.6920% | 40.6920% |
| Trades | 209 | 209 |
| Stops | 33 | 33 |

## Interpretation

The `0.80VX1 - VX2` version is the best-Sharpe point in the peer hedge-ratio scan. However, it is not necessarily the most defensible baseline because a high VX1 long leg makes the strategy less like pure hedged carry and more like a long-front-volatility tilted spread.

For research framing:

- Use `0.80` as the empirical high-Sharpe benchmark.
- Use `0.65` as the economically anchored hedge ratio because the peer package estimates spike-day median `dVX2 / dVX1` at about `0.653`.
- Compare both versions under the same regime and basis filters before choosing the final narrative.

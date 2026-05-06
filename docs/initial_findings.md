# Initial Findings

This note captures the first quick pass over the current local source files. Treat these as starting hypotheses, not final research conclusions.

## Coverage

- VIX futures term structure: `2004-03-26` to `2026-05-01`
- Term structure rows: `5,578`
- Complete 9-maturity curve rows: `3,578`, about `64.1%`
- VIX index OHLC: `1990-01-02` to `2026-05-05`

## Term-structure behavior

- M2 > M1 contango days: about `79.0%`
- M2 < M1 backwardation days: about `15.9%`
- Average M2/M1 - 1: about `5.75%`
- Median M2/M1 - 1: about `6.40%`
- Average M4/M1 - 1: about `12.28%`
- Median M4/M1 - 1: about `13.60%`

## VIX regime behavior

| VIX close bucket | Days | Contango rate | Avg M1-M2 % | Avg M1-M4 % |
|---|---:|---:|---:|---:|
| <15 | 2,137 | 94.6% | 9.00% | 20.46% |
| 15-20 | 1,710 | 84.9% | 6.38% | 13.77% |
| 20-25 | 865 | 68.6% | 4.18% | 7.18% |
| 25-30 | 416 | 59.9% | 1.41% | 0.59% |
| 30+ | 448 | 19.9% | -5.08% | -11.40% |

The curve changes character sharply when VIX gets into the `30+` zone. That makes VIX-regime gating and spike avoidance central, not optional.

## First baseline backtest diagnostic

A deliberately simple rank-based prototype was checked:

```text
active when M2/M1 - 1 >= 3% and VIX close <= 30
position = 10% capital fraction
return proxy = -M1 close-to-close return + M2 close-to-close return
```

Initial result:

- Active rate: about `69.3%`
- Ending equity multiple: about `0.356x`
- Annualized return: about `-4.8%`
- Annualized volatility: about `3.8%`
- Max drawdown: about `-65.3%`

Interpretation: naive front/deferred hedged carry is not enough. The next research step should decompose performance by VIX regime, slope percentile, curve shape, and recent spike behavior before optimizing parameters.

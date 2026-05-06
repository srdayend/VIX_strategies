# Backtesting Plan

The strategy phase focuses on roll-down carry with hedges, while avoiding naive exposure to volatility spikes.

## Baseline family

### Short front / long deferred hedge

Prototype expression:

```text
strategy return = -M1 return + hedge_ratio * M2 return
```

The first scaffold uses close-to-close changes in constant maturity ranks from the term-structure file. This is a research approximation, not yet a production execution model.

## Signal gates

Candidate filters:

- M2/M1 slope above threshold
- M4/M1 slope above threshold
- VIX close below threshold
- No deep backwardation
- No recent VIX spike
- Curve state belongs to historically carry-friendly cluster

## Hedge variants

- Short M1 / long M2
- Short M1 / long M3
- Short M1 / basket long M2-M4
- Short M2 / long M4
- Hedge ratio fixed at 1.0
- Hedge ratio beta-estimated from rolling returns
- Hedge ratio chosen to reduce VIX shock sensitivity

## Risk controls

- Volatility targeting
- Max drawdown stop for research diagnostics
- VIX spike de-risking
- Backwardation kill switch
- Exposure cooldown after large adverse moves
- Transaction cost and slippage sensitivity

## More realistic next step

Move from rank-based M1/M2 approximations to contract-level returns using `VIX_futures_by_maturity (1).xlsx`:

- Select actual front and deferred contracts each day
- Model roll windows
- Use volume/open interest liquidity filters
- Apply roll-day transaction cost assumptions
- Compare contract-realistic results against rank-based prototypes

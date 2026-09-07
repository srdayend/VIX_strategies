# G2-A CIRD / Data-Construction Core — Design

**Date:** 2026-09-07  
**Branch:** thesis/refinement  
**Research Gate:** G2 Data Construction  
**Status:** Approved

## 1. Scope

This subsystem implements the minimum research-grade machinery needed to represent actual VIX futures contracts and compute curve-implied roll-down (CIRD) without rank-series artifacts.

It includes only:

1. actual-contract schema,
2. official final-settlement-date handling,
3. calendar-day DTE,
4. local maturity curve construction,
5. static curve-implied roll-down,
6. realized same-contract P&L decomposition,
7. roll-boundary invariants,
8. tests.

It explicitly does **not** include:
- full Cboe historical downloader,
- weekly VX contracts,
- strategy optimization,
- hedge-ratio optimization,
- intraday execution,
- transaction-cost optimization,
- portfolio backtesting.

## 2. Economic objects

For actual contract j:

- settlement price: F[j,t]
- official final settlement date: T[j]
- calendar DTE: tau[j,t] = T[j] - t
- same-day maturity curve: Fhat_t(tau)

M1/M2 are derived rank labels only.

## 3. Settlement-date rule

The primary function must support a validated official settlement date per contract.

When official dates are not explicitly provided, a rule-based monthly VX date may be computed:

- nominally 30 calendar days prior to the third Friday of the following month,
- normally a Wednesday,
- with holiday adjustments handled explicitly,
- and the result must be treated as derived, not authoritative.

The module must allow authoritative settlement dates from source data to override the rule.

## 4. Calendar DTE

Use calendar days, not trading-day counts.

For interval t -> t+1:

delta_calendar = (date[t+1] - date[t]).days

Friday -> Monday therefore has delta_calendar = 3.

DTE must be non-negative before final settlement.

## 5. Local maturity curve

### Primary curve

Use local piecewise-linear interpolation in **price vs calendar DTE**.

Front boundary:

- anchor tau=0 to a time-aligned VIX level,
- connect VIX anchor to M1,
- connect M1 to M2,
- extend farther maturities locally segment by segment as needed.

No global spline in the primary estimator.

### Robustness, not primary

- log-price linear interpolation,
- PCHIP,
- parametric term-structure models.

These are out of G2-A unless needed only to expose a clean interface.

## 6. CIRD

For long contract j over one interval:

RD[j,t] = Fhat_t(tau[j,t+1]) - F[j,t]

Short roll-down contribution:

-RD[j,t]

For one short deferred contract and r long front contracts:

CIRD(r) = r * RD1 - RD2

## 7. Realized same-contract P&L

Realized move:

DeltaF[j,t+1] = F[j,t+1] - F[j,t]

Curve repricing:

RP[j,t+1] = F[j,t+1] - Fhat_t(tau[j,t+1])

Invariant:

DeltaF = RD + RP

Tests must verify this identity numerically.

## 8. Roll boundary

A change in rank label is not P&L.

The code must never calculate:

new_M1_price - old_M1_price

as a holding return.

At a roll:
- old actual contract holding P&L is closed,
- transaction/opening events are separate,
- the new contract starts with a new cost basis.

G2-A only enforces the data/P&L invariant; full roll execution comes later.

## 9. Primary APIs

Recommended interfaces:

- ContractRecord
- compute_monthly_vx_settlement_date(...)
- compute_calendar_dte(...)
- build_local_curve(...)
- curve_price_at_dte(...)
- compute_contract_roll_down(...)
- decompose_contract_move(...)
- compute_spread_cird(...)

The final names may vary only if the same responsibilities remain isolated and explicit.

## 10. Validation requirements

Use hand-computable synthetic tests for:

1. linear VIX-M1-M2 curve,
2. Friday-Monday three-day aging,
3. positive short carry under a simple contango example,
4. negative hedge carry cost under contango,
5. exact DeltaF = RD + RP identity,
6. rank-label change produces no holding P&L,
7. invalid DTE / expired-contract behavior,
8. authoritative settlement date overriding rule-derived date.

## 11. Data policy

Existing processed Excel files are reference/check datasets only.

No silent scale correction or outlier replacement is allowed in this subsystem.

Full raw Cboe ingestion is G2-B.

## 12. Acceptance

G2-A is accepted only when:
- APIs implement the approved economic definitions,
- all synthetic tests pass,
- edge cases are explicit,
- no strategy-performance code is introduced,
- no return denominator is introduced,
- no historical Sharpe/CAGR is used to justify implementation choices.

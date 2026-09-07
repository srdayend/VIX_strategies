# AGENTS.md — VIX Hedged Roll-Down Carry Thesis

## Project role

This repository supports a Seoul National University Industrial Engineering undergraduate thesis.

The thesis refines the 2026 Spring FIXERS project:
**VIX futures term-structure Hedged Roll-Down Carry**.

The goal is not to maximize historical Sharpe or proliferate strategy variants.
The goal is to make the original research economically precise, statistically defensible, reproducible, and execution-aware.

## Binding documents

Before changing thesis code, read these in order:

1. `docs/thesis/README.md`
2. `docs/thesis/METHODOLOGICAL_AUDIT_PROTOCOL.md`
3. `docs/thesis/CANONICALIZATION_STATUS.md`
4. the relevant approved design/spec in `docs/superpowers/specs/`
5. the relevant implementation plan in `docs/superpowers/plans/`

If code behavior conflicts with a binding methodology document, the methodology document wins.

## Branch policy

- `archive/fixers-baseline-v0`: frozen historical baseline. Never modify.
- `main`: historical/canonical pre-thesis line. Do not use for active thesis implementation.
- `thesis/refinement`: thesis integration branch.
- For non-trivial implementation, create an isolated worktree/feature branch from `thesis/refinement`.

Do not merge or rewrite history without explicit human approval.

## Research rules

### 1. No performance-first development

Never add a parameter, filter, stop, regime rule, or hedge variant merely because it improves CAGR, Sharpe, or drawdown.

Every empirical change must have:
- hypothesis,
- economic rationale,
- sample/window,
- primary metric,
- expected direction,
- OOS-touch status,

recorded in the Notion Thesis Experiment Registry before interpretation.

### 2. Preserve economic identity

The primary strategy is:
- short deferred VIX future for roll-down/carry,
- long front VIX future for tail-risk mitigation.

If an implementation causes expected P&L to be dominated by front-VIX directional exposure, flag strategy-identity drift rather than relabeling it as improved carry.

### 3. Actual contracts are the P&L primitive

M1/M2 are rank labels, not economic instruments.

Do not compute P&L from rank jumps.
Same-contract settlement-to-settlement P&L is the primitive.

A roll consists of:
- holding P&L on the old contract,
- close/open transactions,
- transaction costs,
- new position initialization.

The price difference between old M1 and new M1 is not return.

### 4. Keep these objects distinct

Do not conflate:
- raw front spread,
- maturity-normalized curve slope,
- curve-implied roll-down,
- statistical expected carry,
- realized P&L,
- investment return.

### 5. No arbitrary return denominator

Until capital/margin convention is explicitly approved, report economic output primarily in:
- VIX points per one short deferred contract,
- dollar P&L using the contract multiplier.

Do not silently call gross-notional-normalized P&L an investment return.

### 6. OOS honesty

Historical 2004–2026 data were already explored in the FIXERS/Codex project.
Do not describe any historical subset as pristine untouched OOS.

Use:
- historical development-contaminated sample,
- pseudo-OOS / walk-forward,
- post-freeze genuinely new data,

with those labels explicitly preserved.

## Current approved G2-A scope

Implement only:

1. actual-contract schema,
2. official final-settlement-date handling,
3. calendar-day DTE,
4. local maturity curve,
5. curve-implied roll-down estimator,
6. roll-boundary invariants,
7. tests.

Do NOT yet implement:
- full Cboe downloader/history ingestion,
- intraday engine,
- transaction-cost optimization,
- hedge-ratio optimization,
- strategy-performance tuning.

Those belong to later gates.

## Current approved CIRD methodology

For contract j:

- `F[j,t]`: settlement price
- `tau[j,t]`: calendar time to final settlement
- `Fhat_t(tau)`: same-day maturity curve

Long static roll-down:

`RD[j,t] = Fhat_t(tau[j,t+1]) - F[j,t]`

Same-contract realized move:

`DeltaF[j,t+1] = F[j,t+1] - F[j,t]`

Exact primary decomposition:

`DeltaF = RD + repricing`

For one short deferred future and `r` long front futures:

`CIRD(r) = r * RD1 - RD2`

Primary local curve design:
- calendar DTE axis,
- piecewise-linear price interpolation,
- front boundary anchored to time-aligned VIX at tau=0,
- log-price interpolation as robustness only.

Do not substitute a spline or parametric model into the primary estimator without a new approved methodology decision.

## Coding workflow

Use test-driven development for new thesis functionality:

1. write a failing test,
2. run it and confirm the expected failure,
3. implement the minimum code,
4. rerun the targeted test,
5. rerun the relevant suite,
6. refactor only while green.

For research calculations, tests should include:
- hand-computable synthetic examples,
- boundary cases,
- invariants,
- regression fixtures where appropriate.

## Verification

Never claim:
- tests pass,
- behavior is fixed,
- the implementation matches the spec,

without fresh command output proving it.

When handing work back, report:
- files changed,
- commands run,
- exact test results,
- unresolved concerns,
- methodology assumptions introduced.

## Data policy

Historical source binaries are frozen by checksum in `data/README.md`.

Current processed Excel files are reference/check datasets, not automatically trusted raw data.
Do not introduce silent scale corrections or outlier fixes.

Any correction must be:
- traceable to raw-source evidence,
- documented,
- tested.

## Scope discipline

When uncertain whether an implementation idea is methodology or engineering:
stop implementation and surface the question.

Do not solve methodological ambiguity with code.

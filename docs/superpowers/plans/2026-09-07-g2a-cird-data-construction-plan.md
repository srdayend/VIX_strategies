# G2-A CIRD / Data-Construction Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build a tested, actual-contract data/CIRD core that implements the approved G1/G2 methodology without rank-series P&L artifacts.

**Architecture:** Add a new focused thesis module separate from the legacy backtest engine. Keep contract calendar logic, local curve logic, and roll-down/decomposition logic isolated so each can be unit-tested independently. Existing historical backtests remain untouched.

**Tech Stack:** Python 3, pandas, numpy, pytest, standard library datetime/calendar.

**Spec:** docs/superpowers/specs/2026-09-07-g2a-cird-data-construction-design.md

## Global Constraints

- Work from thesis/refinement in an isolated branch/worktree.
- Do not modify archive/fixers-baseline-v0 or main.
- M1/M2 are rank labels, never P&L primitives.
- Use calendar-day DTE.
- Primary curve is local piecewise-linear price vs DTE with VIX anchor at tau=0.
- Do not add global spline/parametric fitting.
- Do not define investment return.
- Do not implement full Cboe ingestion in this plan.
- Do not optimize any trading parameter.
- Test first; every production behavior must be preceded by a failing test.

---

### Task 1: Contract calendar and schema

**Files:**
- Create: src/vix_strategies/thesis/contracts.py
- Create: tests/thesis/test_contracts.py

**Produces:**
- ContractRecord dataclass
- compute_monthly_vx_settlement_date(year: int, month: int, holidays: set[date] | None = None) -> date
- compute_calendar_dte(trade_date: date, settlement_date: date) -> int

- [ ] Step 1: Write failing tests for ContractRecord, monthly VX nominal settlement date, holiday override behavior, and Friday/Monday-compatible calendar DTE.
- [ ] Step 2: Run: pytest tests/thesis/test_contracts.py -v
Expected: FAIL because thesis contract module does not exist.
- [ ] Step 3: Implement minimum dataclass/date functions.
- [ ] Step 4: Run: pytest tests/thesis/test_contracts.py -v
Expected: PASS.
- [ ] Step 5: Commit: feat: add thesis contract calendar primitives

### Task 2: Local price-DTE curve

**Files:**
- Create: src/vix_strategies/thesis/curve.py
- Create: tests/thesis/test_curve.py

**Consumes:**
- ContractRecord / DTE primitives

**Produces:**
- CurvePoint(dte: float, price: float)
- build_local_curve(vix_level: float, futures_points: Sequence[CurvePoint])
- curve_price_at_dte(curve, target_dte: float) -> float

- [ ] Step 1: Write failing tests for exact interpolation at anchors, linear interpolation between VIX-M1 and M1-M2, sorted/unique DTE validation, and target-DTE bounds.
- [ ] Step 2: Run: pytest tests/thesis/test_curve.py -v
Expected: FAIL because curve module does not exist.
- [ ] Step 3: Implement minimum local piecewise-linear price-DTE curve.
- [ ] Step 4: Run: pytest tests/thesis/test_curve.py -v
Expected: PASS.
- [ ] Step 5: Commit: feat: add local VIX futures maturity curve

### Task 3: Contract roll-down and exact decomposition

**Files:**
- Create: src/vix_strategies/thesis/cird.py
- Create: tests/thesis/test_cird.py

**Consumes:**
- local curve API

**Produces:**
- compute_contract_roll_down(current_price, current_dte, next_dte, curve) -> float
- decompose_contract_move(current_price, next_price, current_dte, next_dte, curve) -> object with realized, roll_down, repricing
- compute_spread_cird(front_rd: float, deferred_rd: float, hedge_ratio: float) -> float

- [ ] Step 1: Write failing synthetic tests for contango short carry, front-long hedge carry cost, Friday-Monday aging, and exact realized = roll_down + repricing identity.
- [ ] Step 2: Run: pytest tests/thesis/test_cird.py -v
Expected: FAIL because cird module does not exist.
- [ ] Step 3: Implement minimum CIRD/decomposition functions.
- [ ] Step 4: Run: pytest tests/thesis/test_cird.py -v
Expected: PASS.
- [ ] Step 5: Commit: feat: add curve-implied roll-down decomposition

### Task 4: Rank-change invariant

**Files:**
- Create: src/vix_strategies/thesis/positions.py
- Create: tests/thesis/test_positions.py

**Produces:**
- same_contract_pnl(previous_positions, current_prices) behavior that keys holdings by actual contract ID
- explicit rejection of rank-only P&L inputs

- [ ] Step 1: Write failing test where M1 rank changes from contract A to B and assert B_price - A_price is not recorded as holding P&L.
- [ ] Step 2: Run: pytest tests/thesis/test_positions.py -v
Expected: FAIL because position module does not exist.
- [ ] Step 3: Implement minimum actual-contract keyed holding P&L primitive.
- [ ] Step 4: Run: pytest tests/thesis/test_positions.py -v
Expected: PASS.
- [ ] Step 5: Commit: fix: prevent rank transition from creating P&L

### Task 5: Integrated synthetic validation

**Files:**
- Create: tests/thesis/test_g2a_integration.py
- Modify only if necessary: src/vix_strategies/thesis/__init__.py

**Consumes:**
- all G2-A APIs

- [ ] Step 1: Write one end-to-end synthetic two-contract example covering VIX anchor, DTE aging, front/deferred RD, spread CIRD, realized repricing, and rank transition.
- [ ] Step 2: Run: pytest tests/thesis/test_g2a_integration.py -v
Expected: FAIL until public APIs are wired.
- [ ] Step 3: Add only minimal package exports needed by the test.
- [ ] Step 4: Run targeted integration test; then run: pytest tests/thesis -v
Expected: all thesis tests PASS.
- [ ] Step 5: Run the existing repository test suite if present; record any pre-existing failures separately.
- [ ] Step 6: Commit: test: validate G2-A economic invariants end to end

### Task 6: Documentation and handoff

**Files:**
- Create: docs/thesis/G2A_IMPLEMENTATION_STATUS.md

- [ ] Step 1: Record APIs, assumptions, commands executed, exact test counts, and any unresolved issues.
- [ ] Step 2: Confirm no code in G2-A calculates Sharpe/CAGR, defines investment return, or performs parameter optimization.
- [ ] Step 3: Run final: pytest tests/thesis -v
- [ ] Step 4: Review git diff against the approved spec.
- [ ] Step 5: Commit: docs: record G2-A validation status

## Self-review requirements

Before handoff:
- confirm every spec requirement maps to a task,
- search plan/code for TODO/TBD placeholders,
- confirm actual-contract IDs rather than M1/M2 are used for holding P&L,
- confirm calendar rather than trading-day DTE,
- confirm primary curve uses price-linear local interpolation,
- confirm no investment-return denominator was added.

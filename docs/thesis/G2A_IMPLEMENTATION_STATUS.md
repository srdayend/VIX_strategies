# G2-A Implementation Status

Date: 2026-09-07

Branch: `codex/g2a-cird-data-construction`

Base: `thesis/refinement`

## Implemented Scope

G2-A adds a thesis-only contract-level data/CIRD core separate from the
historical rank-based backtest engines.

Implemented APIs:

- `ContractRecord`
- `compute_monthly_vx_settlement_date`
- `compute_calendar_dte`
- `CurvePoint`
- `LocalCurve`
- `build_local_curve`
- `curve_price_at_dte`
- `compute_contract_roll_down`
- `decompose_contract_move`
- `compute_spread_cird`
- `ContractPosition`
- `same_contract_pnl`

## Methodology Mapping

- Actual contracts are represented by `contract_id` on `ContractRecord` and
  `ContractPosition`.
- Official settlement dates can be supplied directly through
  `ContractRecord` or `ContractRecord.from_monthly_vx`.
- Rule-derived monthly settlement dates are marked with
  `settlement_date_source="derived"` and are not treated as authoritative.
- The monthly schema is explicit: G2-A accepts monthly contracts and rejects
  weekly listing types.
- Calendar DTE is computed as `(settlement_date - trade_date).days`, so a
  Friday-to-Monday interval ages by three calendar days.
- The primary local curve is price-linear over calendar DTE and anchors VIX
  at tau 0.
- Contract roll-down is `Fhat_t(next_dte) - current_price`.
- Contract roll-down validates that the current DTE is on the local curve and
  that the current settlement price matches the curve at that DTE.
- Realized decomposition is exact by construction:
  `next_price - current_price = roll_down + repricing`.
- Holding P&L is keyed by actual contract ID. Rank-only labels such as `M1`
  and `VX1` are rejected at the same-contract P&L boundary.

## Explicit Engineering Assumptions

- The rule-derived monthly VX date uses the approved rule:
  third Friday of the following month minus 30 calendar days.
- If the rule-derived settlement Wednesday or the Friday 30 days after that
  Wednesday falls on an explicitly supplied Cboe Options holiday, settlement
  is adjusted backward to the prior non-holiday weekday.
- Local curve interpolation does not extrapolate beyond the VIX anchor and
  farthest provided futures DTE.
- Futures DTE anchors must be positive, strictly increasing, and price-positive.

## Commands and Results

- `python -m pip install -r requirements.txt`
  - Result: all requirements already satisfied in the active Python
    environment.
- Baseline `python -m pytest -v`
  - Result before new tests: collected 0 items; no tests ran; exit code 1.
- `python -m pytest tests/test_package_import.py -v`
  - RED: package import failed under local pandas 1.4.1 because
    `ChainedAssignmentError` and `mode.copy_on_write` were unavailable.
  - GREEN: 1 passed.
- `python -m pytest tests/thesis/test_contracts.py -v`
  - RED: `ModuleNotFoundError: No module named 'vix_strategies.thesis.contracts'`.
  - GREEN: 9 passed.
- `python -m pytest tests/thesis/test_curve.py -v`
  - RED: `ModuleNotFoundError: No module named 'vix_strategies.thesis.curve'`.
  - GREEN: 6 passed.
- `python -m pytest tests/thesis/test_cird.py -v`
  - RED: `ModuleNotFoundError: No module named 'vix_strategies.thesis.cird'`.
  - GREEN: 7 passed.
- `python -m pytest tests/thesis/test_positions.py -v`
  - RED: `ModuleNotFoundError: No module named 'vix_strategies.thesis.positions'`.
  - GREEN: 3 passed.
- `python -m pytest tests/thesis/test_g2a_integration.py -v`
  - RED: package-level thesis exports were not wired.
  - GREEN: 1 passed.
- Current full test command: `python -m pytest -v`
  - Result: 27 passed in 0.62s.

## Scope Checks

Search command:

`rg -n "Sharpe|CAGR|optimization|optimize|return denominator|investment return|TODO|TBD" src/vix_strategies/thesis tests/thesis tests/test_package_import.py tests/conftest.py`

Result: no matches.

No full Cboe ingestion, intraday engine, transaction-cost optimization,
hedge-ratio optimization, Sharpe/CAGR improvement, or investment-return
denominator was introduced.

## Unresolved Concerns

- Authoritative Cboe settlement-date source ingestion is not implemented in
  G2-A. Future data construction must supply official dates and treat derived
  dates as non-authoritative fallbacks.
- Weekly VX contracts are out of scope.
- Full roll execution, close/open transactions, transaction costs, and new
  cost basis events remain later-gate work.
- Capital, margin, and investment-return denominator conventions remain
  intentionally undefined.

## Methodology Decisions Not Made Here

- No curve model beyond primary local price-linear interpolation was chosen.
- No hedge ratio was optimized or recommended.
- No sample split, OOS interpretation, Sharpe/CAGR interpretation, or
  performance claim was made.
- No transaction-cost, slippage, or margin convention was selected.

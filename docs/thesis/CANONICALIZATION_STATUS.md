# Canonicalization Status — 2026-09-07

## Decision

The FIXERS project is frozen as **Baseline v0** and thesis development continues only on `thesis/refinement`.

## Frozen reference

- Repository: `srdayend/VIX_strategies`
- Frozen branch: `archive/fixers-baseline-v0`
- Frozen commit: `1447b5e64a78a2e25746d4b0a79373651e35a880`
- `main` has not been modified by thesis canonicalization.

## Active thesis branch

- Branch: `thesis/refinement`
- Purpose: canonical research line for the SNU Industrial Engineering undergraduate thesis.
- Research stance: **refine the existing Hedged Roll-Down Carry project rather than branch into many new strategies.**

## What has been consolidated

The active branch now contains the full functional source surface represented in the current FIXERS evidence package:

### Data
- `data/source_paths.py`
- `data/excel_loaders.py`

### Analysis
- `analysis/summarize_term_structure.py`
- `analysis/vix_distribution_rolldown_hedge_ratio.py`

### Backtests
- `backtests/simple_m1_m2_carry_backtest.py`
- `backtests/hedged_vx1_vx2_rolldown.py`

### Existing experiments
- `compare_065_vs_080_hedge_ratios.py`
- `reproduce_peer_research.py`
- `stop_loss_parameter_grid.py`
- `regime_overlay_grid.py`
- `high_r_hedge_ratio_extension.py`
- `stop_slippage_and_yearly_extension.py`
- `contango_frequency.py`
- `portfolio_sleeve_overlay.py`
- `summary_charts.py`

### Chart utilities
- `charts/`

The older `VIX.zip` backtest skeleton and code package are treated as **legacy lineage**, not as active thesis code.

## Binary / large-file policy

The following source artifacts remain outside GitHub and are frozen by SHA-256 in `data/README.md`:

- VIX futures term-structure workbook
- VIX futures contract-by-maturity workbook
- CBOE VIX daily OHLC workbook
- VIX.zip
- FIXERS evidence ZIP
- FIXERS presentation PPTX

This avoids mixing large historical binaries with the active source tree while keeping the exact snapshots verifiable.

## Output policy

Historical CSV / chart outputs are evidence, not canonical thesis results.

Going forward:
1. code is canonical,
2. config is canonical,
3. raw-data checksum is canonical,
4. tables and figures are regenerated,
5. thesis claims cite the regenerated output and code/config lineage.

## Known methodological issues inherited from Baseline v0

These are intentionally **not fixed silently during canonicalization**:

- rank-based VX1/VX2 vs actual contract-level execution,
- possible rank-transition / roll-day P&L contamination,
- gross-notional return proxy vs capital/margin accounting,
- stop-clipped intraday fill assumption,
- transaction-cost / bid-ask / slippage omission,
- parameter selection on the same sample used for evaluation,
- weak statistical inference around mean return / Sharpe,
- limited OOS / structural-break validation,
- mixed versions of some portfolio and regime outputs.

They will be addressed explicitly in the thesis refinement stages.

## Next engineering step

Do not modify the historical engine in place. Build a thesis-quality engine with:
- explicit contract mapping,
- explicit signal/execution timestamps,
- config objects,
- unit/regression tests,
- data-quality checks,
- deterministic table/figure generation,
- separate IS/OOS evaluation.

This document marks **Stage 1: Canonicalization** as substantially complete.

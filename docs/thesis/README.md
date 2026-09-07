# SNU Industrial Engineering Undergraduate Thesis — VIX Hedged Roll-Down Carry

This branch is the canonical research line for refining the 2026 Spring FIXERS project into a Seoul National University Industrial Engineering undergraduate thesis.

## Research stance

The objective is **refinement, not strategy proliferation**.

We keep the core FIXERS research question and rebuild it with:
- precise economic definitions,
- explicit data lineage,
- statistically defensible inference,
- out-of-sample / robustness checks,
- execution-aware backtesting,
- one reproducible code-to-table/figure pipeline.

Headline performance from the presentation is not treated as something that must be preserved. If a stronger methodology weakens the result, the stronger methodology wins.

## Branch policy

- `archive/fixers-baseline-v0`: frozen GitHub baseline as of 2026-09-07.
- `thesis/refinement`: only active development line for the thesis.
- `main`: left untouched while canonicalization is in progress.

## Planned pipeline

1. Canonicalize source code and data definitions.
2. Audit rank-series construction, roll logic, signal timing and P&L.
3. Rebuild the backtest with explicit configs and tests.
4. Re-estimate the economic evidence: contango, maturity beta, volatility, carry, shock beta and basis.
5. Separate economic parameter justification from in-sample performance optimization.
6. Add statistical uncertainty, OOS / walk-forward analysis and realistic costs.
7. Re-run portfolio analysis on one consistent sample and return definition.
8. Generate every thesis table and figure from code.

See the project Notion Research Hub for the reconstruction map and methodological audit.

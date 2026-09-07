# VIX Hedged Roll-Down Carry — Thesis Research Repository

This repository is the canonical codebase for refining the 2026 Spring FIXERS project into a **Seoul National University Industrial Engineering undergraduate thesis**.

## Research objective

The project does **not** aim to proliferate new VIX strategies. It keeps the original Hedged Roll-Down Carry idea and raises its methodological completeness:

- precise economic and return definitions,
- explicit data lineage and contract mapping,
- statistically defensible parameter selection and inference,
- out-of-sample / robustness validation,
- execution-aware backtesting,
- one reproducible code → table / figure pipeline.

If a stricter methodology weakens the original presentation result, the stricter methodology takes priority.

## Branch policy

- `archive/fixers-baseline-v0` — frozen pre-thesis GitHub baseline at commit `1447b5e64a78a2e25746d4b0a79373651e35a880`.
- `thesis/refinement` — **the only active thesis-development branch**.
- `main` — intentionally left unchanged while thesis canonicalization is underway.
- old `codex/*` branches — historical work only; not canonical.

## Original FIXERS strategy

```text
Position = r * VX1 - 1.00 * VX2
front_slope = ln(VX2 / VX1)
```

Economic intuition:
- short `VX2`: roll-down / carry leg,
- long `VX1`: volatility-spike hedge leg,
- `r`: hedge ratio controlling the carry-vs-hedge trade-off.

The original project used a rank-based close-to-close backtest and explored slope thresholds, a VX1 cap, stop rules, hedge ratios, basis/regime analysis, and portfolio sleeves. Those results are treated as **Baseline v0**, not as thesis-final evidence.

## Thesis refinement priorities

1. Define whether the object is a synthetic rank-series strategy or an executable futures strategy.
2. Audit VX1/VX2 construction, contract transitions and roll-day P&L.
3. Formalize signal timing and eliminate look-ahead ambiguity.
4. Rebuild return/capital/margin accounting.
5. Re-estimate maturity beta, volatility, carry, shock beta and basis with uncertainty.
6. Separate economic parameter justification from in-sample performance optimization.
7. Add OOS / walk-forward and subperiod robustness.
8. Add costs, slippage and defensible stop assumptions.
9. Add statistical inference and tail-risk diagnostics.
10. Re-run portfolio analysis on one consistent sample and return convention.

See [docs/thesis/README.md](docs/thesis/README.md).

## Repository map

```text
archive/
  README.md                    Historical lineage policy

data/
  README.md                    Immutable source-file checksum manifest

docs/
  thesis/                      Thesis methodology / decisions / validation
  00_research_summary.md       FIXERS-era / post-FIXERS research synthesis
  01_data/                     Existing data notes
  02_strategy/                 Existing strategy framing
  03_results/                  Existing result interpretation
  04_backlog/                  Historical backlog

src/vix_strategies/
  data/                        Loaders and source path resolution
  analysis/                    Descriptive / sizing analysis
  backtests/                   Strategy engines
  experiments/                 Existing experiment suite
  charts/                      Chart helpers

reports/generated/             Reproducible generated outputs
```

## Source data

Large source workbooks and the historical ZIP/PPT packages are not committed on the thesis branch. Their SHA-256 hashes are recorded in [data/README.md](data/README.md).

Expected raw sources include:
- VIX futures term structure,
- contract-by-maturity VIX futures,
- CBOE VIX Index daily OHLC,
- SPY / IEF price histories for portfolio analysis.

Path overrides:
```text
VIX_TERM_STRUCTURE_PATH
VIX_FUTURES_BY_MATURITY_PATH
VIX_INDEX_PATH
```

## Existing experiment entry points

```bash
python -m src.vix_strategies.analysis.vix_distribution_rolldown_hedge_ratio
python -m src.vix_strategies.experiments.reproduce_peer_research
python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios
python -m src.vix_strategies.experiments.stop_loss_parameter_grid
python -m src.vix_strategies.experiments.regime_overlay_grid
python -m src.vix_strategies.experiments.high_r_hedge_ratio_extension
python -m src.vix_strategies.experiments.stop_slippage_and_yearly_extension
python -m src.vix_strategies.experiments.contango_frequency
python -m src.vix_strategies.experiments.portfolio_sleeve_overlay
```

These scripts preserve and organize the existing project. The thesis-quality engine and tests will be developed separately on `thesis/refinement` rather than silently modifying historical results.

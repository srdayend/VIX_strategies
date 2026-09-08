# G2-B1 Implementation Status

## Scope

Implemented G2-B1 VX futures canonical panel infrastructure only:

- Cboe VX source registry and immutable provenance manifest records.
- Legacy vs modern monthly VX final-settlement date regimes.
- Fixture-based raw Cboe contract-row parsers.
- Standard monthly VX universe filter.
- Official 2007 price/multiplier normalization.
- DAILY_DSP vs FINAL_SOQ observation typing.
- Canonical contract-date records with raw row/file lineage.
- Duplicate/conflict validation and holdout-safe access.
- Fixture-based reproducible pipeline outputs and run metadata.

Not implemented:

- G2-B2 VIX anchor acquisition/alignment.
- M1/M2 maturity-rank panel construction.
- CIRD calculation.
- Hedge ratio selection.
- Strategy/backtest/performance analysis.
- Legacy workbook full reconciliation.

## RED/GREEN Evidence

This file is finalized after the live-source smoke step.

## Live-Source Smoke

Pending final smoke retrieval.

## Unresolved Source/Schema Issues

- Current-detail fixture columns use the same source-shaped contract detail
  layout documented in repository source inventory and parser fixtures.
  Final live-source smoke must verify whether the official current-detail CSV
  exposed by Cboe still matches this parser contract.

# G2-B — Authoritative Raw Data Construction Design

**Date:** 2026-09-08  
**Branch:** thesis/refinement  
**Research Gate:** G2 Data Construction  
**Status:** Approved  
**Depends on:** G2-A CIRD / Data-Construction Core

## 1. Objective

G2-B rebuilds the research data foundation from authoritative Cboe sources.

The objective is not to reproduce the legacy Excel files exactly and not to improve strategy performance.

The target lineage is:

`Cboe source -> immutable raw -> canonical actual-contract panel -> later derived maturity ranks`

No CIRD result, hedge-ratio result, signal rule, Sharpe, CAGR, or strategy backtest may be interpreted before G2-C validates the canonical panel.

## 2. Implementation split

G2-B is implemented in two separately reviewed units.

### G2-B1 — VX futures canonical panel

- official/public Cboe futures source registry
- immutable source manifest
- monthly VX universe
- historical contract-calendar regimes
- 2007 exchange-wide price/multiplier rescaling
- DAILY_DSP vs FINAL_SOQ observation typing
- raw-to-canonical lineage
- missing/duplicate/conflict policy
- development/holdout quarantine

### G2-B2 — VIX anchor provenance

- official VIX source registry
- futures-settlement timestamp regime
- VIX anchor timestamp/alignment status
- exact vs proxy anchor classification
- decision on paid/exact post-2020 data only after B1 coverage is known

Do not combine B1 and B2 implementation into one uncontrolled task.

## 3. Authoritative source hierarchy

### 3.1 VX futures

Primary public Cboe sources:

1. CFE Historical Archive, contract-level VX Price and Volume Detail, 2004–2013.
2. CFE Price and Volume Detail for select futures products, 2013–current.

2013 is an overlap/bridge year and must later be reconciled between source families.

Legacy project files:
- `VIX_futures_by_maturity.xlsx`
- `VIX_futures_term_structure.xlsx`
- historical FIXERS/Codex artifacts

are reference/reconciliation artifacts only, not authoritative raw input.

### 3.2 Source provenance

Every ingested source file must have:
- source family
- source URL
- retrieval timestamp
- local immutable path
- SHA-256 checksum
- source filename
- parser version
- ingest status

Raw source files are never edited in place.

## 4. Canonical monthly VX universe

Primary thesis universe:
- CFE VX
- standard monthly expirations only

Explicitly exclude:
- weekly VX
- VX TAS / VXT observations as separate instruments
- VXM
- calendar spreads / combinations
- options on futures

Canonical contract ID:
`VX_YYYYMM`

Preserve source symbol separately.

M1/M2 are never stored as economic identities in the raw/canonical contract panel.

## 5. Historical final-settlement regimes

### 5.1 Legacy regime

Original VX specification:
- final settlement was the Wednesday immediately prior to the third Friday associated with the contract month structure used at launch.

For canonical implementation, this legacy rule applies to contracts governed by the pre-2005-10-17 specification.

### 5.2 Modern regime

Effective 2005-10-17, CFE changed the rule:
- final settlement is the Wednesday 30 days prior to the third Friday of the calendar month immediately following the contract expiration month,
- with applicable Cboe Options holiday adjustment.

### 5.3 Governance

Do not apply the G2-A modern settlement-date helper blindly to the full history.

Each contract calendar entry must include:
- contract_id
- contract_month
- final_settlement_date
- settlement_rule_regime
- settlement_date_source
- validation_status
- evidence_reference

Allowed validation statuses:
- `explicit_official`
- `rule_derived_validated`
- `rule_derived_unvalidated`

Primary canonical analysis may not use `rule_derived_unvalidated` contracts.

## 6. 2007 exchange-wide rescaling

CFE rescaled VX effective 2007-03-26:
- displayed futures price divided by 10
- multiplier changed from $100 to $1,000
- dollar contract value preserved

Therefore raw and canonical values must coexist.

For rows before 2007-03-26:
- preserve source price unchanged in raw fields
- normalized VIX-point price = raw price / 10
- source multiplier = 100
- canonical comparison multiplier = 1000
- normalization factor = 0.1

For rows on/after 2007-03-26:
- normalized price = raw price
- source multiplier = 1000
- normalization factor = 1.0

This is the only automatically permitted historical scale normalization in G2-B1.

No per-contract x10 or /10 heuristic may be introduced.

## 7. Observation types

Published final settlement / SOQ is not an ordinary daily futures DSP.

Canonical `observation_type`:
- `DAILY_DSP`
- `FINAL_SOQ`

Rules:
- FINAL_SOQ is retained for later final-settlement P&L handling.
- FINAL_SOQ is not an ordinary EOD maturity-curve point.
- A contract that has final-settled is not eligible for the normal post-settlement daily curve.
- Do not infer roll return from the price difference between the final-settled contract and the next ranked contract.

## 8. Immutable raw schema

Minimum raw record fields:

- source_file
- source_family
- source_url
- source_sha256
- retrieval_timestamp
- parser_version
- raw_row_id
- source_symbol
- trade_date
- raw_open
- raw_high
- raw_low
- raw_close
- raw_settle
- raw_change
- raw_volume
- raw_efp
- raw_open_interest

The raw layer preserves source values and source missingness.

No normalization, forward-fill, clipping, or outlier correction occurs in raw records.

## 9. Canonical contract-date schema

Minimum canonical fields:

- trade_date
- contract_id
- contract_month
- source_symbol
- final_settlement_date
- settlement_rule_regime
- settlement_date_source
- settlement_date_validation_status
- listing_type
- observation_type
- price_scale_regime
- source_multiplier
- normalization_factor
- open_norm
- high_norm
- low_norm
- close_norm
- settle_norm
- volume
- open_interest
- source_file
- source_row_id
- source_sha256
- quality_flags
- sample_role

Primary economic price for later research:
- published settlement, transformed only by the official 2007 normalization regime.

Do not use source `Change` as an economic P&L primitive.

## 10. Missing / duplicate / conflict policy

### Missing

- Never forward-fill futures settlement.
- Missing settlement => row ineligible for primary curve/P&L.
- Missing OHLC may remain if settlement exists.
- Missing volume/OI remains missing.

### Duplicate key

Canonical uniqueness key:
`(trade_date, contract_id, observation_type)`

- exact duplicate with identical values => deterministic deduplication with provenance flag
- conflicting duplicate => do not silently choose; emit conflict record / fail acceptance

### Abnormal price

No automatic clipping, winsorization, x10, /10, or neighboring-price replacement.

Only official exchange-wide 2007 normalization is automatic.

Any other suspected scale issue must be:
- reconciled to an independent official source, or
- flagged unresolved.

## 11. Sample quarantine

Historical strategy-development cutoff:
`2026-05-01`

Rows:
- trade_date <= 2026-05-01 => `development_contaminated`
- trade_date > 2026-05-01 => `post_freeze_holdout`

Post-freeze holdout may be:
- downloaded
- checksummed
- parsed
- schema validated
- quality checked

but must not be used for:
- parameter selection
- feature selection
- hedge-ratio selection
- strategy comparison
- G3–G9 development conclusions

Development-facing APIs/reports must default-exclude the holdout.

## 12. G2-B1 acceptance gates

G2-B1 is accepted only when:

1. every canonical row traces to an immutable raw Cboe source row/file;
2. source SHA-256 and retrieval metadata exist;
3. no silent/manual price correction exists;
4. legacy and modern settlement-rule regimes are explicit;
5. 2007 normalization is explicit and unit-tested;
6. DAILY_DSP and FINAL_SOQ are separated;
7. monthly VX is separated from weekly/TAS/VXM/combinations;
8. canonical duplicate key is enforced;
9. unresolved conflicts are enumerated rather than hidden;
10. holdout quarantine is enforced by default;
11. no M1/M2 strategy panel or CIRD/backtest result is produced.

## 13. G2-B2 scope

G2-B2 starts only after G2-B1 review.

Known futures DSP reference-time regime:
- historical reference time: 3:15 p.m. CT
- effective 2020-10-26: 3:00 p.m. CT on normal business days

The VIX anchor layer must record:
- vix_value
- vix_source
- vix_timestamp
- target_futures_settlement_timestamp
- anchor_alignment

Allowed `anchor_alignment`:
- `exact`
- `proxy_15m`
- `unavailable`

Do not purchase paid intraday VIX data before B1 establishes the exact required date coverage and the research thread approves the cost/benefit decision.

## 14. G2-B / G2-C boundary

### G2-B

- source ingestion
- immutable raw manifest
- contract calendar
- official normalization
- observation typing
- holdout quarantine
- VIX anchor provenance layer

### G2-C

- full legacy-workbook reconciliation
- 2013 overlapping-source reconciliation
- derived M1/M2 panel
- completeness diagnostics
- sparse-listing diagnostics
- unexplained mismatch audit
- final canonical dataset approval

No strategy result before G2-C approval.

## 15. Binding source references

- Cboe Historical Archive: https://www.cboe.com/markets/us/futures/market-statistics/historical-data/settlement-archive
- Cboe historical futures detail: https://www.cboe.com/markets/us/futures/market-statistics/historical-data/futures/
- Original VX contract specification: CFE-2004-10
- 2005 settlement-date revision: CFE-2005-28
- 2007 VX rescaling circular: CFE-IC-2007-003
- 2020 DSP reference-time change notice: Cboe adjustment effective 2020-10-26

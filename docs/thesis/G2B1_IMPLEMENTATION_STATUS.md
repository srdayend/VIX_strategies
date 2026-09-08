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

- Baseline before G2-B1 work:
  `python -m pytest -v` -> `33 passed in 1.96s`.
- Task 1 source manifest:
  RED `python -m pytest tests/thesis/test_g2b_sources.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.data_sources'`;
  GREEN -> `6 passed in 0.51s`.
- Task 2 settlement regimes:
  RED `python -m pytest tests/thesis/test_g2b_calendar.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_calendar'`;
  GREEN -> `6 passed in 0.48s`.
- Task 3 raw parsers:
  RED `python -m pytest tests/thesis/test_g2b_raw_parsers.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_raw'`;
  GREEN -> `5 passed in 0.58s`.
- Task 4 monthly universe:
  RED `python -m pytest tests/thesis/test_g2b_universe.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_universe'`;
  GREEN -> `9 passed in 0.50s`.
- Task 5 2007 normalization:
  RED `python -m pytest tests/thesis/test_g2b_normalization.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_normalization'`;
  GREEN -> `8 passed in 0.45s`.
- Task 6 canonical records:
  RED `python -m pytest tests/thesis/test_g2b_canonical.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_canonical'`;
  GREEN -> `7 passed in 0.48s`.
- Task 7 validation/quarantine:
  RED `python -m pytest tests/thesis/test_g2b_validation.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_validation'`;
  GREEN -> `5 passed in 0.49s`.
- Task 8 pipeline:
  RED `python -m pytest tests/thesis/test_g2b_pipeline.py -v` ->
  `ModuleNotFoundError: No module named 'vix_strategies.thesis.vx_pipeline'`;
  GREEN -> `2 passed in 1.10s`.
- Task 9 live-smoke hardening:
  archive-style symbol RED
  `python -m pytest tests/thesis/test_g2b_universe.py::test_archive_month_code_symbol_is_primary_when_calendar_evidence_matches -v`
  -> `1 failed in 0.63s`;
  GREEN -> `1 passed in 0.47s`.
- Task 9 FINAL_SOQ/zero-price hardening:
  RED
  `python -m pytest tests/thesis/test_g2b_canonical.py::test_final_soq_allows_zero_ohlc_from_source_without_price_repair tests/thesis/test_g2b_canonical.py::test_non_positive_daily_settlement_is_flagged_ineligible_not_forward_filled -v`
  -> `2 failed in 0.66s`;
  GREEN -> `2 passed in 0.51s`.

Final local verification:

- `python -m pytest tests/thesis -v` -> `83 passed in 1.54s`.
- `python -m pytest -v` -> `84 passed in 1.61s`.
- Scope scan command:
  `rg -n "Sharpe|CAGR|hedge.?ratio|M1|M2|CIRD|backtest|optimi[sz]" src/vix_strategies/thesis scripts/build_g2b1_vx_canonical_panel.py`
  matched only pre-existing G2-A thesis files:
  `src/vix_strategies/thesis/positions.py` rank-label rejection and
  `src/vix_strategies/thesis/cird.py` G2-A CIRD/hedge-ratio helpers.
  No new G2-B1 module or script emits M1/M2 panels, CIRD, backtests, or
  performance analysis.

## Live-Source Smoke

- Archive URL attempted:
  `https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_F13_VX.csv`.
- Retrieval result: success.
- Temp file:
  `C:\Users\heeta\AppData\Local\Temp\CFE_F13_VX_g2b1_smoke.csv`.
- SHA-256:
  `5e880a72439277bc6a274c2b4e233da1b6d12ce235d4a7fa2707785675f933d8`.
- Line count: `194` including header.
- Header:
  `Trade Date,Futures,Open,High,Low,Close,Settle,Change,Total Volume,EFP,Open Interest`.
- Raw parse result: `193` records, date range `2012-04-11` to `2013-01-16`,
  first source symbol `F (Jan 13)`.
- Positive-row canonical smoke:
  row `CFE_F13_VX_g2b1_smoke.csv:11`, trade date `2012-04-24`, source symbol
  `F (Jan 13)`, raw OHLC/settle `27.49, 27.49, 27.28, 27.35, 27.25`;
  canonical result `VX_201301`, `DAILY_DSP`, `post_2007_standard`,
  source multiplier `1000`, normalization factor `1.0`, settle norm `27.25`,
  sample role `development_contaminated`, primary curve eligible `True`.
- One-file archive pipeline smoke:
  status `accepted`, raw records `193`, canonical records `193`,
  conflicts `0`, quality flag counts
  `{'non_positive_settlement': 8, 'final_soq_zero_ohlc': 1}`;
  final SOQ row `2013-01-16`, settle norm `13.69`,
  quality flags `('final_soq_zero_ohlc',)`, primary curve eligible `False`.
- Current-detail registry page attempted:
  `https://www.cboe.com/markets/us/futures/market-statistics/historical-data/futures/`.
  Retrieval result: HTTP `200`, static HTML content length `403180`.
  The static HTML exposes the `VX+VXT` product selector but did not expose a
  direct per-contract current-detail CSV URL in the inspected HTML.

## Unresolved Source/Schema Issues

- Current-detail per-contract CSV URL discovery remains unresolved because the
  Cboe page appears to expose the selector through client-side UI rather than a
  direct static link. No alternate legacy Excel file was substituted as an
  authoritative source.
- Current-detail fixture columns intentionally match the official archive
  header verified in live smoke. They still require future confirmation against
  an actual 2013-current Cboe current-detail contract CSV once its direct source
  URL or browser-mediated link is available.
- Contract calendars in these tests use rule-derived fixture entries with
  explicit validation status; full official settlement-date table ingestion is
  not part of G2-B1.

## G2-B2 Boundary

No VIX anchor acquisition, VIX timestamp alignment, paid intraday data decision,
or anchor classification layer was implemented.

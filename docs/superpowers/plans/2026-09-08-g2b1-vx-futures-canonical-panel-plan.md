# G2-B1 VX Futures Canonical Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, provenance-preserving Cboe VX monthly-futures ingestion and canonicalization pipeline without producing maturity-rank strategy data.

**Architecture:** Keep source acquisition/manifest logic, source parsing, contract-calendar rules, normalization, canonical validation, and output writing in separate focused modules. Unit tests use local synthetic/fixture files and must not require live network access. A live-source smoke run is allowed only after the parser/validator suite is green.

**Tech Stack:** Python 3, pandas, standard library pathlib/hashlib/datetime/csv/json, pytest.

**Spec:** `docs/superpowers/specs/2026-09-08-g2b-authoritative-raw-data-design.md`

## Global Constraints

- Base branch: `thesis/refinement`.
- Work in an isolated feature branch/worktree.
- Read `AGENTS.md`, `docs/thesis/CODEX_WORKFLOW.md`, the G2-B spec, and this plan before coding.
- No CIRD computation.
- No M1/M2 strategy panel.
- No Sharpe/CAGR/performance calculation.
- No hedge-ratio work.
- No full legacy-workbook reconciliation; that is G2-C.
- No paid VIX data acquisition; that is G2-B2.
- No silent price repair.
- No production code before a failing test.
- Unit tests must not depend on network access.
- Live download failures must be surfaced, not replaced with synthetic data.

---

### Task 1: Source manifest and immutable provenance

**Files:**
- Create: `src/vix_strategies/thesis/data_sources.py`
- Create: `tests/thesis/test_g2b_sources.py`
- Create: `data/manifests/.gitkeep` only if repository policy allows empty tracked directory

**Produces:**
- `SourceFamily`
- `SourceSpec`
- `SourceManifestRecord`
- `sha256_file(path: Path) -> str`
- `build_manifest_record(...) -> SourceManifestRecord`
- source-family constants for Cboe archive and current detail

- [ ] **Step 1: Write failing manifest/hash tests**

Create tests that:
- hash a known small fixture and assert exact SHA-256;
- require source URL, source family, retrieval timestamp, local path, checksum;
- reject a manifest record whose file checksum does not match the declared checksum.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_sources.py -v`

Expected: FAIL because G2-B source module does not exist.

- [ ] **Step 3: Implement minimal provenance primitives**

Implement immutable dataclasses/enums and checksum logic only.
Do not implement historical parsing yet.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_sources.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat: add G2-B source provenance manifest"`

---

### Task 2: Historical contract-calendar regimes

**Files:**
- Create: `src/vix_strategies/thesis/vx_calendar.py`
- Create: `tests/thesis/test_g2b_calendar.py`
- Reuse: `src/vix_strategies/thesis/contracts.py`

**Produces:**
- `SettlementRuleRegime`
- `SettlementDateValidationStatus`
- `ContractCalendarEntry`
- `compute_legacy_vx_settlement_date(...)`
- `compute_modern_vx_settlement_date(...)`
- `build_contract_calendar_entry(...)`

- [ ] **Step 1: Write failing tests for both rule regimes**

Tests must include:
- May 2004 contract => 2004-05-19 under the original rule;
- a representative post-2005 contract under the modern 30-day rule;
- 2005-10-17 effective-rule boundary classification;
- holiday-adjusted modern example;
- rejection of `rule_derived_unvalidated` when requesting primary-eligible calendar entries.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_calendar.py -v`

Expected: FAIL because regime-aware calendar module does not exist.

- [ ] **Step 3: Implement minimal calendar-regime API**

Do not overwrite G2-A helpers. Wrap/reuse the modern helper where correct and add explicit legacy logic.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_calendar.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat: add historical VX settlement regimes"`

---

### Task 3: Raw Cboe row parsing

**Files:**
- Create: `src/vix_strategies/thesis/vx_raw.py`
- Create: `tests/thesis/fixtures/g2b/archive_contract_sample.csv`
- Create: `tests/thesis/fixtures/g2b/current_detail_sample.csv`
- Create: `tests/thesis/test_g2b_raw_parsers.py`

**Produces:**
- `RawVxRecord`
- `parse_archive_contract_file(...)`
- `parse_current_detail_file(...)`
- parser-version constant(s)

- [ ] **Step 1: Create minimal source-shaped fixtures**

Fixtures must preserve the actual source-column names discovered from official Cboe files where known.
If current-detail column names cannot be verified from a source file, stop and report the missing schema instead of inventing it.

- [ ] **Step 2: Write failing parser tests**

Tests must assert:
- source values are preserved without normalization;
- source missing values remain missing;
- raw row IDs are deterministic;
- parser attaches source file/checksum lineage;
- malformed required fields fail loudly.

- [ ] **Step 3: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_raw_parsers.py -v`

Expected: FAIL because parser module does not exist.

- [ ] **Step 4: Implement minimal parsers**

Do not repair values.
Do not classify M1/M2.
Do not infer investment returns.

- [ ] **Step 5: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_raw_parsers.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

`git commit -m "feat: parse immutable Cboe VX source rows"`

---

### Task 4: Monthly-contract identity and universe filter

**Files:**
- Create: `src/vix_strategies/thesis/vx_universe.py`
- Create: `tests/thesis/test_g2b_universe.py`

**Produces:**
- `canonical_contract_id(year: int, month: int) -> str`
- `classify_vx_listing(...)`
- `is_primary_monthly_vx(...)`

- [ ] **Step 1: Write failing classification tests**

Tests must distinguish:
- standard monthly VX => eligible;
- weekly VX => excluded;
- VXM => excluded;
- TAS/VXT => excluded as a separate instrument/observation family;
- spreads/combinations => excluded.

Canonical ID test:
- March 2026 monthly VX => `VX_202603`.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_universe.py -v`

Expected: FAIL.

- [ ] **Step 3: Implement minimum identity/filter rules**

Where source metadata is insufficient to distinguish monthly vs weekly, require settlement-calendar evidence rather than symbol guessing.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_universe.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat: define canonical monthly VX universe"`

---

### Task 5: 2007 official normalization

**Files:**
- Create: `src/vix_strategies/thesis/vx_normalization.py`
- Create: `tests/thesis/test_g2b_normalization.py`

**Produces:**
- `PriceScaleRegime`
- `normalize_vx_price(trade_date, raw_price)`
- `source_multiplier_for_date(trade_date)`
- `normalization_factor_for_date(trade_date)`

- [ ] **Step 1: Write failing boundary tests**

Tests must assert:
- 2007-03-23: raw 103.90 -> normalized 10.39, source multiplier 100;
- 2007-03-26: raw 10.39 -> normalized 10.39, source multiplier 1000;
- dollar contract value is invariant in the example:
  `103.90 * 100 == 10.39 * 1000`;
- NaN/Infinity and non-positive price behavior is explicit and consistent with canonical policy.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_normalization.py -v`

Expected: FAIL.

- [ ] **Step 3: Implement only official exchange-wide normalization**

Do not add any heuristic scale detector.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_normalization.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat: encode official 2007 VX rescaling"`

---

### Task 6: Observation typing and canonical row construction

**Files:**
- Create: `src/vix_strategies/thesis/vx_canonical.py`
- Create: `tests/thesis/test_g2b_canonical.py`

**Consumes:**
- raw records
- contract calendar
- universe classification
- normalization

**Produces:**
- `ObservationType` with `DAILY_DSP`, `FINAL_SOQ`
- `SampleRole`
- `CanonicalVxRecord`
- `canonicalize_raw_record(...)`

- [ ] **Step 1: Write failing canonicalization tests**

Tests must assert:
- ordinary settlement row -> DAILY_DSP;
- final-settlement/SOQ row -> FINAL_SOQ;
- FINAL_SOQ is not marked ordinary curve eligible;
- trade_date <= 2026-05-01 -> development_contaminated;
- trade_date > 2026-05-01 -> post_freeze_holdout;
- canonical row keeps raw source lineage;
- official 2007 normalization is applied;
- missing settlement produces an explicit ineligible/quality state rather than forward-fill.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_canonical.py -v`

Expected: FAIL.

- [ ] **Step 3: Implement minimal canonicalization**

Do not build M1/M2.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_canonical.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat: build canonical VX contract-date records"`

---

### Task 7: Duplicate/conflict validator and holdout-safe access

**Files:**
- Create: `src/vix_strategies/thesis/vx_validation.py`
- Create: `tests/thesis/test_g2b_validation.py`

**Produces:**
- canonical key validator
- exact-duplicate handling
- conflict report object
- `development_rows(...)` default-safe accessor

- [ ] **Step 1: Write failing validation tests**

Tests must assert:
- uniqueness key = `(trade_date, contract_id, observation_type)`;
- identical duplicates can be deterministically collapsed and flagged;
- conflicting duplicates create an unresolved conflict and block acceptance;
- development accessor excludes post-2026-05-01 rows by default;
- caller must make an explicit opt-in to access holdout rows.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_validation.py -v`

Expected: FAIL.

- [ ] **Step 3: Implement validation and quarantine guard**

Do not introduce performance metrics.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_validation.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat: enforce G2-B data conflicts and holdout quarantine"`

---

### Task 8: Pipeline orchestration and reproducible outputs

**Files:**
- Create: `src/vix_strategies/thesis/vx_pipeline.py`
- Create: `tests/thesis/test_g2b_pipeline.py`
- Create: `scripts/build_g2b1_vx_canonical_panel.py`
- Create: `docs/thesis/G2B1_IMPLEMENTATION_STATUS.md`

**Produces:**
- pipeline from registered local raw source files to canonical records
- manifest output
- canonical dataset output
- conflict report
- run metadata

- [ ] **Step 1: Write failing end-to-end fixture test**

Use only fixture files.
Assert:
- raw manifest is emitted;
- canonical records are lineage-traceable;
- legacy/modern calendar regimes survive;
- pre/post-2007 normalization works;
- FINAL_SOQ is separated;
- no M1/M2 fields exist;
- holdout is labeled and excluded from development view;
- unresolved conflict makes pipeline status non-accepted.

- [ ] **Step 2: Verify RED**

Run:
`python -m pytest tests/thesis/test_g2b_pipeline.py -v`

Expected: FAIL.

- [ ] **Step 3: Implement minimal orchestration**

Output formats may be CSV/Parquet/JSON only if already available in the environment.
Do not add a new heavy dependency solely for storage.

- [ ] **Step 4: Verify GREEN**

Run:
`python -m pytest tests/thesis/test_g2b_pipeline.py -v`

Expected: PASS.

- [ ] **Step 5: Run all G2-B1 and existing thesis tests**

Run:
`python -m pytest tests/thesis -v`

Then:
`python -m pytest -v`

Record exact output.

- [ ] **Step 6: Scope scan**

Run:
`rg -n "Sharpe|CAGR|hedge.?ratio|M1|M2|CIRD|backtest|optimi[sz]" src/vix_strategies/thesis scripts/build_g2b1_vx_canonical_panel.py`

Review every match.
M1/M2/CIRD should appear only in comments/docs stating they are prohibited, not as produced data/logic.

- [ ] **Step 7: Commit**

`git commit -m "feat: assemble G2-B1 canonical VX data pipeline"`

---

### Task 9: Live-source smoke and handoff

**Files:**
- Modify: `docs/thesis/G2B1_IMPLEMENTATION_STATUS.md`
- Do not commit downloaded source binaries unless repository policy explicitly allows them

- [ ] **Step 1: Attempt official-source smoke retrieval**

Use the official Cboe source registry.

At minimum attempt one archive contract file from the public 2004–2013 archive.

If network access is unavailable:
- record the exact URL attempted;
- record the exact failure;
- do not fabricate successful ingestion;
- do not substitute legacy Excel as authoritative raw.

- [ ] **Step 2: If retrieval succeeds, run one-file real parse**

Confirm:
- source checksum;
- parsed row count;
- date range;
- source symbol;
- raw values unchanged;
- canonical normalization behavior if relevant.

- [ ] **Step 3: Do not run strategy analysis**

No maturity ranks, CIRD, returns, or performance.

- [ ] **Step 4: Final verification**

Run:
`python -m pytest -v`

Run:
`git diff --check origin/thesis/refinement..HEAD`

Record exact results.

- [ ] **Step 5: Handoff report**

PR body must include:
- files changed;
- commits;
- RED/GREEN evidence;
- full-suite result;
- live-source smoke result or exact network limitation;
- unresolved schema/source issues;
- confirmation that G2-B2 was not implemented.

## Self-review requirements

Before opening the PR, verify:

- every canonical row has raw provenance;
- no source file is modified in place;
- 2005 rule boundary is explicit;
- 2007 rescaling is explicit, not heuristic;
- FINAL_SOQ is distinct from DAILY_DSP;
- weekly/TAS/VXM/spreads are not silently admitted;
- holdout is inaccessible by default to development code;
- no M1/M2 panel is produced;
- no CIRD/backtest/performance code is introduced;
- no undocumented price correction exists;
- any missing official source schema is surfaced instead of guessed.

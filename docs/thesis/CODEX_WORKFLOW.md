# Codex Workflow for Thesis Implementation

## Division of labor

### ChatGPT research thread
Owns:
- research question,
- economic definitions,
- literature interpretation,
- statistical methodology,
- experiment governance,
- approval of specifications,
- interpretation of results,
- Notion research record.

### Codex
Owns:
- implementation from approved specs,
- tests,
- refactoring,
- reproducible notebooks/scripts,
- code review,
- verification evidence.

### GitHub
Shared handoff layer:
- binding methodology docs,
- approved specs,
- plans,
- source code,
- tests,
- generated reproducible artifacts.

## Standard handoff sequence

1. Research thread defines one narrow Gate/subtask.
2. Approved design is committed under `docs/superpowers/specs/`.
3. Implementation plan is committed under `docs/superpowers/plans/`.
4. Codex starts from `thesis/refinement` in an isolated branch/worktree.
5. Codex reads `AGENTS.md`, the spec, and the plan.
6. Codex implements with test-first workflow.
7. Codex reports test commands/results and opens a reviewable diff/PR.
8. Research thread reviews methodology-sensitive behavior and results.
9. Only approved changes are integrated into `thesis/refinement`.

## Rule

Codex is an implementer, not the authority for research design.

If a task requires choosing:
- a statistical estimator,
- a return definition,
- a sample split,
- an economic interpretation,
- a hedge objective,
- a curve boundary condition,

Codex should stop and surface the choice rather than infer it from performance.

## Current task boundary

The next coding task is **G2-A: CIRD/Data-Construction Core**.

The approved design is:
- contract-date primitive,
- official settlement date,
- calendar DTE,
- local price-DTE curve,
- VIX anchor at tau=0,
- exact roll-down/repricing decomposition,
- no rank-jump P&L.

Full Cboe historical ingestion is deliberately a separate later task.

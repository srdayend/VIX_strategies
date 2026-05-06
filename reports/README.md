# Reports

Generated analysis outputs, charts, and backtest result summaries should live here.

Use `reports/generated/` for machine-created files so source documents and generated artifacts stay separate.

## Expected Layout

```text
reports/generated/
  compare_065_vs_080_hedge_ratios/
  stop_loss_parameter_grid/
  regime_overlay_grid/
  reproduce_peer_research/
```

## Rules

- Do not put handwritten research notes in this folder. Use `docs/` for interpretation and conclusions.
- Keep generated CSVs, pivots, and tables under an experiment-specific subfolder.
- When a generated result becomes important, summarize the conclusion in `docs/` and link back to the generated files.
- Treat generated files as reproducible outputs from scripts in `src/vix_strategies/`.

## Current Generators

- `python -m src.vix_strategies.experiments.compare_065_vs_080_hedge_ratios`
- `python -m src.vix_strategies.experiments.stop_loss_parameter_grid`
- `python -m src.vix_strategies.experiments.regime_overlay_grid`
- `python -m src.vix_strategies.experiments.reproduce_peer_research`

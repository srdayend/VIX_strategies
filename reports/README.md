# Reports

This folder contains generated outputs from scripts in `src/vix_strategies/`.

Handwritten interpretation belongs in `docs/`. Generated CSVs and charts belong under `reports/generated/<experiment_name>/`.

## Current Output Folders

```text
reports/generated/
  reproduce_peer_research/
  vix_distribution_rolldown_hedge_ratio/
```

Some scripts listed in `docs/code_execution_guide.md` generate additional folders when run:

```text
compare_065_vs_080_hedge_ratios/
stop_loss_parameter_grid/
regime_overlay_grid/
```

## Primary Generated Outputs

For the latest baseline weight study, the script generates CSVs and charts under:

```text
reports/generated/vix_distribution_rolldown_hedge_ratio/
```

The most useful CSV outputs are:

```text
  vix_spot_distribution_stats.csv
  vix_spot_percentile_curve.csv
  term_structure_contango_backwardation_summary.csv
  adjacent_maturity_rolldown_summary.csv
  front_carry_by_hedge_ratio.csv
  vix_spike_hedge_ratio_summary.csv
  advanced_pnl_weight_grid.csv
  advanced_pnl_weight_summary.csv
```

The script also writes local chart PNGs:

```text
  vix_spot_percentile_curve.png
  term_structure_slope_profile.png
  term_structure_contango_heatmap.png
  adjacent_maturity_average_rolldown.png
  front_carry_by_hedge_ratio_curve.png
  vix_spike_vx2_vx1_hedge_ratio.png
  advanced_pnl_weight_grid_returns.png
  advanced_spike_pnl_by_weight.png
```

The CSV files preserve the underlying numbers used in the docs. The PNG files are reproducible local artifacts from the script.

## Reproducibility Rule

Generated files are reproducible outputs. If a generated result becomes important, summarize it in `docs/` and link back to the relevant files rather than editing generated CSVs manually.

# Logbook

Chronological record of work on the ADM-EC clock-consensus project. Each entry documents what was done, what was found, and what it means for the decision gates.

Entries are Markdown files named `NNN_YYYY-MM-DD_title.md`. Figures are stored in the `figures/` subdirectory.

| Entry | Date | Summary |
|-------|------|---------|
| [001](001_2026-03-31_ic-implementation-and-aipp-correction.md) | 2026-03-31 | IC implementation, AIPP null limit corrected from 0.55 to 1.25 bit |
| [002](002_2026-03-31_sigma-sensitivity-analysis.md) | 2026-03-31 | σ-sensitivity: systematic −20% fails 15% bound; proceed with worst-case calibration |
| [003](003_2026-03-31_powerlaw-nulls-and-finite-n-bias.md) | 2026-03-31 | Power-law, flicker, random-walk nulls all pass ×1.5; finite-N bias < 1% at N ≥ 75; DG-1 closed |
| [004](004_2026-03-31_delta-min-calibration.md) | 2026-03-31 | δ_min calibrated: var_slope 0.21, autocorr 0.87; classification rule complete; WP1 complete |
| [005](005_2026-04-01_positioning-ic-against-fom.md) | 2026-04-01 | IC positioned against χ², Huber, Allan deviation; property table; data infrastructure created |
| [006](006_2026-05-04_per-reading-threshold-recalibration.md) | 2026-05-04 | AIPP→per-reading threshold recalibration; operational WP2 threshold 2.976 bit (worst case), 1.62× the AIPP value it replaces; closes WP2-prerequisite open item |
| [007](007_2026-05-04_wp2-simulation-harness.md) | 2026-05-04 | WP2 simulation harness (8 scenarios × 10 seeds × 9 estimators); metrics module (MSE, collapse index, structure correlation); two bug fixes (`admec_full` t=0 init, FP variance-ratio guard); **DG-2 NOT MET** — only S2 wins on MSE |

## Summary

| Document | Scope |
|----------|-------|
| [WP1 Summary](wp1-summary.md) | Calibration and positioning of IC — what was defined, demonstrated, and not solved |
| [WP2 Summary](wp2-summary.md) | Network simulation, the negative DG-2 verdict, and the WP3 ablation framing scoped to characterise the failure mode |

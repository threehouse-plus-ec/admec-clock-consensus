# Data

Numerical output from each logbook entry, stored as compressed NumPy archives (`.npz`).

## Naming convention

`{entry_number}_{short_name}.npz` — one file per logbook entry.

## Seed convention

All data files use `np.random.default_rng(2026)` unless stated otherwise in the corresponding logbook entry.

## Files

| File | Entry | Description | Size |
|------|-------|-------------|------|
| `001_aipp_convergence.npz` | [001](../logbook/001_2026-03-31_ic-implementation-and-aipp-correction.md) | AIPP per N per realisation (14 sample sizes × 200 realisations); 95th-percentile thresholds for 5 noise models | 25 KB |
| `002_sigma_sensitivity.npz` | [002](../logbook/002_2026-03-31_sigma-sensitivity-analysis.md) | AIPP distributions under 4 perturbation conditions at N = 50 and N = 200 (300 realisations each) | 20 KB |
| `003_powerlaw_thresholds.npz` | [003](../logbook/003_2026-03-31_powerlaw-nulls-and-finite-n-bias.md) | AIPP distributions for all 10 null models (300 realisations); finite-N bias fit coefficients (a, b, AIPP_inf) | 26 KB |
| `004_delta_min.npz` | [004](../logbook/004_2026-03-31_delta-min-calibration.md) | Null distributions of variance slope and autocorrelation for all 10 models (300 realisations × T = 200); calibrated delta_min values; sanity-check signal arrays | 7.9 MB |
| `005_comparison_fom.npz` | [005](../logbook/005_2026-04-01_positioning-ic-against-fom.md) | Controlled comparison: 20 clocks × 200 steps; per-clock chi2, Huber, and IC arrays | 121 KB |

## Notes

- Entry 004 is the largest file (~8 MB) because it stores the full null distributions across all ten noise models. This is within the GitHub size limit but approaches the threshold where git-lfs or Zenodo hosting should be considered.
- WP2 simulation data (when generated) will likely exceed 5 MB per scenario. At that point, consider migrating to git-lfs or archiving on Zenodo with DOI.
- To load: `data = np.load('data/001_aipp_convergence.npz'); data['aipp_N50']` etc.
- Metadata fields (seed, n_realisations, etc.) are stored as scalar arrays within each .npz file.

## Regeneration

All data can be regenerated from the scripts in `scripts/`:

- Entries 001–004: `python scripts/save_wp1_data.py`
- Entry 005: `python scripts/fig07_comparison_fom.py`

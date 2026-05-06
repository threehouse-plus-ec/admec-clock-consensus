# Data

Numerical output from each logbook entry and campaign, stored as compressed NumPy archives (`.npz`).

## Phase namespaces

Archives use a phase prefix to keep work packages from different phases strictly separable. **Strictly additive separation** is a Phase-2 governance constraint (Phase-2 Projektantrag §0): a Phase-2 run must never overwrite or migrate a Phase-1 archive.

| Prefix | Phase | Purpose | Status |
|--------|-------|---------|--------|
| `00N_*.npz` | Phase 1 / WP1 | Per-logbook-entry archives for entries 001–006 (IC calibration). | Frozen — read-only artefact. |
| `wp2_*.npz` | Phase 1 / WP2 | Campaign harness; one canonical per scenario × seed × estimator. | Frozen — read-only artefact. |
| `wp3_*.npz` | Phase 1 / WP3 | Per-ablation archives for entries 008–012, plus integrated combined-tuning. | Frozen — read-only artefact. |
| `p2_continuity_*.npz` | Phase 2 | S1–S8 re-runs under Phase-2 harness for harness-drift sanity checks against `wp2_*` originals. | Reserved (no archives yet). |
| `p2_alpha0_*.npz` | Phase 2 | WP-α₀ per-noise-family Monte Carlo null distributions. | Reserved. |
| `p2_alpha_*.npz` | Phase 2 | WP-α STRUCTURED-channel separability diagnostic. | Reserved. |
| `p2_beta_*.npz` | Phase 2 | WP-β Cramér–Rao floors per (scenario, family). | Reserved. |
| `p2_gamma_*.npz` | Phase 2 | WP-γ α-rule campaign. | Reserved. |
| `p2_gamma_lite_*.npz` | Phase 2 | WP-γ-lite EXPLORATORY runs (only if triggered; tagged in archive metadata). | Reserved. |
| `p2_delta_*.npz` | Phase 2 | WP-δ λ-rule campaign. | Reserved. |
| `p2_epsilon_*.npz` | Phase 2 | WP-ε combined α + λ campaign (only opens if DG-γ PASS *and* DG-δ PASS). | Reserved. |

**Harness-drift checksum.** Every `p2_continuity_*` run must compute and log a checksum against the matching `wp2_*` archive; checksum drift is a parameters-layer / RNG-governance bug, not a Phase-2 result (Phase-2 Appendix A).

**Phase-1 archives are read-only artefacts in Phase 2.** Do not regenerate `wp2_*` or `wp3_*` archives from Phase-2 code; do not migrate them into a `p2_*` namespace.

## Naming convention

`{entry_number}_{short_name}.npz` — one file per Phase-1 logbook entry. Phase-2 archives use the `p2_<wp>_<descriptor>_<YYYYMMDD>.npz` pattern (mirrors `wp3_<descriptor>_<YYYYMMDD>.npz`).

## Seed convention

All Phase-1 data files use `np.random.default_rng(2026)` unless stated otherwise in the corresponding logbook entry. **Phase-2 seeding is governed by Phase-2 Projektantrag §10**: master seed S₀ from `secrets.randbits(64)` logged at campaign start; per-stream seeds derived as `SHA-256(S₀ ‖ family_name ‖ str(replicate) ‖ scenario_id)[:8] → uint64`. Phase-2 seed-stream metadata is required in every `p2_*` archive.

## Files

| File | Entry | Description | Size |
|------|-------|-------------|------|
| `001_aipp_convergence.npz` | [001](../logbook/001_2026-03-31_ic-implementation-and-aipp-correction.md) | AIPP per N per realisation (14 sample sizes × 200 realisations); 95th-percentile thresholds for 5 noise models | 25 KB |
| `002_sigma_sensitivity.npz` | [002](../logbook/002_2026-03-31_sigma-sensitivity-analysis.md) | AIPP distributions under 4 perturbation conditions at N = 50 and N = 200 (300 realisations each) | 20 KB |
| `003_powerlaw_thresholds.npz` | [003](../logbook/003_2026-03-31_powerlaw-nulls-and-finite-n-bias.md) | AIPP distributions for all 10 null models (300 realisations); finite-N bias fit coefficients (a, b, AIPP_inf) | 26 KB |
| `004_delta_min.npz` | [004](../logbook/004_2026-03-31_delta-min-calibration.md) | Null distributions of variance slope and autocorrelation for all 10 models (300 realisations × T = 200); calibrated delta_min values; sanity-check signal arrays | 7.9 MB |
| `005_comparison_fom.npz` | [005](../logbook/005_2026-04-01_positioning-ic-against-fom.md) | Controlled comparison: 20 clocks × 200 steps; per-clock chi2, Huber, and IC arrays | 121 KB |
| `006_per_reading_threshold.npz` | [006](../logbook/006_2026-05-04_per-reading-threshold-recalibration.md) | Per-reading I_k pools and 95th/99th percentiles across ten null models, both clean and -20% sigma worst case; operational WP2 threshold 2.976 bit | 2.2 MB |

## Notes

- Entry 004 is the largest file (~8 MB) because it stores the full null distributions across all ten noise models. This is within the GitHub size limit but approaches the threshold where git-lfs or Zenodo hosting should be considered.
- WP2 simulation data (when generated) will likely exceed 5 MB per scenario. At that point, consider migrating to git-lfs or archiving on Zenodo with DOI.
- To load: `data = np.load('data/001_aipp_convergence.npz'); data['aipp_N50']` etc.
- Metadata fields (seed, n_realisations, etc.) are stored as scalar arrays within each .npz file.

## Regeneration

All data can be regenerated from the scripts in `scripts/`:

- Entries 001–004: `python scripts/save_wp1_data.py`
- Entry 005: `python scripts/fig07_comparison_fom.py`
- Entry 006: `python scripts/fig08_per_reading_threshold.py`

# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] — 2026-05-04

### Added
- `src/clocks.py`: WP2 clock simulator. `ClockParams` dataclass; `simulate_clock` / `simulate_network_clocks`; signal generators `signal_sinusoidal`, `signal_linear_drift`, `signal_step`, `signal_fold_bifurcation` (S8); `hydrogen_maser` reference preset (Panfilo & Arias 2019); `build_scenario_clocks` composer for the eight WP2 scenarios.
- `src/network.py`: WP2 network topology + delay model. `make_ring`, `make_fully_connected`, `make_random_sparse` (k-regular spanning-tree heuristic, no networkx dependency); `sample_delays` (symmetric Poisson on edges); `make_network` dispatcher.
- `tests/test_clocks.py`: 21 tests covering noise levels, declared sigma, signal additivity for all four generators, heavy-tail behaviour, multi-clock simulation, hydrogen-maser preset, and the scenario builder.
- `tests/test_network.py`: 21 tests covering topology shapes, symmetry, connectivity, degree targets, delay symmetry/integer/edge-only/Poisson-mean behaviour, and the dispatcher.

### Status
- WP2 foundational modules (`clocks.py`, `network.py`) implemented. `classify.py`, `estimators.py`, `constraints.py` remain stubs.
- **149 tests total**, 147 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.3.2] — 2026-05-04

### Added
- `scripts/fig08_per_reading_threshold.py`: Per-reading I_k threshold calibration across the ten null noise models, with worst-case sigma recalibration (-20%)
- `data/006_per_reading_threshold.npz`: Per-reading I_k pools and percentiles for all ten null models, both clean and worst-case sigma regimes
- `tests/test_per_reading_threshold.py`: 19 tests covering the AIPP-vs-per-reading P95 ordering, ×1.5 stability across all ten noise models (clean and worst-case), worst-case inflation under sigma underestimation, and ×1.2 stability across N ∈ {50, 100, 200} for the operational threshold
- `logbook/`: Entry 006 (per-reading threshold recalibration; closes the WP2-prerequisite open item from `wp1-summary.md`)

### Changed
- `logbook/wp1-summary.md`: Open item on AIPP-to-per-reading threshold recalibration is closed; the operational WP2 threshold is 2.976 bit (worst case, heteroscedastic Gaussian), 1.62× the AIPP threshold it replaces
- `src/classify.py`: Stub docstring updated to reference the per-reading 2.976 bit threshold (Entry 006), distinguishing it from the AIPP-derived value of 1.835 bit

### Status
- WP1 → WP2 bridge. Does not modify DG-1 ruling. Resolves the only open item flagged for WP2 entry
- **107 tests total**, 105 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration)

## [0.3.1] — 2026-04-01

### Added
- `src/comparison.py`: Comparison figures of merit — `compute_chi2`, `compute_huber`, `compute_allan_deviation`
- `tests/test_comparison.py`: 12 tests for comparison functions and ordering consistency
- `scripts/fig07_comparison_fom.py`: Figure generation for Entry 005
- `scripts/save_wp1_data.py`: Retroactive data export for entries 001–004
- `data/`: Data directory with `.npz` archives for all five logbook entries
- `data/README.md`: Data naming conventions, contents, and regeneration instructions
- `logbook/`: Entry 005 (positioning IC against established figures of merit)

### Status
- **WP1 addendum.** Does not modify DG-1 ruling. Triggered by external review.
- **88 tests total**, 86 passing (2 known failures: systematic −20% σ-sensitivity).

## [0.3.0] — 2026-03-31

### Added
- `src/temporal.py`: Temporal-structure statistics — `compute_temporal_structure`, `calibrate_delta_min`
- `tests/test_temporal.py`: 13 tests for temporal statistics, δ_min calibration, and detectability
- `scripts/fig06_delta_min_calibration.py`: Figure generation script
- `logbook/`: Entry 004 (δ_min calibration)
- `docs/outreach.md`: Non-technical overview

### Changed
- `src/classify.py`: Stub updated to reflect calibrated thresholds (δ_min_var = 0.2105, δ_min_acf = 0.8703) and corrected classifier definition (plain lag-1 acf, not acf trend slope)
- `docs/projektantrag.md`: Classifier rule updated to match WP1 implementation (autocorrelation trend slope → plain lag-1 autocorrelation)
- `README.md`, `index.md`: DG-1 status now consistently reports the σ-sensitivity failure and mitigation

### Status
- **WP1: Complete.** All tasks done (entries 001–004). DG-1 closed with one recorded failure (systematic σ-underestimation, mitigated).
- **76 tests total**, 74 passing (2 known failures: systematic −20% σ-sensitivity).
- Three-way classification rule fully specified.

## [0.2.0] — 2026-03-31

### Added
- `src/ic.py`: IC implementation — `compute_ic`, `compute_aipp`, `compute_ti`, `aipp_gaussian_limit`, `perturb_sigmas`, `verify_sigmas`
- `src/noise.py`: Noise generators — `generate_pareto_symmetric`, `generate_flicker` (Davies-Harte fGn), `generate_random_walk`, `generate_ar1`
- `tests/test_ic.py`: 24 tests for IC computation, convergence, threshold stability, σ-verification
- `tests/test_sensitivity.py`: 17 tests for σ-sensitivity analysis (15 pass, 2 known failures — systematic −20% exceeds 15% bound)
- `tests/test_noise.py`: 15 tests for noise generators
- `tests/test_powerlaw_thresholds.py`: 7 tests for extended threshold stability and finite-N bias
- `scripts/fig04_sigma_sensitivity.py`, `scripts/fig05_powerlaw_thresholds.py`: Figure generation scripts
- `logbook/`: Entries 001–003 with figures (AIPP correction, σ-sensitivity, power-law nulls)
- `index.md`, `_config.yml`: GitHub Pages site (Jekyll, minimal theme)
- `.gitignore`

### Changed
- `docs/projektantrag.md`: Split from combined rebuttal+proposal into proposal-only (v0.5.3). AIPP target corrected from 0.55 to 1.25 bit. All labels switched to English.
- `docs/rebuttal.md`: Standalone rebuttal with proper title. Labels switched to English.
- `README.md`: Updated to reflect WP1 progress, DG-1 closure, test counts, and code status.

### Status
- **DG-1: Closed.** All criteria assessed. All pass except systematic σ-underestimation (−20%), which exceeds the pre-registered 15% bound. Mitigation: worst-case threshold calibration for WP2.
- **63 tests total**, 61 passing.
- Remaining WP1 item: effect-size threshold δ_min.

## [0.0.1] — 2026-03-30

### Added
- Repository structure: `src/`, `tests/`, `notebooks/`, `docs/`
- Stub modules for all six code components (ic, clocks, network, estimators, constraints, classify)
- Project proposal (`docs/projektantrag.md`, v0.5.2 frozen)
- Rebuttal to hostile internal review (`docs/rebuttal.md`)
- README with decision gates, timeline, and honest status reporting
- CITATION.cff
- MIT licence (code), CC BY 4.0 (docs)

### Status
- **No code was implemented.** All modules raised `NotImplementedError`.
- **No results existed.** The repository documented what would be built.

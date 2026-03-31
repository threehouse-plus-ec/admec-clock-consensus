# Changelog

All notable changes to this project will be documented in this file.

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

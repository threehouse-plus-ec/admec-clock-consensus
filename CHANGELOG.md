# Changelog

All notable changes to this project will be documented in this file.

## [0.7.0] — 2026-05-04

### Added
- `src/estimators.py`: `delay_mode` parameter on `freq_local`, `admec_delay`, and `admec_full`. `'drop'` (default) preserves the WP2 baseline; `'stale'` (WP3 ablation 1) pulls the delayed reading `Y[t − delays[i, j], j]` for every adjacency neighbour rather than dropping inaccessible ones.
- `scripts/wp3_ablation_delay_convention.py`: WP3 ablation 1 harness — runs S1, S2, S3 × 10 seeds × {drop, stale} on the three local estimators plus centralised baselines for direct comparison. Output: `data/wp3_ablation_delay_convention_YYYYMMDD.npz`. RNG ordering matched to `scripts/wp2_campaign.py` so drop-mode reproduces the WP2 canonical archive exactly.
- `data/wp3_ablation_delay_convention_20260504.npz`: ablation archive.
- `logbook/008_2026-05-04_wp3-ablation-delay-convention.md`: WP3 ablation-1 entry with finding, interpretation, and the unexpected `admec_delay > admec_full` on S3 stale (suggests WP3 ablation 3 — constraint sensitivity — as the next step).
- `tests/test_estimators.py`: 10 new tests under `TestDelayMode` (zero-delay equivalence, unknown-mode rejection, hand-constructed delayed-readings example, finiteness sweep).

### Findings
- Stale convention reduces `admec_full` MSE by **44 %** on S1 (0.732 → 0.413) and **38 %** on S3 (0.741 → 0.461). Structure correlation closes most of the gap to centralised baselines on S3 (0.887 → 0.949 vs `imm` 0.960).
- **DG-2 stays NOT MET under stale**: S1 admec_full 0.413 vs freq_exclude 0.135 (3.1× gap); S3 admec_full 0.461 vs imm 0.025 (18× gap). The WP2 verdict is robust to the delay convention.
- On S2, drop slightly beats stale (0.093 vs 0.104) because adjacency neighbours are already accessible at freshness=1 in dense topology.
- Unexpected: under stale, `admec_delay` beats `admec_full` on S3 MSE (0.340 vs 0.461) — suggests the variance-ratio constraint mis-fires when proposed updates are noisier (multiple stale lags). WP3 ablation 3 will quantify.

### Status
- WP3 ablation 1 of 5 complete. DG-2 robustly NOT MET across delay conventions. Next ablation: constraint sensitivity (#3) or classification threshold (#2).
- 271 tests / 269 passing (10 new `TestDelayMode` tests; 2 known WP1 failures from entry-002 σ-underestimation, mitigated).

## [0.6.1] — 2026-05-04

### Fixed
- `src/constraints.py:is_feasible`: matched the FP guard in `project_update` (`var_before > 1e-20` rather than `> 0`). Previously the two functions disagreed on near-uniform states because `np.var` of a constant array returns ~3e-33: `is_feasible` would mark a small update as infeasible while `project_update` would accept it. Added regression test `test_constant_state_agrees_with_project_update`.
- `logbook/007_2026-05-04_wp2-simulation-harness.md`: corrected the S1 / S3 DG-2 result tables to match the canonical archive — S1 collapse-index `0.622 → 0.644` and structure-correlation `0.899 → 0.897`; S3 collapse-index baseline `freq_exclude → imm`, value `0.820 → 0.808`; S3 structure-correlation baseline `imm 0.952 → 0.960` and admec_full `0.795 → 0.887`. Verdict (NOT MET, S1 = 0/3, S3 = 0/3) is unchanged.
- `logbook/007*.md` and `logbook/wp2-summary.md`: re-derived DG-2b classification metrics with `scripts/wp2_classification_check.py` (now in the repository). Reports both "all 8 scenarios" (TPR 0.432, FPR 0.010, precision 0.767, F1 0.553) and "signal scenarios only" (precision 0.834, F1 0.569). Strict STRUCTURED-only TPR ≈ 0.007. The earlier `0.808 / 0.590` figures were from a separate aggregation that is no longer in the repository; the current values are reproducible from a checked-in script.
- `logbook/007*.md`: structure-correlation table now reports `freq_local` as a mean over the finite-seed subset with explicit seed counts (`0.598 (8/10 seeds)`, etc.) rather than as `NaN`. The collapse-to-zero residual on signal-bearing nodes leaves the Pearson r undefined on a subset of seeds, but the mean over the finite seeds is still informative.

### Added
- `scripts/wp2_classification_check.py`: reproducible DG-2b recomputation. Mirrors the campaign loop and reports `classification_metrics` for both "all scenarios" and "signal scenarios only" denominators, plus the strict STRUCTURED-only TPR.

### Status
- 261 tests / 259 passing (one new regression test for the `is_feasible` FP guard; 2 known WP1 failures from entry-002 σ-underestimation, mitigated).

## [0.6.0] — 2026-05-04

### Added
- `logbook/wp2-summary.md`: WP2 summary document parallel to `wp1-summary.md`. Records the closure of WP2, the negative DG-2 verdict, the structural failure mode (delay-restricted local consensus on sparse networks), and the WP3 ablation framing scoped to *characterise* the failure rather than rescue DG-2.
- `notebooks/wp2_tutorial.ipynb`: WP2 tutorial mirroring the WP1 pattern. Builds a 15-clock ring scenario, computes cross-sectional IC and the three-way classifier output, runs eight estimators, computes the three IC-independent metrics, then loads the canonical campaign archive and reproduces the DG-2 verdict (NOT MET, S1 = 0/3, S3 = 0/3).
- `docs/wp2_tutorial.md`: Rendered markdown twin of the tutorial with figures under `docs/wp2_tutorial_files/`, mirroring `docs/wp1_tutorial.md` so the tutorial is browsable on GitHub Pages without running Python.

### Changed
- `logbook/007_2026-05-04_wp2-simulation-harness.md`: corrected MSE / collapse-index / structure-correlation tables to match the canonical `data/wp2_campaign_20260504_fix.npz`. The earlier draft had carried over a few values from a pre-fix dry run; in particular the claim that `admec_full` "wins on S2, S7, S8" was wrong — only **S2** beats the best non-ADMEC baseline on MSE. The DG-2 verdict (NOT MET, S1 = 0/3, S3 = 0/3) is unchanged. Mitigating-factors section rewritten accordingly.

### Status
- WP2 closed. **DG-2 NOT MET** (negative result, recorded as anticipated by the proposal). DG-2b strict-three-way TPR ≈ 0.7 % (also not met). The constraint layer beats `admec_delay` on every scenario but cannot close the gap to centralised exclusion methods on sparse-with-delay topologies.
- WP3 ablations now scoped to characterise the failure mode (delay convention, classification threshold, constraint sensitivity, two-vs-three-way, ADMEC-full-lagged).
- 261 tests / 259 passing (unchanged; 2 known WP1 failures from entry-002 σ-underestimation, mitigated by worst-case threshold calibration in entry 006).

## [0.5.3] — 2026-05-04

### Added
- `src/metrics.py`: IC-independent performance metrics for WP2 campaign. `mse(estimates, reference=0.0)` — mean squared error vs nominal frequency. `collapse_index(estimates, sigmas)` — time-averaged `std(estimates)/mean(sigma)`; 0 for centralised estimators, >0 for local estimators that preserve per-node diversity. `structure_correlation(Y, estimates, signals, signal_clocks, onset_idx)` — Pearson r between (reading−estimate) and injected signal, averaged over signal clocks post-onset; high = estimator preserved structure rather than absorbing it. `classification_metrics(excluded, true_anomalous)` — TPR/FPR/precision/F1 for DG-2b validation against designer-injected ground truth.
- `scripts/wp2_campaign.py`: Full WP2 simulation harness. Defines all 8 proposal scenarios (S1–S8) with signal parameters chosen in unit scale (sigma_white=1.0): sinusoidal amplitude 5.0, step magnitude 5.0, linear drift rate 0.01/step, fold bifurcation epsilon=0.005/r0=-1.0 (empirically tuned to avoid Euler blow-up). Runs `(scenario, seed, estimator)` triples, computes the three primary metrics, and writes a compressed `.npz`. `--smoke` flag for quick validation (2 scenarios, 2 seeds, T=50).
- `tests/test_metrics.py`: 15 tests covering MSE, collapse-index scale invariance, structure-correlation perfect/zero/constant-residual edge cases, and classification-metric contingency tables.

### Fixed
- `src/estimators.py:admec_full`: t=0 initialization changed from `estimates[0, :] = Y[0, :]` (raw readings) to the centralised inverse-variance weighted mean. The old initialization caused the variance-ratio constraint (`var_after/var_before ∈ [0.5, 1.5]`) to reject *every* update, freezing estimates at the t=0 raw readings. MSE on S2 (fully connected) dropped from **4.85 to 0.13**; on S1 (ring) from **1.50 to 0.64**.

### Status
- **256 tests total**, 254 passing (2 known failures: entry-002 sigma-sensitivity).
- WP2 simulation campaign is ready to launch.

## [0.5.2] — 2026-05-04

### Added
- `src/estimators.py:imm_per_node`: Two-mode IMM filter (Blom & Bar-Shalom 1988). Per-node Kalman bank with shared observation model y = mu + N(0, sigma^2) and two process-noise levels — nominal (`sigma_walk_nominal = 0.01 × mean(sigmas)`) and anomalous (`sigma_walk_anomalous = 0.1 × mean(sigmas)`). Q ratio of 100× sits in the upper end of the 10×–100× sweet spot (smaller ratios collapse both filters; larger ratios let the anomalous mode "explain" any null noise as a true mean shift). Symmetric Markov transition `P(j → k ≠ j) = p_switch = 0.05`; the proposal evaluates `p_switch ∈ {0.01, 0.05, 0.1}`. Returns `(mode_probs (T, 2), estimates (T,))`.
- `src/estimators.py:imm_excluded`: per-step exclusion mask — True when the anomalous-mode posterior exceeds `anomalous_threshold = 0.7`. Empirically chosen: under the Gaussian null with default Q ratio, the anomalous posterior never crosses 0.7 (~0% false-positive rate over 50 random seeds); a clean 5σ step is detected with 1-2 step lag.
- `src/estimators.py:imm`: centralised consensus via IMM-based per-node exclusion — same overall structure as `bocpd`, with the same `t=0` centralised-mean fallback.
- `tests/test_estimators.py`: 12 new IMM tests covering shape and normalisation, low anomalous probability under null, step detection within 5 steps, drift detection, exclusion-mask behaviour (post-step and null), centralised consistency across all nodes, step suppression on a network, parameter validation.

### Changed
- `ESTIMATORS` registry now exposes all 9 of 9 estimators (`imm` added).

### Status
- **WP2 modules complete**: `clocks.py`, `network.py`, `classify.py`, `constraints.py`, `estimators.py` (9/9). The simulation harness can now begin.
- **241 tests total**, 239 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.5.1] — 2026-05-04

### Added
- `src/estimators.py:bocpd_run_length_posterior`: Adams & MacKay 2007 Bayesian online changepoint detection in log-space, with message-passing truncation at `r_max` (default 200) keeping per-step cost O(r_max). Gaussian observations with known per-sample sigma; Gaussian prior on the segment mean (default weakly informative). Constant hazard h(r) = 1/`hazard_lambda`.
- `src/estimators.py:bocpd_excluded`: per-node exclusion mask — True when MAP run-length is below `min_run_keep` (default 10), interpreting the proposal's "post-changepoint nodes excluded" rule.
- `src/estimators.py:bocpd`: centralised consensus estimator using inverse-variance weighted mean over non-excluded nodes. Carries previous estimate forward when all nodes are excluded; uses an all-nodes weighted-mean fallback at t=0 (BOCPD's MAP run-length always starts at 1, so the first step is excluded by construction).
- `tests/test_estimators.py`: 11 new tests for BOCPD covering posterior shape and normalisation, MAP-run-length growth under null, MAP collapse around a step changepoint, exclusion-mask behaviour with one-or-two-step detection lag, centralised-consistency across all nodes, and step suppression on a network with one stepped clock.

### Changed
- `src/estimators.py`: Added documentation comments to `freq_local`, `admec_delay`, and `admec_full` clarifying that delay-inaccessible neighbours are dropped (not pulled from history). Stale-reading variants are deferred to WP3 ablations per user-feedback after batch (a) review.
- `ESTIMATORS` registry now exposes 8 of 9 entries (`bocpd` added).

### Status
- WP2 modules `clocks.py`, `network.py`, `classify.py`, `constraints.py`, and `estimators.py` (8/9). Only IMM remains.
- **229 tests total**, 227 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.5.0] — 2026-05-04

### Added
- `src/estimators.py`: WP2 batch (a) — seven of nine consensus estimators sharing a common `(Y, Sigmas, adj, delays, **kwargs) -> Estimates(T, N)` interface.
  - **FREQ-global**: inverse-variance weighted mean over all nodes per step.
  - **FREQ-local**: per-node weighted mean over delay-accessible neighbours plus self (configurable `freshness` window).
  - **FREQ-exclude**: centralised mean excluding nodes with cross-sectional per-reading IC ≥ `THRESHOLD_95`.
  - **Huber**: IRLS M-estimator with default tuning constant `c = 1.345`; the proposal evaluates `c ∈ {1.0, 1.345, 2.0}` on null scenarios and fixes the best.
  - **ADMEC-unconstrained**: cross-sectional IC + longitudinal temporal stats → three-way classifier; centralised weighted mean over STABLE nodes only (STRUCTURED nodes "tracked and gated", not absorbed; UNSTRUCTURED excluded).
  - **ADMEC-delay**: per-node weighted mean over delay-accessible STABLE neighbours.
  - **ADMEC-full**: ADMEC-delay + sequential constraint projection on the per-node update vector via `src/constraints.py:project_update`.
- Module-level `ESTIMATORS` registry maps method names to callables, ready for the WP2 simulation harness.
- `tests/test_estimators.py`: 27 tests covering shape, dtype, registry membership, finiteness across all seven methods on a clean ring topology, plus per-method correctness checks (variance reduction, outlier exclusion, Huber robustness, full topology equivalence between ADMEC-delay and ADMEC-unconstrained, constraint smoothing under tight variance bounds).

### Status
- WP2 modules `clocks.py`, `network.py`, `classify.py`, `constraints.py`, and `estimators.py` (7/9) implemented. BOCPD and IMM are deferred to the next batch.
- **218 tests total**, 216 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.4.2] — 2026-05-04

### Added
- `src/constraints.py`: Update-size projector for ADMEC-full. `ConstraintParams` dataclass (defaults match proposal spec: max_step_factor=3, energy_factor=1, var_ratio in [0.5, 1.5]); `project_update(state, proposed_update, sigmas)` performs sequential projection (per-node box → energy ball → variance-ratio rejection fallback) and returns (filtered_update, status); `is_feasible` diagnostic helper.
- `tests/test_constraints.py`: 19 tests covering passthrough, box clipping (per-node and per-sigma-vector), energy scaling, variance-ratio rejection (collapsing and inflating), variance-neutral updates, edge cases (scalar sigma, negative sigma, shape mismatch, constant state), `is_feasible` paths, and a sequential-projection feasibility sweep.

### Status
- WP2 modules implemented: `clocks.py`, `network.py`, `classify.py`, `constraints.py`. Only `estimators.py` remains a stub.
- **191 tests total**, 189 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.4.1] — 2026-05-04

### Added
- `src/classify.py`: Three-way classifier wired with calibrated default thresholds (`THRESHOLD_95 = 2.976`, `DELTA_MIN_VAR = 0.2105`, `DELTA_MIN_ACF = 0.8703`) from entries 004 and 006. `Mode` IntEnum (UNDEFINED/STABLE/STRUCTURED/UNSTRUCTURED), `classify_node` (scalar), `classify_array` (vectorised), `classify_series` (single-clock end-to-end), `classify_network` (T×N matrix), `mode_counts` summary helper.
- `tests/test_classify.py`: 23 tests covering default values, all branches of the three-way rule, NaN handling, vectorisation parity, end-to-end behaviour on a Gaussian null and on a heavy-tailed clock, network shape and per-clock independence, and the documented blind spot for linear drift.

### Notes
- Two empirical observations baked into the classifier docstring: (1) linear drift below ~sigma/W classifies as UNSTRUCTURED, since the temporal-structure heuristic is calibrated for critical-slowing-down dynamics; (2) the per-reading IC threshold of 2.976 bit is selective — coherent processes (high-rho AR(1), smooth drifts) broaden the mixture density along with the readings and do not reliably cross it. Crossing typically requires isolated extreme readings. Which scenarios populate STRUCTURED vs UNSTRUCTURED in practice is a WP2 question.

### Status
- WP2 modules implemented: `clocks.py`, `network.py`, `classify.py`. `estimators.py` and `constraints.py` remain stubs.
- **172 tests total**, 170 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

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

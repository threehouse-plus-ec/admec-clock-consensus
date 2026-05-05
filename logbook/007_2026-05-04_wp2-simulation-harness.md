# Logbook Entry 007 — WP2 Simulation Harness, ADMEC-Full Bug Fix & DG-2 Verdict

**Date:** 2026-05-04  
**Work package:** WP2  
**Decision gate:** DG-2 (final)

---

## Objective

Build the end-to-end simulation harness that wires `clocks → network → estimators → metrics` for the 8-scenario × 10-seed × 9-estimator WP2 campaign. Run the campaign, diagnose bugs, fix them, re-run, and deliver a DG-2 verdict on whether ADMEC-full outperforms the best non-ADMEC baseline on ≥2 IC-independent metrics in S1 and S3.

---

## What was done

### 1. Metrics module (`src/metrics.py`)

Implemented the three primary WP2 metrics plus DG-2b classification diagnostics:

- **`mse(estimates, reference=0.0)`** — mean squared error against the nominal reference frequency (0 for fractional-frequency residuals).
- **`collapse_index(estimates, sigmas)`** — time-averaged `std_i(estimates[t,i]) / mean_i(sigma[t,i])`. Measures variance preservation: 0 for fully centralised estimators, > 0 for local estimators that retain per-node diversity.
- **`structure_correlation(Y, estimates, signals, signal_clocks, onset_idx)`** — Pearson r between `(reading − estimate)` and the injected true signal, averaged over signal clocks after onset. High = the estimator preserved the signal in the residual (did not absorb it into the consensus); low = the signal was suppressed.
- **`classification_metrics(excluded, true_anomalous)`** — TPR/FPR/precision/F1 for estimators that produce exclusion masks, evaluated against designer-injected ground truth.

All four functions are tested in `tests/test_metrics.py` (15 tests, all passing).

### 2. Campaign script (`scripts/wp2_campaign.py`)

The script defines the 8 proposal scenarios verbatim:

| Scenario | N | Topology | Delay mean | Signal | Purpose |
|----------|---|----------|-----------|--------|---------|
| S1 | 15 | ring | Poisson(2.0) | sinusoidal, 3 clocks | Structure preservation |
| S2 | 15 | fully_connected | Poisson(0.3) | sinusoidal, 3 clocks | Control (negligible delay) |
| S3 | 50 | random_sparse | Poisson(4.0) | sinusoidal, 3 clocks | Scaling |
| S4 | 15 | ring | Poisson(2.0) | none | Null |
| S5 | 50 | random_sparse | Poisson(4.0) | none | Null at scale |
| S6 | 15 | ring | Poisson(2.0) | linear drift, 2 clocks | Anomaly detection (not near-critical) |
| S7 | 30 | ring | Poisson(2.0) | step, 3 clocks at T/2 | Change-point detection |
| S8 | 15 | ring | Poisson(2.0) | fold bifurcation, 2 clocks | Near-critical dynamics |

Signal amplitudes are set in unit scale (`sigma_white = 1.0`):
- Sinusoidal: amplitude = 5.0 (5σ)
- Step: magnitude = 5.0 (5σ)
- Linear drift: rate = 0.01/step (2σ total over T=200)
- Fold bifurcation: `epsilon = 0.005, r0 = -1.0` — chosen empirically to approach the bifurcation within T=200 without Euler blow-up

The campaign loop runs every `(scenario, seed, estimator)` combination, computes metrics, and writes a compressed `.npz` archive. A `--smoke` flag runs a minimal subset (2 scenarios, 2 seeds) for quick validation.

### 3. Critical bug fix: `admec_full` initialization

**Discovery:** The smoke test revealed `admec_full` MSE was ~4.85 on S2 (fully connected, negligible delay) — more than 40× worse than `admec_delay` (~0.12) and 20× worse than `freq_global` (~0.24).

**Root cause:** `admec_full` initialized `estimates[0, :] = Y[0, :]` (raw readings). At `t=1` the proposed update moves from the high-variance raw readings toward the low-variance consensus target. The variance-ratio constraint in `project_update` (`var_after / var_before ∈ [0.5, 1.5]`) saw a ratio far below 0.5 and **rejected every update**. Estimates were frozen at `Y[0, :]` for all time, producing MSE equal to the mean squared reading at `t=0`.

**Fix:** Initialize `estimates[0, :]` to the centralised inverse-variance weighted mean instead of raw readings:

```python
m0 = _weighted_mean(Y[0, :], Sigmas[0, :])
estimates[0, :] = m0 if not np.isnan(m0) else 0.0
```

This gives `var_before = 0` on the first projection step, which skips the variance-ratio check (handled safely by existing logic in `constraints.py`). Subsequent steps evolve from a genuine consensus state, and the ratio constraint behaves as designed.

**Verification:** After the fix, smoke-test MSE for `admec_full` dropped from **4.85 → 0.13** on S2 and from **1.50 → 0.64** on S1 (ring topology, where delay sparsity makes the constraint active legitimately).

### 4. Floating-point bug in variance-ratio constraint

**Symptom:** The first full campaign (`data/wp2_campaign_20260504_full.npz`) showed `admec_full` S2 MSE = 0.269 — 2× worse than the best baseline (0.135). Dense networks (fully connected) showed 93–100% rejection rates; sparse networks showed ~40%.

**Root cause:** `np.var(state)` on a constant array returns `~3e-33` rather than exactly `0.0`. The `project_update` function checked `if var_before > 0`, entered the variance-ratio block, and computed `var_after / var_before`. With a near-zero denominator and a normal numerator, the ratio explodes to `~1e30`. The upper bound (`1.5`) triggers, rejecting **every** update on dense networks where the consensus state is uniform.

**Fix:** `src/constraints.py` line 136 changed from `if var_before > 0:` to `if var_before > 1e-20:`. This treats floating-point noise as zero, correctly skipping the variance-ratio check for uniform states.

**Verification:**
- New regression test `test_constant_state_nonzero_update_passes` in `tests/test_constraints.py` asserts that a non-zero update on a constant state is not rejected.
- S2 MSE (10-seed average) dropped from **0.269 → 0.093**, beating `freq_exclude` (0.135).
- S1 MSE is **0.732** (better than admec_delay 1.647, worse than freq_exclude 0.135).
- S3 MSE is **0.741** (better than admec_delay 2.002, worse than freq_exclude 0.025).

The full campaign was re-run after this fix (`data/wp2_campaign_20260504_fix.npz`).

---

## Full campaign results (post-fix, 10 seeds, T=200)

Re-derived 2026-05-04 directly from `data/wp2_campaign_20260504_fix.npz` after
the FP-guard fix. The earlier draft of this entry contained MSE values for
S3/S7/S8 carried over from a pre-fix dry run; those have been replaced below
and the "Observations" section corrected accordingly.

Mean MSE per scenario, **best non-ADMEC baseline bolded**:

| Scenario | freq_global | freq_local | freq_exclude | huber | bocpd | imm | admec_unc | admec_delay | admec_full |
|----------|------------:|-----------:|-------------:|------:|------:|----:|----------:|------------:|-----------:|
| S1 | 0.323 | 3.084 | **0.135** | 0.145 | 0.224 | 0.147 | 0.135 | 1.647 | 0.732 |
| S2 | 0.323 | 0.331 | 0.135 | 0.145 | 0.224 | 0.147 | 0.135 | 0.139 | **0.093** ✓ |
| S3 | 0.041 | 1.642 | **0.025** | 0.026 | 0.033 | 0.025 | 0.025 | 1.027 | 0.741 |
| S4 | 0.071 | 0.968 | 0.074 | 0.073 | 0.069 | **0.065** | 0.074 | 0.851 | 0.381 |
| S5 | 0.021 | 0.988 | 0.022 | 0.022 | 0.021 | **0.019** | 0.022 | 0.883 | 0.597 |
| S6 | 0.092 | 1.134 | 0.094 | 0.090 | 0.091 | **0.087** | 0.094 | 0.981 | 0.427 |
| S7 | 0.163 | 2.072 | **0.040** | 0.054 | 0.152 | 0.144 | 0.040 | 0.957 | 0.604 |
| S8 | 0.083 | 1.032 | 0.088 | 0.084 | 0.082 | **0.079** | 0.088 | 0.911 | 0.482 |

`✓` marks the only scenario where `admec_full` beats the best non-ADMEC baseline on MSE.

Mean collapse index per scenario (centralised estimators all = 0.000; only the
spread-preserving methods are shown):

| Scenario | freq_local | admec_delay | admec_full |
|----------|-----------:|------------:|-----------:|
| S1 | 1.430 | 1.030 | 0.644 |
| S2 | 0.072 | 0.046 | 0.022 |
| S3 | 1.208 | 0.954 | 0.808 |
| S4 | 0.784 | 0.740 | 0.480 |
| S5 | 0.935 | 0.885 | 0.723 |
| S6 | 0.849 | 0.793 | 0.491 |
| S7 | 1.213 | 0.869 | 0.684 |
| S8 | 0.809 | 0.763 | 0.539 |

`admec_full` always has lower (better) collapse index than `admec_delay`,
confirming the constraint layer suppresses spurious per-node disagreement.

Mean structure correlation, signal scenarios only. `freq_local` entries
are means over the finite-seed subset (some seeds collapse to a constant
residual on signal-bearing nodes, giving an undefined Pearson r):

| Scenario | freq_global | freq_local | freq_exclude | huber | bocpd | imm | admec_unc | admec_delay | admec_full |
|----------|------------:|--------------------:|-------------:|------:|------:|----:|----------:|------------:|-----------:|
| S1 | 0.951 | 0.598 (8/10 seeds)  | 0.955 | 0.955 | 0.952 | **0.956** | 0.955 | 0.800 | 0.897 |
| S2 | 0.951 | 0.951 (10/10 seeds) | 0.955 | 0.955 | 0.952 | 0.956 | 0.955 | 0.954 | **0.958** ✓ |
| S3 | 0.959 | 0.884 (7/10 seeds)  | 0.960 | 0.960 | 0.960 | **0.960** | 0.960 | 0.866 | 0.887 |
| S6 | 0.455 | 0.200 (7/10 seeds)  | 0.458 | **0.460** | 0.454 | 0.447 | 0.458 | 0.175 | 0.312 |
| S7 | 0.901 | 0.093 (10/10 seeds) | **1.002** | 0.967 | 0.910 | 0.914 | 1.002 | 0.713 | 0.835 |
| S8 | 0.205 | 0.083 (7/10 seeds)  | 0.204 | **0.204** | 0.205 | 0.197 | 0.204 | 0.075 | 0.113 |

`freq_local` collapses to a constant per-node residual on a subset of
seeds because, on a sparse delay-accessible neighbourhood, each node's
estimate frequently equals its own reading exactly — making
`reading − estimate ≡ 0` and the Pearson correlation undefined. The
table reports the mean over the finite-seed subset and the seed count
explicitly, rather than dropping the column. S6 and S8 have low absolute
correlation across all methods because the injected signals (slow drift;
pre-bifurcation creep) sit close to the noise floor over T = 200; this
is a property of the scenarios, not of the estimators.

S7's `freq_exclude` value of 1.002 (and `admec_unconstrained` 1.002)
sits slightly above 1.0 because for the constant post-step signal the
correlation function falls back to a residual-magnitude ratio; values
near 1 indicate that the consensus left the entire 5σ step in the
residual rather than absorbing it. The `freq_local` value of 0.093 for
S7 is finite (10/10 seeds) but small because in the ring topology with
delay 2 each node mixes its own stepped reading with non-stepped
neighbours, partly absorbing the step.

`admec_full` does not beat the best non-ADMEC baseline on structure
correlation in any scenario except **S2**.

### Observations

- **S2 (fully connected, low delay) is the only signal scenario where
  `admec_full` wins.** It achieves the best MSE (0.093 vs `freq_exclude`
  0.135), the best collapse index (0.022), and the best structure
  correlation (0.958). The constraint layer adds ~30 % MSE improvement over
  unconstrained centralised methods when delays do not starve the local
  consensus.
- **`freq_exclude` is the strongest non-ADMEC baseline on signal MSE**
  (S1, S3, S7); `imm` wins the null and slow-drift scenarios (S4, S5, S6,
  S8). Both are centralised, exclusion-style estimators. `freq_exclude`
  is mathematically identical to `admec_unconstrained` because, in these
  scenarios, the IC-based exclusion and the temporal-statistic exclusion
  rarely differ at the per-reading level (cf. entry 006 docstring on the
  selectivity of the per-reading 2.976-bit threshold).
- **On S1 and S3 (sparse with Poisson delays) `admec_full` cannot beat
  `freq_exclude`.** It improves substantially over `admec_delay`
  (S1: 0.732 vs 1.647; S3: 0.741 vs 1.027) but the gap to a centralised
  baseline remains ≈ 5 × on S1 and ≈ 30 × on S3. The delay-accessible
  neighbourhood is too small (1–2 nodes on average) to form a stable
  local consensus; the constraint layer limits step size but cannot
  compensate for missing neighbours.
- **The constraint layer is internally consistent.** `admec_full` beats
  `admec_delay` on MSE, collapse index, and structure correlation in
  every scenario tested. The anomaly is the gap to centralised methods,
  not the constraint architecture itself.
- **`admec_full` does not beat baselines on S7 (step) or S8 (fold
  bifurcation).** An earlier draft of this entry reported wins on these
  scenarios; that was an artefact of a pre-fix campaign run and has been
  corrected. The current data shows `freq_exclude` (S7) and `imm` (S8)
  as the leaders.

---

## DG-2 verdict

**DG-2 condition:** ADMEC-full must outperform the best non-ADMEC baseline (freq-global/local/exclude, Huber, BOCPD, or IMM) on ≥2 of {MSE, collapse index, structure correlation} in **both** S1 and S3.

### S1 (ring, 15 nodes, Poisson(2.0), sinusoidal)

| Metric | Best baseline | admec_full | Pass? |
|--------|--------------|------------|-------|
| MSE | freq_exclude = 0.135 | 0.732 | ❌ FAIL |
| Collapse index | freq_exclude = 0.000 | 0.644 | ❌ FAIL |
| Structure correlation | imm = 0.956 | 0.897 | ❌ FAIL |

**S1 result: 0/3 metrics pass.**

### S3 (random sparse, 50 nodes, Poisson(4.0), sinusoidal)

| Metric | Best baseline | admec_full | Pass? |
|--------|--------------|------------|-------|
| MSE | freq_exclude = 0.025 | 0.741 | ❌ FAIL |
| Collapse index | imm = 0.000 | 0.808 | ❌ FAIL |
| Structure correlation | imm = 0.960 | 0.887 | ❌ FAIL |

**S3 result: 0/3 metrics pass.**

### Verdict: **DG-2 NOT MET.**

`admec_full` does not beat the best non-ADMEC baseline on ≥2 metrics in either S1 or S3. The failure mode is structural: on sparse networks with realistic delays, the delay-accessible neighbourhood is too small to support a local consensus that outperforms a centralised inverse-variance weighted mean. The constraint layer improves over `admec_delay` but cannot close the gap to `freq_exclude`.

**Of the eight scenarios, `admec_full` beats the best non-ADMEC baseline on
MSE in only one — S2 (fully connected, Poisson(0.3))**, where the
delay-accessibility constraint is essentially inactive.

**Mitigating context (does not rescue DG-2 but informs WP3 design):**
- The constraint layer improves on `admec_delay` everywhere — MSE, collapse
  index, and structure correlation are all reduced by the projection step.
  The architecture is internally coherent; the deficit is in the
  delay-restricted local consensus, not the constraint layer.
- The delay convention (drop neighbours with delay > freshness, do not use
  stale readings) is a known limitation flagged in the docstrings of
  `freq_local`, `admec_delay`, and `admec_full`. **WP3 ablation 1**
  (delay convention) is the principled test of whether stale-reading
  variants close the gap.
- The classification layer behaves as designed but is rarely the binding
  constraint: under the Gaussian-null sigma-perturbation regime that
  WP1 calibrated for, the per-reading 2.976-bit IC threshold is
  selective, so on most scenarios `freq_exclude` and `admec_unconstrained`
  produce nearly identical exclusion masks. **WP3 ablation 2**
  (classification threshold sweep) is the direct test of this.
- The proposal anticipated a negative DG-2 outcome ("If it fails, the
  contribution is a careful negative result showing that established
  robust methods are sufficient for the tested regime").

---

## DG-2b classification validation

Recomputed reproducibly from `scripts/wp2_classification_check.py`,
which mirrors the campaign loop and aggregates `classification_metrics`
against designer-injected ground truth (signal-bearing clocks
post-onset). Two reports are given because the choice of denominator
for FPR / precision is itself ambiguous — *all eight scenarios* dilutes
FPR with the null scenarios' large pool of true negatives, while
*signal scenarios only* (S1, S2, S3, S6, S7, S8) restricts the denominator
to settings where ground-truth anomalies actually exist.

| Scope | TPR | FPR | precision | F1 |
|-------|----:|----:|----------:|---:|
| All 8 scenarios | 0.430 | 0.010 | 0.763 | 0.550 |
| Signal scenarios only (6) | 0.430 | 0.010 | 0.831 | 0.567 |

Strict STRUCTURED-only TPR = **0.007** (signal scenarios). Almost all
detections classify as UNSTRUCTURED. Both classes produce the same
exclusion effect on consensus, so the low STRUCTURED TPR does not
compromise DG-2 functionality — but it does mean the *three-way*
distinction the proposal motivates is not detectably operative at
T = 200 with these signals; the temporal-statistic gates (var_slope,
acf) almost never fire on top of an IC-flagged reading. WP3 ablation 4
(two-way vs three-way) is the direct test of whether the distinction
adds anything.

An earlier draft of this entry quoted TPR = 0.465 / precision = 0.808 /
F1 = 0.590 from a different aggregation pass; those values have been
replaced by the `wp2_classification_check.py` output above so the
numbers are reproducible from a script in the repository. A subsequent
fix to that script (RNG-order alignment with `wp2_campaign.py`)
shifted the numbers by < 0.005 on every metric — the post-fix values
are the canonical ones reported above.

---

## Tests added / updated

`tests/test_metrics.py` — 15 tests, all passing:
- MSE against zero, ones, offset reference, mixed values
- Collapse index: centralised = 0, spread > 0, scale invariance
- Structure correlation: perfect correlation, zero correlation, no signal clocks, constant residual edge case
- Classification metrics: perfect, all-wrong, mixed, 2-D arrays

`tests/test_constraints.py` — +2 regression tests:
- `test_constant_state_zero_update_passes`: zero update on constant state is not rejected
- `test_constant_state_nonzero_update_passes`: small non-zero update on constant state is not rejected

`tests/test_estimators.py` — +2 regression tests:
- `test_does_not_freeze_at_initial_reading`: asserts estimates evolve away from `Y[0, :]` and MSE stays below 0.5 on pure noise
- `test_fully_connected_stays_near_delay_variant`: asserts `admec_full` stays within 2.0 of `admec_delay` on fully-connected zero-delay data

Suite now **261 tests / 259 passing** (the 2 failing tests are the documented entry-002 σ-underestimation cases).

---

## Files changed

| File | Change |
|------|--------|
| `src/metrics.py` | New: MSE, collapse index, structure correlation, classification diagnostics; constant-signal fallback for step scenarios |
| `scripts/wp2_campaign.py` | New: 8-scenario campaign harness with `--smoke` mode; smoke filename suffix to avoid collision |
| `tests/test_metrics.py` | New: 17 metric tests (+2 constant-signal edge cases) |
| `tests/test_estimators.py` | +2 regression tests for `admec_full` freeze and near-delay behaviour |
| `tests/test_constraints.py` | +2 regression tests for FP variance-ratio bug |
| `src/estimators.py` | Fix: `admec_full` t=0 init; docstring updated; module header updated to 9/9 |
| `src/constraints.py` | Fix: `var_before > 0` → `var_before > 1e-20` to guard against FP noise |
| `src/__init__.py` | Status updated to WP2 modules complete |
| `data/wp2_campaign_20260504_fix.npz` | New: canonical campaign data (8 scenarios × 10 seeds × 9 estimators, T=200) |

---

*Entry by AI assistant (Kimi Code CLI). Human review and sign-off by U. Warring.*

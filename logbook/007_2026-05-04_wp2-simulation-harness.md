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

Mean MSE per scenario:

| Scenario | freq_global | freq_local | freq_exclude | huber | bocpd | imm | admec_unc | admec_delay | admec_full |
|----------|------------:|-----------:|-------------:|------:|------:|----:|----------:|------------:|-----------:|
| S1 | 0.323 | 3.084 | **0.135** | 0.145 | 0.224 | 0.147 | 0.135 | 1.647 | 0.732 |
| S2 | 0.323 | 0.316 | 0.135 | 0.145 | 0.224 | 0.147 | 0.135 | 0.136 | **0.093** |
| S3 | 0.316 | 4.176 | **0.025** | 0.026 | 0.109 | 0.026 | 0.025 | 2.002 | 0.741 |
| S4 | 0.323 | 1.611 | **0.135** | 0.145 | 0.224 | 0.147 | 0.135 | 0.746 | 0.485 |
| S5 | 0.316 | 1.426 | **0.025** | 0.026 | 0.109 | 0.026 | 0.025 | 0.851 | 0.528 |
| S6 | 0.323 | 1.591 | **0.135** | 0.145 | 0.224 | 0.147 | 0.135 | 0.751 | 0.461 |
| S7 | 0.319 | 1.670 | 0.135 | 0.145 | 0.224 | 0.147 | 0.135 | 0.746 | **0.119** |
| S8 | 0.323 | 1.645 | 0.135 | 0.145 | 0.224 | 0.147 | 0.135 | 0.752 | **0.115** |

Mean collapse index per scenario:

| Scenario | admec_delay | admec_full |
|----------|------------:|-----------:|
| S1 | 1.088 | 0.622 |
| S2 | 0.071 | 0.014 |
| S3 | 1.264 | 0.820 |
| S4 | 0.647 | 0.441 |
| S5 | 0.661 | 0.456 |
| S6 | 0.648 | 0.431 |
| S7 | 0.649 | 0.117 |
| S8 | 0.649 | 0.111 |

Mean structure correlation per scenario:

| Scenario | freq_global | freq_local | freq_exclude | huber | bocpd | imm | admec_unc | admec_delay | admec_full |
|----------|------------:|-----------:|-------------:|------:|------:|----:|----------:|------------:|-----------:|
| S1 | 0.951 | 0.640 | 0.954 | 0.954 | 0.951 | 0.955 | 0.954 | 0.799 | 0.899 |
| S2 | 0.951 | 0.949 | 0.954 | 0.954 | 0.951 | 0.955 | 0.954 | 0.949 | 0.955 |
| S3 | 0.946 | 0.432 | 0.950 | 0.951 | 0.948 | 0.952 | 0.950 | 0.574 | 0.795 |

### Observations

- `freq_exclude` is the strongest non-ADMEC baseline across all scenarios. It is mathematically identical to `admec_unconstrained` (both compute the inverse-variance weighted mean of all non-degraded clocks), so their metrics are identical.
- On **S2** (fully connected, negligible delay), `admec_full` achieves the best MSE (0.093), best collapse index (0.014), and best structure correlation (0.955). The constraint layer adds conservatism that improves over the unconstrained consensus.
- On **S1** and **S3** (sparse topologies with Poisson delays), `admec_full` is better than `admec_delay` but cannot beat `freq_exclude`. The delay-accessible neighbourhood is too small (1–2 nodes on average) to form a stable local consensus; the constraint layer limits step size but cannot compensate for missing neighbours.
- On **S7** and **S8** (change-point and near-critical), `admec_full` achieves the best MSE (0.119 and 0.115) and collapse index (0.117 and 0.111), beating all baselines. The constraint layer's conservatism prevents overshoot after the step/bifurcation.

---

## DG-2 verdict

**DG-2 condition:** ADMEC-full must outperform the best non-ADMEC baseline (freq-global/local/exclude, Huber, BOCPD, or IMM) on ≥2 of {MSE, collapse index, structure correlation} in **both** S1 and S3.

### S1 (ring, 15 nodes, Poisson(2.0), sinusoidal)

| Metric | Best baseline | admec_full | Pass? |
|--------|--------------|------------|-------|
| MSE | freq_exclude = 0.135 | 0.732 | ❌ FAIL |
| Collapse index | freq_exclude = 0.000 | 0.622 | ❌ FAIL |
| Structure correlation | imm = 0.955 | 0.899 | ❌ FAIL |

**S1 result: 0/3 metrics pass.**

### S3 (random sparse, 50 nodes, Poisson(4.0), sinusoidal)

| Metric | Best baseline | admec_full | Pass? |
|--------|--------------|------------|-------|
| MSE | freq_exclude = 0.025 | 0.741 | ❌ FAIL |
| Collapse index | freq_exclude = 0.000 | 0.820 | ❌ FAIL |
| Structure correlation | imm = 0.952 | 0.795 | ❌ FAIL |

**S3 result: 0/3 metrics pass.**

### Verdict: **DG-2 NOT MET.**

ADMEC-full does not beat the best non-ADMEC baseline on ≥2 metrics in S1 or S3. The failure mode is structural: on sparse networks with realistic delays, the delay-accessible neighbourhood is too small to support a local consensus that outperforms a centralised inverse-variance weighted mean. The constraint layer improves over `admec_delay` but cannot close the gap to `freq_exclude`.

**Mitigating factors:**
- S2 (fully connected) and S7/S8 (change-point / near-critical) show strong wins, demonstrating that the constraint architecture is beneficial when the network topology is favourable.
- The delay convention (drop neighbours with delay > freshness, do not use stale readings) is a known limitation. WP3 will ablate this choice.
- The classification layer (STRUCTURED vs UNSTRUCTURED gating) is working as designed — the issue is in the consensus step, not the IC layer.

---

## DG-2b classification validation

TPR/FPR over all anomaly detections (structured + unstructured):
- TPR = 0.465, FPR = 0.0111, precision = 0.808, F1 = 0.590

Strict STRUCTURED-only TPR = 0.0071. Most detections classify as UNSTRUCTURED, not STRUCTURED. Both classes produce the same exclusion effect on consensus, so the low STRUCTURED TPR does not compromise DG-2 functionality. It does, however, indicate that the temporal-statistic gates (var_slope, acf) are not yet sensitive enough to capture structured anomalies in these short (T=200) runs.

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

Suite now **259 tests / 257 passing** (the 2 failing tests are the documented entry-002 σ-underestimation cases).

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

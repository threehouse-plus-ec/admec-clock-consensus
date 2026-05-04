# WP2 Summary — Network Simulation and DG-2 Verdict

**Status:** Work Package 2 complete. **DG-2 NOT MET** — recorded as a negative result. Core architecture (`clocks` → `network` → `classify` → `constraints` → `estimators` → `metrics`) implemented and validated. WP3 ablations are scoped to characterise the failure mode rather than salvage DG-2.

---

## Objective

WP2 tested whether the proposed three-way classification + delay constraints + update-size constraints scheme (ADMEC-full) yields measurably better consensus than established robust baselines on a controlled simulated clock network. The pre-registered decision gate DG-2 required that ADMEC-full beat the best non-ADMEC baseline on at least two of three IC-independent metrics (MSE, collapse index, structure correlation) in **both** scenarios S1 (15-clock ring with delay 2.0) and S3 (50-clock random-sparse network with delay 4.0), and additionally beat ADMEC-delay (i.e. the constraint layer must add value).

## What was implemented

**Clock model (`src/clocks.py`).** SDE-based per-clock simulator with white frequency noise, flicker noise (fractional Gaussian noise, Davies-Harte H = 0.9), random-walk frequency noise, optional linear drift, optional injected signal callable, optional Student-t heavy-tail mode, and a degradation factor for outlier clocks. The `hydrogen_maser()` preset matches Panfilo & Arias (2019, Table 1): σ_y(τ = 1 day) ≈ 1.5 × 10⁻¹⁵ for white frequency, flicker floor σ_y ≈ 7 × 10⁻¹⁶. Four signal generators cover the proposal's scenario taxonomy: sinusoidal (S1, S2, S3), linear drift (S6), step (S7), and fold-bifurcation Euler integrator (S8).

**Network topology and delays (`src/network.py`).** Three topologies: ring, random-sparse with target degree k = 3 (constructed by random spanning tree plus random edge-addition, yielding average degree within 5 % of target), and fully connected. Symmetric Poisson delay sampling on edges. No NetworkX dependency.

**Three-way classifier (`src/classify.py`).** Wired to the calibrated WP1 thresholds: per-reading I_k threshold 2.976 bit (entry 006, worst-case σ regime), δ_min_var = 0.2105 (entry 004, 3 × median |var slope| under Student-t(3)), δ_min_acf = 0.8703 (entry 004, 95th percentile of |acf| under random walk). Implements the three-way rule:

```
STABLE                 I_k <  threshold
STRUCTURED ANOMALY     I_k >= threshold AND
                       (|var_slope| > delta_min_var OR
                        |lag-1 acf|  > delta_min_acf)
UNSTRUCTURED ANOMALY   I_k >= threshold AND
                       |var_slope| <= delta_min_var AND
                       |lag-1 acf|  <= delta_min_acf
```

ADMEC consensus uses STABLE-only weighted mean (STRUCTURED nodes are "tracked and gated" per the proposal — preserved as a separate channel rather than absorbed; UNSTRUCTURED nodes are excluded). The classifier behaves as designed but rarely fires on the WP2 scenarios because both the per-reading IC threshold and δ_min are selective on coherent signals that broaden the mixture density along with the readings (cf. entry 006 docstring).

**Constraint projector (`src/constraints.py`).** Sequential projection onto the feasible set defined by three constraints: per-node 3 σ box clip, total Nσ̄² energy ball (uniform shrink), and a [0.5, 1.5] variance-ratio post-check that rejects violating updates entirely (carrying the previous estimate forward). Defaults match the proposal verbatim. The constraint thresholds will be ablated at ±30 % in WP3.

**Nine consensus estimators (`src/estimators.py`).** All implemented behind a common `(Y, Sigmas, adj, delays, **kwargs) → Estimates(T, N)` interface and exposed in an `ESTIMATORS` registry:
- `freq_global` — inverse-variance weighted mean of all nodes per step.
- `freq_local` — per-node weighted mean over delay-accessible neighbours and self.
- `freq_exclude` — centralised mean excluding nodes with cross-sectional per-reading I_k ≥ 2.976.
- `huber` — IRLS Huber M-estimator, default tuning constant c = 1.345.
- `bocpd` — per-node Adams & MacKay 2007 changepoint detection in log-space with r_max truncation; centralised consensus over non-excluded nodes (MAP run-length ≥ `min_run_keep` = 10).
- `imm` — per-node two-mode Blom & Bar-Shalom 1988 IMM filter; centralised consensus excluding nodes whose anomalous-mode posterior crosses 0.7. Default Q ratio = 100 ×, tuned to the upper end of the 10–100 × sweet spot that keeps mode probabilities informative.
- `admec_unconstrained` — three-way classification, centralised STABLE-only weighted mean.
- `admec_delay` — per-node STABLE-only weighted mean over delay-accessible neighbours.
- `admec_full` — `admec_delay` followed by sequential constraint projection on the per-node update vector; constraint failure carries the previous estimate forward.

**Performance metrics (`src/metrics.py`).** Three IC-independent metrics matching the proposal:
- `mse(estimates, reference)` — mean squared error against the nominal reference (0 for fractional-frequency residuals).
- `collapse_index(estimates, sigmas)` — time-averaged std(estimates over nodes) / mean(sigmas), so 0 for centralised methods and > 0 for spread-preserving local methods.
- `structure_correlation(Y, estimates, signals, signal_clocks, onset_idx)` — Pearson r between (reading − estimate) and the injected signal, averaged over signal clocks post-onset; high = signal preserved in residual; low = signal absorbed into consensus. Falls back to a residual-magnitude-ratio when the injected signal is constant (S7's step).

Plus DG-2b classification diagnostics: `classification_metrics(excluded, true_anomalous)` returns TPR/FPR/precision/F1 against designer-injected ground truth.

**Campaign harness (`scripts/wp2_campaign.py`).** Defines the eight proposal scenarios verbatim, runs every `(scenario, seed, estimator)` triple, computes all three metrics, and writes `data/wp2_campaign_YYYYMMDD_*.npz`. Signal amplitudes are set to unit-scale (σ_white = 1.0) to keep the metric values dimensionless and comparable: sinusoidal amplitude 5 σ, step magnitude 5 σ, drift rate 0.01 σ/step, fold bifurcation `epsilon = 0.005, r0 = -1.0` (chosen empirically to approach the bifurcation within T = 200 without explicit-Euler blow-up).

## What was demonstrated

**End-to-end pipeline operational.** All eight scenarios, ten seeds, nine estimators run to completion; all three metrics computed without numerical issues after two bug fixes (entry 007). The canonical campaign archive is `data/wp2_campaign_20260504_fix.npz`.

**`admec_full` beats `admec_delay` on every scenario** (lower MSE, lower collapse index, higher structure correlation). The constraint layer is internally coherent and adds measurable value over the unconstrained delay-restricted variant. This satisfies one half of DG-2's requirement; the other half (beating non-ADMEC baselines) is where it fails.

**S2 win.** On S2 (fully connected, Poisson(0.3)) — the scenario explicitly designed as a control with negligible delay — `admec_full` achieves the best MSE (0.093 vs `freq_exclude` 0.135), the best collapse index (0.022), and the best structure correlation (0.958). The constraint layer's projection adds ~30 % MSE improvement over centralised exclusion methods when delays do not starve the local consensus.

**Two bug fixes recorded** (entry 007):
1. `admec_full` initialisation: `estimates[0, :] = Y[0, :]` triggered the variance-ratio constraint to reject every subsequent update, freezing the estimator at t = 0. Replaced with the centralised inverse-variance weighted mean. Effect: S2 MSE 4.85 → 0.093; S1 MSE 1.50 → 0.732.
2. Floating-point variance-ratio guard: `np.var(state)` of a constant array returns `~3 × 10⁻³³`, not exactly zero. The original `if var_before > 0` branch entered the variance-ratio check on uniform states and rejected every update. Replaced with `var_before > 1e-20`. Effect: S2 MSE 0.269 → 0.093 (the 100 % rejection rate on dense networks dropped to <1 %).

Both fixes have regression tests in `tests/test_constraints.py` and `tests/test_estimators.py`.

## DG-2 verdict

**DG-2 condition.** ADMEC-full must outperform the best non-ADMEC baseline (FREQ-global / FREQ-local / FREQ-exclude / Huber / BOCPD / IMM) on ≥ 2 of {MSE, collapse index, structure correlation} in **both** S1 and S3, **and** must outperform ADMEC-delay.

| Metric | Best non-ADMEC, S1 | admec_full S1 | Pass S1? | Best non-ADMEC, S3 | admec_full S3 | Pass S3? |
|--------|-------------------:|--------------:|:--------:|-------------------:|--------------:|:--------:|
| MSE | freq_exclude 0.135 | 0.732 | ✗ | freq_exclude 0.025 | 0.741 | ✗ |
| Collapse index | (centralised) 0.000 | 0.644 | ✗ | (centralised) 0.000 | 0.808 | ✗ |
| Structure correlation | imm 0.956 | 0.897 | ✗ | imm 0.960 | 0.887 | ✗ |

**S1: 0/3 metrics pass. S3: 0/3 metrics pass. DG-2 NOT MET.**

`admec_full` does beat `admec_delay` on all three metrics in both scenarios (constraint layer has positive contribution), but the gap to centralised non-ADMEC methods cannot be closed.

**Of the eight scenarios, `admec_full` beats the best non-ADMEC baseline on MSE in only one (S2)**.

## What this does and does not show

**It does show:** the architectural choice "delay-restricted local consensus" is the binding limitation. On sparse networks with realistic Poisson delays, the delay-accessible neighbourhood at freshness = 1 is too small (1–2 nodes on average for S1/S3) for any local-consensus design — constrained or not — to beat a centralised inverse-variance weighted mean that pools all readings. Centralised exclusion methods (`freq_exclude`, `imm`) are sufficient for the tested regime.

**It does not show:** that the *full* design space has been falsified. WP3 ablations test three specific design choices that could plausibly close the gap: the delay convention (drop vs use stale readings), the IC classification threshold, and the constraint thresholds. The current data already constrains what those ablations can reveal — see "WP3 framing" below.

**It does not show:** that the IC classification was the source of failure. The classifier behaved as designed (cf. entry 006 docstring on the selectivity of the per-reading 2.976-bit threshold). On most scenarios `freq_exclude` and `admec_unconstrained` give nearly identical exclusion masks because IC and temporal-statistic gates rarely diverge at the per-reading level for the tested signals. The deficit is in the consensus step downstream of classification, not in classification itself.

**It does not show:** that ADMEC's constraint architecture is wrong. The constraint layer beats `admec_delay` everywhere on all three metrics. The architecture is internally coherent; it just cannot compensate for the missing neighbours.

## DG-2b classification validation

DG-2b required the three-way classifier to report TPR ≥ 70 % against designer-injected ground truth. Across the campaign the overall TPR (treating either STRUCTURED or UNSTRUCTURED detection as a positive) is 0.465, FPR 0.011, precision 0.808, F1 0.590. Strict STRUCTURED-only TPR is 0.0071 — almost all detections classify as UNSTRUCTURED.

**DG-2b NOT MET on the strict three-way criterion.** The temporal-statistic gates that distinguish STRUCTURED from UNSTRUCTURED rarely fire on the tested scenarios, consistent with entry-006's docstring observation that the calibrated δ_min values are tuned for critical-slowing-down dynamics, not for the linear drifts (S6) or step changes (S7) that dominate the WP2 signal injection. Whether the structured/unstructured distinction adds anything beyond binary anomaly handling is the explicit DG-3 question; the current data already hints at the answer.

## WP3 framing

WP3 ablations are now scoped to **characterise the WP2 failure mode** rather than to attempt rescue, in line with the project's pre-registered position that DG-2 outcomes — positive or negative — are reported either way.

| Ablation | Question | Expected outcome given WP2 data |
|----------|----------|---------------------------------|
| 1. Delay convention | Does pulling stale readings (`Y[t − τ_ij, j]`) instead of dropping inaccessible neighbours close the S1/S3 gap? | If yes, the failure was the convention, not the architecture. If no, the constraint locality is the binding limit. |
| 2. Classification threshold sweep | At what threshold does `admec_full` differ from `freq_exclude`? | Should reveal the active region of the IC gate. If thresholds in [1.5, 2.5] all give similar results, the gate is rarely binding. |
| 3. Constraint sensitivity (±30 %) | Which constraint (box, energy, variance-ratio) drives the rejection rate on dense networks? | Will tell us whether the rejection rate is acceptable or pathological. |
| 4. Two-way vs three-way (DG-3 core) | Does the structured/unstructured distinction add anything? | Given DG-2b's strict-STRUCTURED TPR ≈ 0.7 %, the expectation is no. |
| 5. ADMEC-full-lagged | Does using IC(t−1) instead of IC(t) in classification change anything? | Tests for simultaneity bias. Expected null result given the rare gate firing. |

The 5-configuration × 3-scenario × 10-seed WP3 design is described in `docs/projektantrag.md` § WP3.

## Resulting status

**WP2 closed:** all five WP2 modules implemented (`clocks.py`, `network.py`, `classify.py`, `constraints.py`, `estimators.py`), full campaign archive saved, test suite at 260 / 258 passing (the 2 known WP1 failures from entry 002 σ-underestimation, mitigated by worst-case threshold calibration). Entry 007 records the harness build, the two bug fixes, and the DG-2 verdict.

**Decision-gate state after WP2:**

| Gate | Status |
|------|--------|
| DG-1 | Closed (entry 003), one recorded sub-criterion failure (entry 002 σ-underestimation, mitigated by worst-case calibration in entry 006) |
| DG-2 | **NOT MET** (entry 007); only S2 beats the best non-ADMEC baseline on MSE |
| DG-2b | NOT MET on strict three-way criterion (entry 007) |
| DG-3 | Will be addressed in WP3 ablations |

## References

1. Adams, R. P. & MacKay, D. J. C. Bayesian online changepoint detection. arXiv:0710.3742 (2007).
2. Blom, H. A. P. & Bar-Shalom, Y. The interacting multiple model algorithm. *IEEE Trans. Automat. Contr.* **33**, 780–783 (1988).
3. Huber, P. J. *Robust Statistics* (Wiley, 1981).
4. Panfilo, G. & Arias, F. The Coordinated Universal Time (UTC). *Metrologia* **56**, 042001 (2019).

## Artefacts

| Artefact | Location |
|----------|----------|
| Campaign harness | `scripts/wp2_campaign.py` |
| Campaign archive (canonical) | `data/wp2_campaign_20260504_fix.npz` |
| Logbook entry 007 (harness, bugs, DG-2 verdict) | `logbook/007_2026-05-04_wp2-simulation-harness.md` |
| Source modules | `src/clocks.py`, `src/network.py`, `src/classify.py`, `src/constraints.py`, `src/estimators.py`, `src/metrics.py` |
| Test suite | `tests/test_clocks.py`, `tests/test_network.py`, `tests/test_classify.py`, `tests/test_constraints.py`, `tests/test_estimators.py`, `tests/test_metrics.py` (105 tests added in WP2; 260 / 258 passing total) |
| Tutorial | `notebooks/wp2_tutorial.ipynb`, rendered as `docs/wp2_tutorial.md` |

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for structural editing and code prototyping. All scientific content, decisions, and claims are the sole responsibility of the author.*

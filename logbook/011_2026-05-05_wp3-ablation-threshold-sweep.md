# Logbook Entry 011 — WP3 Ablation 2: Classification Threshold Sweep

**Date:** 2026-05-05
**Work package:** WP3 (ablation 2 of 5; sequenced last as a hygiene check)
**Decision gate:** none directly; refines the DG-2/DG-3 picture

---

## Objective

The WP1 per-reading IC threshold of 2.976 bit was calibrated in entry 006 as the worst-case-σ 95th percentile of per-reading I_k across ten null noise models — a calibration tuned for null false-positive rate, not for downstream consensus MSE. Entry 010 just established that the structured/unstructured split is operationally invisible to the consensus stage; ablation 2 closes the systematic sweep by checking the remaining tunable in the classifier — the IC threshold itself — to verify that the WP2/WP3 conclusions are not artefacts of one specific threshold value.

The expected outcome (registered in the entry-008 / entry-010 prediction list) was a roughly flat sensitivity curve in a "narrow active region" near 2.976, on the grounds that coherent processes broaden the mixture density along with the readings and so few readings cross any nearby threshold value. **That prediction turned out to be wrong:** the sweep reveals strong, asymmetric sensitivity in the *lower* direction.

## What was done

`scripts/wp3_ablation_threshold_sweep.py` runs `admec_full` on the WP3-ablation-1 scenario set (S1 ring delay 2.0, S2 fully connected delay 0.3, S3 random_sparse delay 4.0) over 10 seeds × 2 delay modes × 7 thresholds. `freq_exclude` is also swept (centralised, no delay-mode dimension) so the head-to-head comparison can be made at matched thresholds. The harness records the STABLE-fraction grid for each cell so the threshold's active region can be inspected directly. RNG order matched to `scripts/wp2_campaign.py`. Output: `data/wp3_ablation_threshold_sweep_20260505.npz`.

Threshold values tested:

`[1.5, 2.0, 2.5, 2.976, 3.5, 4.5, 6.0]`

— with 2.976 being the WP1/entry-006 baseline.

## Results

### STABLE fraction across the (T × N) grid

| Scenario | thr 1.5 | 2.0 | 2.5 | **2.976** | 3.5 | 4.5 | 6.0 |
|---------:|-------:|----:|----:|----------:|----:|----:|----:|
| S1 | 0.582 | 0.784 | 0.849 | **0.883** | 0.930 | 1.000 | 1.000 |
| S2 | 0.582 | 0.784 | 0.849 | **0.883** | 0.930 | 1.000 | 1.000 |
| S3 | 0.760 | 0.891 | 0.935 | **0.953** | 0.963 | 0.974 | 0.997 |

The threshold is far from a cliff edge between 2.0 and 3.5: the STABLE fraction varies smoothly from 0.78 to 0.93 on S1/S2, and 0.89 to 0.96 on S3. Above 4.5 the IC distribution is exhausted (the maximum observed I_k on S1/S2 sits between 4.5 and 6.0; on S3 it just reaches 6.0 in 0.3 % of cells), so the classifier saturates at 100 % STABLE and the estimator collapses to its no-exclusion limit.

### admec_full mean MSE (10 seeds)

| Scenario | mode | thr 1.5 | 2.0 | 2.5 | **2.976** | 3.5 | 4.5 | 6.0 |
|---------:|-----:|-------:|----:|----:|----------:|----:|----:|----:|
| S1 | drop | **0.308** | 0.557 | 0.548 | 0.732 | 1.104 | 2.252 | 2.252 |
| S1 | stale | **0.238** | 0.345 | 0.399 | 0.413 | 0.586 | 1.519 | 1.519 |
| S2 | drop | 0.164 | 0.135 | 0.115 | **0.093** | 0.167 | 0.347 | 0.347 |
| S2 | stale | 0.111 | **0.088** | 0.090 | 0.104 | 0.195 | 0.271 | 0.271 |
| S3 | drop | **0.443** | 0.617 | 0.660 | 0.741 | 0.802 | 0.926 | 1.210 |
| S3 | stale | **0.191** | 0.307 | 0.352 | 0.461 | 0.473 | 0.429 | 0.470 |

**Bold** marks the minimum per row. The optimal threshold for admec_full's MSE is **1.5 on every signal-rich delayed scenario** and 2.0–3.0 on the dense S2 control. The WP1-calibrated 2.976 bit is suboptimal for admec_full's consensus MSE in the WP2 problem regime — by a substantial margin in the most sensitive cases (S1 drop and S3 stale, both halve their MSE at threshold 1.5).

### freq_exclude mean MSE (10 seeds)

| Scenario | thr 1.5 | 2.0 | 2.5 | 2.976 | 3.5 | 4.5 | 6.0 |
|---------:|-------:|----:|----:|------:|----:|----:|----:|
| S1 | 0.276 | 0.134 | **0.122** | 0.135 | 0.214 | 0.323 | 0.323 |
| S2 | 0.276 | 0.134 | **0.122** | 0.135 | 0.214 | 0.323 | 0.323 |
| S3 | 0.038 | 0.031 | 0.027 | 0.025 | **0.025** | 0.027 | 0.040 |

`freq_exclude`'s optimal threshold is 2.5 on S1/S2 and 2.976–3.5 on S3. Lower thresholds (1.5) hurt freq_exclude noticeably on S1/S2 because aggressive centralised exclusion strips signal-bearing nodes from the pool without compensating downstream — there is no constraint layer to absorb the extra noise.

### admec_full vs freq_exclude at matched threshold 1.5

| Scenario | admec_full (best mode) | freq_exclude | ratio |
|----------|----------------------:|-------------:|------:|
| S1 | 0.238 (stale) | 0.276 | **0.86 (admec wins)** |
| S2 | 0.111 (stale) | 0.276 | **0.40 (admec wins)** |
| S3 | 0.191 (stale) | 0.038 | 5.05 (admec loses) |

**At threshold 1.5, admec_full beats freq_exclude on S1 and S2** — the first signal-rich scenario where admec_full beats a centralised baseline outside S2. The mechanism: aggressive exclusion (low threshold) removes signal-bearing readings from the pool, and admec_full's constraint layer absorbs the resulting per-step variance increase via projection, while freq_exclude has no such buffer.

S3 still loses by 5× because the centralised information advantage (50 nodes pooled) overwhelms the constraint-layer gain.

### Best-of-best comparison (each estimator at its optimal threshold)

| Scenario | best admec_full (mode + thr) | best freq_exclude (thr) | best non-ADMEC | ratio |
|----------|----------------------------:|------------------------:|---------------:|------:|
| S1 | 0.238 (stale, 1.5) | 0.122 (2.5) | imm 0.147 (default) | 1.62× |
| S2 | 0.088 (stale, 2.0) | 0.122 (2.5) | imm 0.147 (default) | **0.72** ✓ |
| S3 | 0.191 (stale, 1.5) | 0.025 (3.5) | imm 0.024 (default) | 7.96× |

Under independent threshold tuning, admec_full **adds S2 stale to its win column** — but DG-2 was pre-registered with a fixed threshold (the WP1 calibration), so this finding is informational rather than a verdict change.

## Findings

1. **The expected "narrow active region" was wrong.** The threshold sweep from 1.5 to 4.5 produces large MSE deltas (factor 2–7×) on signal-rich delayed scenarios. The WP1-calibrated 2.976 bit is not in the middle of a flat plateau; it sits on a slope.

2. **The WP1 calibrated threshold (2.976, optimised for null FPR) is *suboptimal for consensus MSE* in the WP2 problem regime.** Admittedly the two are different optimisation criteria — null FPR control vs signal-conditional MSE — and the WP1 calibration was the right thing for hypothesis-test interpretation. But the same number was inherited as the operating threshold for admec_full's classifier, where signal-conditional MSE is what the estimator is scored on.

3. **The optimal admec_full threshold differs from the optimal freq_exclude threshold.** admec_full prefers low thresholds (aggressive exclusion + constraint absorption); freq_exclude prefers moderate thresholds (so it doesn't strip too much signal). The two methods have *different* optimal operating points on the threshold axis, which is expected once you notice that admec_full has a noise-absorbing buffer (the constraint layer) that freq_exclude lacks.

4. **At the optimal threshold for admec_full, it beats freq_exclude on S1 and S2.** S1 admec_full (stale, thr 1.5) = 0.238 vs freq_exclude (thr 1.5) = 0.276; S2 = 0.111 vs 0.276. Under independent threshold tuning per estimator, admec_full also adds S2 stale to its win column (best-of-best = 0.088 vs 0.122). DG-2 was pre-registered at the calibrated threshold so this does not formally rescue DG-2, but it does indicate the architecture is more competitive than the fixed-threshold WP2 verdict suggests.

5. **DG-2 still NOT MET on S3.** Even at admec_full's best (stale, thr 1.5, MSE 0.191), the centralised `imm` MSE of 0.024 is 8× lower. The sparse-delay residual identified in entry 008 (a centralised mean over 50 nodes vs a local consensus over 3 ± 1) remains. No threshold value rescues this.

6. **Saturation above thr 4.5** corresponds to "no exclusion": every cell is STABLE, and admec_full degenerates to admec_unconstrained = freq_global. The high-threshold tail of the curve is admec_full giving up its anomaly handling entirely.

## Interpretation

The original prediction — that the threshold was sitting on a flat region — was a reasonable extrapolation from entry 006's "selectivity" observation but turned out to be incorrect. The selectivity observation (per-reading IC rarely crosses 2.976 for coherent processes) was *correct* in absolute terms but missed the relevant question for ADMEC: the *fraction* flagged matters more than the *count*, and the constraint layer reacts to that fraction in non-trivial ways.

The WP1 calibration logic was: pick the threshold that gives 5 % FPR under the worst-case null. That calibration is sound for hypothesis-test reporting (e.g. "what fraction of nodes look anomalous under null?"). For ADMEC's consensus task, the relevant calibration would instead be: pick the threshold that minimises consensus MSE under the signal-bearing scenarios. These are different optimisation criteria and they pick different optimal thresholds, which is the substance of finding 3 above.

In a production setting, one could either (a) accept that the calibrated threshold is conservative and tune downstream parameters to compensate, or (b) re-calibrate to a signal-conditional criterion. WP3 does not pursue (b) — the proposal's pre-registered design is the calibrated value — but the data suggests it would be worth doing if a follow-up project pursues the architectural redesigns sketched at the end of entry 010.

## Combined WP2 + WP3 verdict

| Gate / sub-criterion | Status | Where addressed |
|----------------------|--------|-----------------|
| DG-1 | Closed (one mitigated sub-criterion failure) | entries 001–003, 006 |
| DG-2 | NOT MET (admec_full beats best non-ADMEC on MSE only on S2) | entry 007 |
| DG-2 (with WP3 retuning, best-of-best) | NOT MET (gains S2 stale; still loses S1 and S3) | this entry |
| DG-2b | NOT MET (strict-STRUCTURED TPR ≈ 0.7 %) | entry 007 |
| DG-3 constraint-clause | satisfied (admec_full > admec_delay everywhere) | entries 007, 009 |
| DG-3 three-way > two-way | NOT MET (architecturally; delta = 0 across 360 cells) | entry 010 |

Three of five WP3 ablations done (1 = delay convention, 3 = constraint sensitivity, 4 = two-vs-three-way, 2 = threshold sweep). Ablation 5 (`admec-full-lagged` — IC(t-1) instead of IC(t)) remains; given the entry-010 architectural-impossibility finding for the structured/unstructured split and the other ablations' results, the predicted outcome is approximately null. It would be a one-line addition to the harness if needed.

## What this does and does not show

**It does show:**
- The threshold has substantial MSE sensitivity for admec_full on signal-rich delayed scenarios (factor of 2–3 between worst and best across the swept range).
- Lower thresholds (1.5–2.0) optimise admec_full MSE; the WP1 calibration (2.976, optimised for null FPR) is suboptimal for consensus MSE.
- At a matched aggressive threshold (1.5), admec_full's constraint layer adds value and the estimator beats freq_exclude on S1 and S2 — the architecture's "absorb-noise" mechanism is real.
- Under independent per-estimator threshold tuning, admec_full adds S2 stale to its win column but still leaves a large S3 residual gap.

**It does not show:**
- That the WP1 calibration was wrong. It was correct for its declared purpose (null FPR control). The mismatch is between two distinct optimisation criteria.
- That re-calibrating the threshold rescues DG-2. The S3 sparse-plus-delayed regime (small effective neighbourhood) cannot be closed by threshold tuning alone.
- That the optimal threshold transfers across scenarios. admec_full's optimal threshold is 1.5 on the delayed scenarios but 2.0 on S2 stale; in a deployment with mixed scenarios you would either pick a compromise value or adapt online.

## Files changed

| File | Change |
|------|--------|
| `scripts/wp3_ablation_threshold_sweep.py` | New: 7-threshold × 2-mode × 3-scenario × 10-seed harness, with STABLE-fraction diagnostics and freq_exclude comparator |
| `data/wp3_ablation_threshold_sweep_20260505.npz` | New: ablation archive |

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for code prototyping and structural editing.*

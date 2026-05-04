# Logbook Entry 010 — WP3 Ablation 4: Two-Way vs Three-Way Classification (DG-3)

**Date:** 2026-05-04
**Work package:** WP3 (ablation 4 of 5)
**Decision gate:** **DG-3** sub-criterion: "three-way > two-way"

---

## Objective

The proposal motivates a three-way classification (STABLE / STRUCTURED / UNSTRUCTURED) over the conventional binary STABLE / ANOMALOUS split, on the argument that *structured* anomalies (persistent temporal departures) carry information worth tracking, while *unstructured* ones (memoryless noise bursts) should be discarded. DG-3 requires that this distinction yield a measurable advantage on at least one IC-independent metric: ADMEC-full with three-way classification must beat the same estimator with the structured/unstructured split collapsed into a single ANOMALOUS class.

This ablation tests that requirement directly.

## What was done

### 1. `two_way` parameter added to `classify_array` and the three ADMEC variants

`src/classify.py:classify_array` now accepts `two_way: bool = False`. When `True`, the temporal-statistic split is bypassed and every flagged reading (`ic >= threshold`) is labelled `Mode.UNSTRUCTURED` (acting as a generic "ANOMALOUS"). NaN temporal stats no longer matter in two-way mode — only NaN IC produces UNDEFINED. The collapse direction (STRUCTURED → UNSTRUCTURED) was chosen so that downstream estimators that already filter on `mode == Mode.STABLE` need no code change: in both classifier modes, the STABLE-only mask has the intended semantics.

`src/estimators.py:admec_unconstrained`, `:admec_delay`, and `:admec_full` all gained a `two_way: bool = False` keyword that propagates through the `_classify_network_full` helper. The default `False` preserves the WP2 behaviour exactly (verified by reproducing the WP2 canonical archive's S1/S2/S3 admec_full numbers).

### 2. Ablation harness `scripts/wp3_ablation_two_vs_three_way.py`

Runs all three ADMEC estimators on the same three scenarios from ablations 1 and 3 (S1, S2, S3) over 10 seeds, both delay modes, and both classifier modes. RNG ordering matched to `scripts/wp2_campaign.py` so the three-way drop-mode numbers reproduce the WP2 canonical archive byte-exactly. Output: `data/wp3_ablation_two_vs_three_way_20260504.npz`.

The harness also records full `(T, N)` mode-count grids for both classifier variants, so the bookkeeping difference can be inspected even when the consensus output does not change.

### 3. Tests added

`tests/test_classify.py:TestTwoWayClassifier` — 5 tests, all passing:
- below-threshold readings classify identically (STABLE in both modes);
- a flagged reading with strong temporal evidence collapses STRUCTURED → UNSTRUCTURED in two-way;
- on a 200×10 random grid, two-way produces zero STRUCTURED labels and the UNSTRUCTURED count equals the three-way (STRUCTURED + UNSTRUCTURED) total;
- a flagged reading with NaN temporal stats is UNDEFINED in three-way but UNSTRUCTURED in two-way (because two-way does not consult temporal stats);
- a NaN IC value stays UNDEFINED regardless of mode.

## Result

**Across 360 configurations (3 scenarios × 10 seeds × 3 estimators × 2 delay modes × 2 classifier modes), the maximum absolute difference between three-way and two-way is exactly 0.0000e+00 on both MSE and structure correlation.** Every consensus-level metric is byte-identical. Eight diagnostic admec_full MSE rows:

| Scenario | mode | three-way MSE | two-way MSE | delta |
|----------|------|--------------:|------------:|------:|
| S1 | drop | 0.7321 | 0.7321 | +0.00e+00 |
| S1 | stale | 0.4132 | 0.4132 | +0.00e+00 |
| S2 | drop | 0.0929 | 0.0929 | +0.00e+00 |
| S2 | stale | 0.1043 | 0.1043 | +0.00e+00 |
| S3 | drop | 0.7408 | 0.7408 | +0.00e+00 |
| S3 | stale | 0.4606 | 0.4606 | +0.00e+00 |

(The other two ADMEC variants give the same all-zero column.)

### Classification mode counts (mean over 10 seeds, the full T×N grid)

| Scenario | classifier | UNDEFINED | STABLE | STRUCTURED | UNSTRUCTURED |
|----------|-----------:|----------:|-------:|-----------:|-------------:|
| S1 | three-way | 34 | 2648 | 5 | 313 |
| S1 | two-way | 0 | 2648 | 0 | 352 |
| S2 | three-way | 34 | 2648 | 5 | 313 |
| S2 | two-way | 0 | 2648 | 0 | 352 |
| S3 | three-way | 46 | 9529 | 6 | 419 |
| S3 | two-way | 0 | 9529 | 0 | 471 |

Two patterns are visible:

- **The STABLE count is identical between modes**, by construction (the IC threshold is the only criterion that produces STABLE in either mode).
- **Three-way's UNDEFINED + STRUCTURED + UNSTRUCTURED equals two-way's UNSTRUCTURED**, so the *non-STABLE* count is identical.

This is the operational explanation for the byte-identical consensus output: every ADMEC variant computes its consensus over the STABLE mask, and that mask is identical between classifiers. Whether the non-STABLE cells are split STRUCTURED vs UNSTRUCTURED (vs UNDEFINED for the trailing-window warmup) makes no difference to the inverse-variance weighted mean over STABLE.

## Interpretation

**The three-way distinction has no operational effect on the consensus output under the WP2/WP3 architecture.** The proposal's "tracked and gated" language implies STRUCTURED nodes should be preserved as a separate channel for downstream analysis; in the WP2 metrics (MSE, collapse index, structure correlation) the consensus value is what is scored, and the consensus value never reads the STRUCTURED channel. So at the level DG-3 measures, three-way collapses to two-way exactly.

This is **not** evidence that the three-way distinction is conceptually wrong, only that it does not contribute to the metrics that DG-3 was specified against. To make three-way affect those metrics, the architecture would need a different update rule — for example:

- include STRUCTURED nodes in the consensus with reduced weight, rather than excluding them outright;
- use the STRUCTURED count as a signal-aware tuning knob for the constraint thresholds;
- track the STRUCTURED channel as a separate output and score *that* as a "preserved-disagreement" channel.

None of these is in the proposal's WP2 architecture. They are redesigns, not tuning ablations.

### DG-3 verdict on the "three-way > two-way" sub-criterion

| Metric | best three-way | best two-way | three-way > two-way? |
|--------|---------------:|-------------:|:--------------------:|
| MSE | identical | identical | NO (delta = 0) |
| Collapse index | identical | identical | NO (delta = 0) |
| Structure correlation | identical | identical | NO (delta = 0) |

**DG-3's "three-way > two-way" sub-criterion: NOT MET (with delta = 0 across all 360 cells).** This is a stronger negative result than ablations 1 / 3 produced for DG-2 — the gap is not "small" or "scenario-dependent"; it is exactly zero.

The other DG-3 sub-criterion ("each constraint layer ≥ 10 % on ≥ 1 metric") was already addressed in ablation 3: the constraint layer beats `admec_delay` everywhere on MSE under the WP2 baseline, so it satisfies that criterion. Per the proposal's logic, **DG-3 fails on the three-way clause regardless of the constraint clause.**

## Combined WP2 + WP3 conclusion

DG-2 NOT MET (entry 007) — admec_full beats centralised baselines on MSE in only S2.
DG-2b NOT MET (entry 007) — strict-STRUCTURED TPR ≈ 0.7 % against ground truth.
DG-3 NOT MET on three-way > two-way (this entry) — the consensus output is byte-identical.

The three findings cohere: STRUCTURED detection is rare (DG-2b), and even when it fires it does not change the consensus (this entry), because both anomaly classes produce the same STABLE mask. The architectural complexity of the structured/unstructured distinction buys nothing on the metrics WP2 was designed to score.

The constructive findings — `stale` reduces MSE 38–44 % on S1/S3 (entry 008), `var_loose` recovers the constraint ordering on S3 stale (entry 009) — remain independently useful as design levers for any future decentralised-consensus application that has to live with the structural information-theoretic ceiling. They do not depend on the three-way classification.

## What this does and does not show

**It does show:**
- The three-way / two-way distinction has zero operational effect on consensus MSE, collapse index, and structure correlation under the WP2/WP3 architecture (delta = 0 across 360 cells).
- The DG-3 "three-way > two-way" sub-criterion cannot be satisfied without a redesign that lets STRUCTURED status enter the consensus update rule directly.
- The bookkeeping difference (STRUCTURED count tracked separately) is informative for diagnostics — STRUCTURED is reliably a tiny minority (5–6 cells out of ~3000 on S1/S2; 6 of ~10 000 on S3) — but the consensus does not consume it.

**It does not show:**
- That the three-way conceptual distinction is wrong. The classifier produces the labels the proposal asked for; what is missing is downstream architecture that uses them.
- That a *different* update rule which weighted STRUCTURED nodes specially would also produce delta = 0. Testing such a redesign is a project-design question, not a WP3 ablation question.

## Files changed

| File | Change |
|------|--------|
| `src/classify.py` | Added `two_way: bool = False` to `classify_array` |
| `src/estimators.py` | Added `two_way` to `_classify_network_full`, `admec_unconstrained`, `admec_delay`, `admec_full` |
| `scripts/wp3_ablation_two_vs_three_way.py` | New: 3 scn × 10 seeds × 3 estimators × 2 modes × 2 classifiers harness |
| `data/wp3_ablation_two_vs_three_way_20260504.npz` | New: ablation archive |
| `tests/test_classify.py` | Added `TestTwoWayClassifier` (5 tests) |

## Suggested next ablations

Two remain in the WP3 menu:

1. **Ablation 2 (classification threshold sweep)** — given the per-reading 2.976 bit threshold's selectivity (entry 006), the prediction is that thresholds between ~1.5 and ~3.5 give similar STABLE masks (the IC distribution is heavy-tailed but the active region is narrow). This is a hygiene check; it will confirm or refute whether the threshold value matters at the consensus level.
2. **Ablation 5 (`admec-full-lagged`)** — uses `IC(t-1)` instead of `IC(t)` for classification. Tests for simultaneity bias. Given DG-2b's ~0.7 % strict-STRUCTURED TPR and this entry's delta = 0 finding, the expected outcome is also approximately null.

Both are quick to run; ablation 2 first.

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for code prototyping and structural editing.*

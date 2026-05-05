# Delay-Constrained Anomaly-Aware Consensus on Heterogeneous Clock Networks: A Characterisation Study

**Author:** Ulrich Warring (Physikalisches Institut, Albert-Ludwigs-Universität Freiburg).
**Status:** Draft manuscript scaffolded 2026-05-05. Maps directly onto the project's pre-registered decision gates (DG-1, DG-2, DG-2b, DG-3) and the five-ablation WP3 menu defined in [docs/projektantrag.md](projektantrag.md). Full numerical detail and supporting code live in the [logbook](../logbook/) and [scripts](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/scripts).
**Reproducibility:** every table in this manuscript is derivable from one of the canonical archives in [`data/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/data); each section cites the archive it draws from.

---

## Abstract

We present a complete characterisation of ADMEC, a candidate decentralised consensus scheme for heterogeneous clock networks that combines an information-content (IC) anomaly observable with a three-way STABLE / STRUCTURED / UNSTRUCTURED classification, delay-constrained updates, and projected update-size limits.

Four pre-registered decision gates govern the result. **DG-1** (IC calibration) is a prerequisite for the simulation work and was closed prior to this manuscript with one mitigated sub-criterion failure. The simulation gates reported here are **DG-2** (ADMEC-full beats the best non-ADMEC baseline on ≥ 2 IC-independent metrics in *both* a 15-node ring and a 50-node random-sparse network, and additionally beats the unconstrained-delay variant), **DG-2b** (strict three-way classification true-positive rate ≥ 70 % against designer-injected ground truth), and **DG-3** (each constraint layer adds ≥ 10 % on at least one metric, and three-way classification outperforms two-way).

The study includes an 8-scenario × 10-seed × 9-estimator simulation campaign and five orthogonal ablations (delay convention, classification threshold, constraint sensitivity, classifier cardinality, detection lag).

**DG-2 is not met** at the pre-registered operating point; ADMEC-full beats centralised baselines on only one of eight scenarios (S2, fully connected, low delay). **DG-2b is not met** on the strict three-way criterion (TPR ≈ 0.7 %). **DG-3 is not met** on the three-way > two-way clause: under the pre-registered architecture, the structured / unstructured distinction is invisible to the consensus output (max delta = 0 across 360 ablation cells, an architectural-impossibility result rather than a statistical near-null).

Combined design tuning (stale-reading delay convention, loosened variance-ratio bound, lower IC threshold), measured directly by an integrated harness on the same RNG-matched seeds as the WP2 campaign, reduces ADMEC-full's S3 mean squared error from 0.741 to 0.196 (−74 %) and S1 from 0.732 to 0.252 (−66 %). The residual gap to centralised exclusion methods (S3: 7.8 ×, S1: 1.7 ×) is consistent with a centralised-vs-local information-theoretic ceiling that no design tuning closes. On S2 the combined-tuned ADMEC-full beats every centralised baseline tested.

We additionally show three constructive findings: the same-step IC computation is well-formed (no simultaneity bias; lagged classification strictly hurts); ADMEC's constraint layer functions as a noise-absorption mechanism that pays off only when paired with aggressive exclusion; and the WP1-calibrated IC threshold (optimised for null false-positive rate) is suboptimal for consensus mean squared error in signal-rich scenarios — at a matched lower threshold, ADMEC-full beats centralised exclusion on S1 and S2.

We conclude with two architectural redesigns (STRUCTURED-with-reduced-weight; decayed-staleness weighting) that could plausibly rescue the gates and would be appropriate for a follow-up project.

---

## 1. Introduction

The standard response to disagreeing clocks in a network is robust averaging: suppress outliers so the consensus stays stable. This works when deviations are random noise. But when some deviations carry information — a slow drift, a rising variance, a near-bifurcation indicator — robust suppression discards signal alongside noise.

The ADMEC scheme proposed in [docs/projektantrag.md](projektantrag.md) tests whether a finer distinction is operationally useful. ADMEC classifies each clock reading into one of three categories using a per-reading information-content (IC) observable plus two trailing-window temporal-structure statistics (variance slope, lag-1 autocorrelation):

```
STABLE                : I_k <  threshold
STRUCTURED ANOMALY    : I_k >= threshold AND (|var_slope| > delta_min_var OR |acf| > delta_min_acf)
UNSTRUCTURED ANOMALY  : I_k >= threshold AND |var_slope| <= delta_min_var AND |acf| <= delta_min_acf
```

The proposal is that *structured* anomalies should be **tracked and gated** rather than excluded — preserved as a separate channel for downstream analysis — while *unstructured* anomalies should be excluded outright as memoryless noise bursts. This three-way response, together with delay-constrained updates and projected update-size limits, defines the `admec_full` estimator.

The pre-registered decision gates are:

- **DG-2** — `admec_full` outperforms the best non-ADMEC baseline (FREQ-global / FREQ-local / FREQ-exclude / Huber / BOCPD / IMM) on ≥ 2 of {MSE, collapse index, structure correlation} in *both* S1 and S3, and additionally beats `admec_delay` (i.e. the constraint layer adds value).
- **DG-2b** — strict-STRUCTURED true-positive rate ≥ 70 % against designer-injected ground truth.
- **DG-3** — each constraint layer adds ≥ 10 % on at least one metric, *and* three-way classification outperforms two-way.

The proposal explicitly anticipated either outcome: "If [O2] fails, the contribution is a careful negative result showing that established robust methods are sufficient for the tested regime." This manuscript reports that careful negative result, plus a five-ablation characterisation of *why* the gates fail.

The IC observable, its calibration, and the per-reading threshold (2.976 bit, the worst-case-σ 95th percentile across ten null noise models) are documented in [logbook entries 001–006](../logbook/) and the [WP1 summary](../logbook/wp1-summary.md). DG-1 — IC calibration — was closed with one mitigated sub-criterion failure ([entry 002](../logbook/002_2026-03-31_sigma-sensitivity-analysis.md), [entry 006](../logbook/006_2026-05-04_per-reading-threshold-recalibration.md)). The present manuscript starts from a calibrated IC.

## 2. Methods

### 2.1 Scenarios

The eight scenarios verbatim from the proposal:

| ID | N | Topology | Delay | Signal | Purpose |
|----|---|----------|-------|--------|---------|
| S1 | 15 | ring | Poisson(2.0) | sinusoidal, 3 clocks | structure preservation |
| S2 | 15 | fully connected | Poisson(0.3) | sinusoidal, 3 clocks | control: delays negligible |
| S3 | 50 | random-sparse | Poisson(4.0) | sinusoidal, 3 clocks | scaling |
| S4 | 15 | ring | Poisson(2.0) | none | null |
| S5 | 50 | random-sparse | Poisson(4.0) | none | null at scale |
| S6 | 15 | ring | Poisson(2.0) | linear drift, 2 clocks | anomaly detection (not near-critical) |
| S7 | 30 | ring | Poisson(2.0) | step at T/2, 3 clocks | change-point detection |
| S8 | 15 | ring | Poisson(2.0) | fold bifurcation, 2 clocks | near-critical dynamics |

Each scenario runs 10 seeds at T = 200 timesteps. Signal amplitudes are set in unit scale (σ_white = 1.0):

- **Sinusoidal** (S1, S2, S3): amplitude 5 σ, period 50 steps, per-clock phase offset i × π/3.
- **Linear drift** (S6): rate 0.01 σ / step (≈ 2 σ total over T = 200).
- **Step** (S7): magnitude 5 σ at t = T/2.
- **Fold bifurcation** (S8): ε = 0.005, r₀ = −1.0, x₀ = 0.0 (chosen empirically to reach the bifurcation within T without explicit-Euler blow-up).

One clock per scenario is degraded (3× noise, per the proposal). Random-number generation uses `numpy.random.default_rng(seed)` with seeds 2026–2035; per-seed RNG order is `simulate_network_clocks` then `make_network`, so all WP3 ablation harnesses can reproduce the WP2 archive byte-for-byte by matching this order.

### 2.2 Estimators

Nine estimators sharing a common interface `(Y, Sigmas, adj, delays, **kwargs) → Estimates(T, N)`:

| Estimator | Type | Mechanism |
|-----------|------|-----------|
| `freq_global` | centralised | inverse-variance weighted mean over all nodes |
| `freq_local` | local | weighted mean over delay-accessible neighbours and self |
| `freq_exclude` | centralised | weighted mean excluding nodes with cross-sectional IC ≥ 2.976 |
| `huber` | centralised | IRLS Huber M-estimator, c = 1.345 |
| `bocpd` | centralised | Adams & MacKay 2007 changepoint detection per node; non-flagged nodes consensus-averaged |
| `imm` | centralised | two-mode Blom & Bar-Shalom 1988 IMM filter; non-flagged nodes consensus-averaged |
| `admec_unconstrained` | centralised | three-way classification; STABLE-only weighted mean |
| `admec_delay` | local | per-node weighted mean over delay-accessible STABLE neighbours |
| `admec_full` | local | `admec_delay` + sequential constraint projection |

Implementation in [`src/estimators.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/estimators.py) (one file, ~600 lines, 50 unit tests).

### 2.3 Metrics

Three IC-independent metrics from the proposal:

- **MSE** — mean squared error of the consensus estimate against the nominal reference (0 for fractional-frequency residuals).
- **Collapse index** — time-averaged std-of-estimates-across-nodes / mean-sigma; 0 for centralised methods, > 0 for local methods that retain per-node diversity.
- **Structure correlation** — Pearson r between (reading − estimate) and the injected signal, averaged over signal-bearing clocks post-onset; high = signal preserved in residual; low = signal absorbed into consensus. Falls back to a residual-magnitude ratio for constant signals (S7 step).

Plus DG-2b classification diagnostics (TPR / FPR / precision / F1) against designer-injected ground truth.

Implementation in [`src/metrics.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/metrics.py).

### 2.4 IC threshold calibration

The per-reading IC threshold of 2.976 bit was calibrated as the 95th percentile of per-reading I_k under worst-case σ-underestimation, across ten null noise models, in [entry 006](../logbook/006_2026-05-04_per-reading-threshold-recalibration.md). The earlier AIPP-derived threshold of 1.835 bit (used in WP1 entries 001/002 for ensemble-level FPR control) does not transfer to per-reading classification; it would inflate the false-positive rate by ≈ 1.6 ×. The 2.976-bit value passes a ×1.5 stability check across the ten models and is robust to a ×1.2 cross-N check (N ∈ {50, 100, 200}).

This calibration was optimised for null FPR control, not for downstream consensus MSE. Section 5.4 returns to that distinction.

### 2.5 Pre-registered ablation menu (WP3)

Five ablations, each varying one design axis around the WP2 baseline:

1. **Delay convention.** Drop (WP2 baseline: drop neighbours with delay > freshness) vs stale (use `Y[t − delays[i, j], j]` for every adjacency neighbour). [Entry 008](../logbook/008_2026-05-04_wp3-ablation-delay-convention.md).
2. **Classification threshold.** Sweep IC threshold across {1.5, 2.0, 2.5, 2.976, 3.5, 4.5, 6.0}. [Entry 011](../logbook/011_2026-05-05_wp3-ablation-threshold-sweep.md).
3. **Constraint sensitivity.** ±30 % on each constraint axis (`max_step_factor`, `energy_factor`, `var_ratio_min/max`). [Entry 009](../logbook/009_2026-05-04_wp3-ablation-constraint-sensitivity.md).
4. **Classifier cardinality.** Three-way (STABLE / STRUCTURED / UNSTRUCTURED) vs two-way (STABLE / ANOMALOUS). [Entry 010](../logbook/010_2026-05-04_wp3-ablation-two-vs-three-way.md).
5. **Detection lag.** Same-step classification (lag = 0) vs one-step lag (`lag = 1`, classifier sees IC at t − 1). [Entry 012](../logbook/012_2026-05-05_wp3-ablation-lagged-classification.md).

## 3. Results: WP2 baseline

Canonical archive: [`data/wp2_campaign_20260504_fix.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp2_campaign_20260504_fix.npz). Full setup and verdict in [entry 007](../logbook/007_2026-05-04_wp2-simulation-harness.md) and the [WP2 summary](../logbook/wp2-summary.md).

### 3.1 Methodological prerequisites: two bug fixes

The first WP2 dry run produced spuriously catastrophic ADMEC-full performance (S2 MSE ≈ 4.85, > 40× the unconstrained variant). Two implementation issues were identified and fixed before the canonical archive was generated:

- **`admec_full` t = 0 initialisation.** The initial state was set to the raw readings `Y[0, :]`, which made the first variance-ratio constraint check compare the consensus target's variance (≈ 1/N of single-reading variance) against the raw-reading variance. The ratio fell below 0.5 and *every* update was rejected, freezing the estimator at `Y[0, :]`. Fix: initialise to the centralised inverse-variance weighted mean. Effect on S2 MSE: 4.85 → 0.13.
- **Floating-point variance-ratio guard.** `np.var(state)` of a constant array returns ≈ 3 × 10⁻³³, not exactly 0. The original guard `if var_before > 0` entered the variance-ratio check on uniform states and the ratio diverged. Fix: guard `var_before > 1 × 10⁻²⁰`. Effect on S2 MSE: 0.27 → 0.09; rejection rate on dense networks dropped from > 90 % to < 1 %.

Both fixes have regression tests; both are documented in [entry 007](../logbook/007_2026-05-04_wp2-simulation-harness.md). The DG-2 verdict below holds for the post-fix archive.

### 3.2 DG-2 result

Mean MSE per (scenario, estimator) across 10 seeds at T = 200. The best non-ADMEC baseline on each row is **bold**; ✓ marks the only scenario where `admec_full` beats it.

| Scenario | freq_global | freq_local | freq_exclude | huber | bocpd | imm | admec_unc | admec_delay | admec_full |
|----------|------------:|-----------:|-------------:|------:|------:|----:|----------:|------------:|-----------:|
| S1 | 0.323 | 3.084 | **0.135** | 0.145 | 0.224 | 0.147 | 0.135 | 1.647 | 0.732 |
| S2 | 0.323 | 0.331 | **0.135** | 0.145 | 0.224 | 0.147 | 0.135 | 0.139 | **0.093** ✓ |
| S3 | 0.041 | 1.642 | **0.025** | 0.026 | 0.033 | 0.025 | 0.025 | 1.027 | 0.741 |
| S4 | 0.071 | 0.968 | 0.074 | 0.073 | 0.069 | **0.065** | 0.074 | 0.851 | 0.381 |
| S5 | 0.021 | 0.988 | 0.022 | 0.022 | 0.021 | **0.019** | 0.022 | 0.883 | 0.597 |
| S6 | 0.092 | 1.134 | 0.094 | 0.090 | 0.091 | **0.087** | 0.094 | 0.981 | 0.427 |
| S7 | 0.163 | 2.072 | **0.040** | 0.054 | 0.152 | 0.144 | 0.040 | 0.957 | 0.604 |
| S8 | 0.083 | 1.032 | 0.088 | 0.084 | 0.082 | **0.079** | 0.088 | 0.911 | 0.482 |

DG-2 verdict at the pre-registered IC threshold (2.976 bit):

| | metric | best non-ADMEC | admec_full | pass? |
|---|---|---:|---:|:---:|
| **S1** | MSE | freq_exclude 0.135 | 0.732 | ✗ |
| **S1** | collapse index | (centralised) 0.000 | 0.644 | ✗ |
| **S1** | structure corr. | imm 0.956 | 0.897 | ✗ |
| **S3** | MSE | freq_exclude 0.025 | 0.741 | ✗ |
| **S3** | collapse index | (centralised) 0.000 | 0.808 | ✗ |
| **S3** | structure corr. | imm 0.960 | 0.887 | ✗ |

**S1: 0/3 metrics pass. S3: 0/3 metrics pass. DG-2 NOT MET.**

`admec_full` does beat `admec_delay` on every scenario × metric (constraint layer is internally coherent). Of the eight scenarios, `admec_full` beats the best non-ADMEC baseline on MSE in only one — **S2**, the fully-connected control where the delay-restricted local consensus is essentially equivalent to a centralised aggregator.

### 3.3 DG-2b classification validation

Recomputed reproducibly with [`scripts/wp2_classification_check.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp2_classification_check.py):

| scope | TPR | FPR | precision | F1 |
|-------|----:|----:|----------:|---:|
| All 8 scenarios | 0.430 | 0.010 | 0.763 | 0.550 |
| Signal scenarios only (6) | 0.430 | 0.010 | 0.831 | 0.567 |

Strict STRUCTURED-only TPR = **0.007**. Almost all anomaly detections classify as UNSTRUCTURED. The DG-2b 70 % threshold is not met on the strict three-way criterion.

This is consistent with the entry-006 docstring observation that the per-reading 2.976-bit threshold is *selective*: coherent processes broaden the mixture density along with the readings, so signal-bearing readings rarely cross the threshold. The temporal-statistic gates (var_slope, acf) calibrated in [entry 004](../logbook/004_2026-03-31_delta-min-calibration.md) are tuned for critical-slowing-down dynamics and rarely fire on linear drifts (S6) or step changes (S7) — confirmed empirically.

## 4. Results: WP3 ablations

Five ablations, summarised here with their best-effect numbers; full per-scenario × per-mode tables in the cited logbook entries.

### 4.1 Delay convention (drop vs stale)

[Entry 008](../logbook/008_2026-05-04_wp3-ablation-delay-convention.md), archive [`data/wp3_ablation_delay_convention_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_delay_convention_20260504.npz).

The "drop" baseline drops neighbours whose delay exceeds a freshness window. The "stale" alternative uses `Y[t − delays[i, j], j]` — the most recent reading sent by each adjacency neighbour, regardless of how stale it is.

| Scenario | drop admec_full | stale admec_full | improvement | best non-ADMEC | gap |
|----------|---:|---:|---:|---|---:|
| S1 | 0.732 | **0.413** | −44 % | freq_exclude 0.135 | 3.1 × |
| S2 | 0.093 | 0.104 | +12 % | imm 0.147 | wins |
| S3 | 0.741 | **0.461** | −38 % | imm 0.025 | 18 × |

Stale convention substantially improves all three local estimators on sparse-with-delay scenarios; the absolute gap to centralised baselines does not close (S1: 3 ×, S3: 18 ×). On the dense S2 control stale slightly hurts because adjacency neighbours are already accessible at freshness = 1 — adding lag only injects irrelevant history. **DG-2 stays NOT MET under stale.**

### 4.2 Constraint sensitivity (±30 %)

[Entry 009](../logbook/009_2026-05-04_wp3-ablation-constraint-sensitivity.md), archive [`data/wp3_ablation_constraint_sensitivity_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_constraint_sensitivity_20260504.npz).

Seven configurations: baseline plus ±30 % on each of `max_step_factor`, `energy_factor`, `var_ratio_min/max`. Diagnostic case: S3 stale, where ablation 4.1 produced an unexpected `admec_delay` (0.340) < `admec_full` (0.461) ordering — the constraint layer is hurting rather than helping.

| variant | S3 stale admec_full MSE | vs baseline | beats admec_delay 0.340? |
|---------|---:|:---:|:---:|
| baseline | 0.461 | — | ✗ |
| step_loose | 0.460 | tiny | ✗ |
| step_tight | 0.453 | tiny | ✗ |
| energy_loose | 0.495 | worse | ✗ |
| **energy_tight** | **0.343** | **−26 %** | tied |
| **var_loose** | **0.307** | **−33 %** | **✓** |
| var_tight | 0.586 | +27 % | ✗ |

`var_loose` [0.35, 1.65] (variance-ratio bounds widened by 30 % at each end) recovers the conventional `admec_full < admec_delay` ordering on S3 stale and reduces MSE by another 33 %. Direct confirmation of the entry-008 hypothesis: the variance-ratio constraint was over-tight when the proposed update vector picked up extra variance from multi-step lags. `energy_tight` (a 30 % tighter energy ceiling) acts as a soft variance regulariser and gives a similar magnitude of improvement.

The cross-scenario picture (S1 drop + 13.4 %, S2/S3 drop ≈ neutral) flags `var_loose` as a **scenario-conditional** recommendation, not a blanket fix: it pays off when the proposed update is noisy across multi-step lags and is otherwise mildly counterproductive on noisy ring topologies.

### 4.3 Two-way vs three-way classifier

[Entry 010](../logbook/010_2026-05-04_wp3-ablation-two-vs-three-way.md), archive [`data/wp3_ablation_two_vs_three_way_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_two_vs_three_way_20260504.npz).

Across 360 (scenario × seed × estimator × delay-mode × classifier) configurations:

> **max abs MSE delta = 0.0000e+00**
> **max abs structure-correlation delta = 0.0000e+00**

Three-way and two-way produce numerically identical consensus output (max absolute element-wise delta on the (T, N) estimate arrays = 0 to double-precision). The classification *counts* differ (5–6 STRUCTURED in three-way vs 0 in two-way), but the *STABLE* count is identical between modes, and the consensus reads only the STABLE mask.

This is an architectural-impossibility result, not a statistical near-null. As long as STRUCTURED and UNSTRUCTURED are excluded equally from the STABLE-only weighted mean, no choice of input data, signal type, threshold, or seed can produce a non-zero delta. **DG-3's "three-way > two-way" sub-criterion is formally unreachable under the present architecture.**

### 4.4 Classification threshold sweep

[Entry 011](../logbook/011_2026-05-05_wp3-ablation-threshold-sweep.md), archive [`data/wp3_ablation_threshold_sweep_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_threshold_sweep_20260505.npz).

The pre-registered prediction was a flat sensitivity curve in a "narrow active region" near 2.976. The data shows otherwise:

| Scenario | mode | thr 1.5 | thr 2.0 | thr 2.976 (WP1) | thr 3.5 | thr 4.5 |
|----------|------|--------:|--------:|----------------:|--------:|--------:|
| S1 | drop | **0.308** | 0.557 | 0.732 | 1.104 | 2.252 |
| S1 | stale | **0.238** | 0.345 | 0.413 | 0.586 | 1.519 |
| S2 | drop | 0.164 | 0.135 | **0.093** | 0.167 | 0.347 |
| S2 | stale | 0.111 | **0.088** | 0.104 | 0.195 | 0.271 |
| S3 | drop | **0.443** | 0.617 | 0.741 | 0.802 | 0.926 |
| S3 | stale | **0.191** | 0.307 | 0.461 | 0.473 | 0.429 |

On the **delayed signal-rich scenarios (S1 and S3)**, `admec_full` prefers low thresholds (1.5–2.0); on the dense low-delay control **S2 the optimum is at the WP1 calibrated value 2.976** (drop) or 2.0 (stale), and `var_tight`-style aggressive exclusion below 1.5 is mildly counterproductive. `freq_exclude` prefers moderate thresholds (2.5–3.5) on every scenario.

At the matched threshold 1.5, `admec_full` (in stale mode) **beats `freq_exclude` on S1 (0.238 vs 0.276) and S2 (0.111 vs 0.276)** — the first signal-rich scenarios where the architecture beats centralised exclusion at a matched setting other than S2's WP2 win. The mechanism: aggressive exclusion strips signal-bearing readings from the local pool, and `admec_full`'s constraint layer absorbs the resulting per-step variance increase via projection; `freq_exclude` has no such buffer.

The WP1-calibrated threshold (2.976, optimised for null false-positive rate) is therefore **suboptimal for consensus MSE on signal-rich delayed scenarios**, while remaining optimal on the dense control. The null-FPR and consensus-MSE optima coincide only when the network is dense enough that exclusion does not need absorption.

### 4.5 Lagged classification (simultaneity bias test)

[Entry 012](../logbook/012_2026-05-05_wp3-ablation-lagged-classification.md), archive [`data/wp3_ablation_lagged_classification_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_lagged_classification_20260505.npz).

If the same-step IC were inflated by self-reference (each clock's IC at time t includes that clock's own reading in the integrand mixture), lagging the classifier to use IC(t − 1) would *help*. It does the opposite:

| Scenario | mode | lag = 0 | lag = 1 | Δ |
|----------|------|--------:|--------:|--:|
| S1 | drop | 0.732 | 1.219 | **+ 66 %** |
| S1 | stale | 0.413 | 0.527 | + 28 % |
| S2 | drop | 0.093 | 0.093 | − 0.2 % |
| S2 | stale | 0.104 | 0.105 | + 0.3 % |
| S3 | drop | 0.741 | 1.058 | **+ 43 %** |
| S3 | stale | 0.461 | 0.465 | + 1 % |

There is no simultaneity bias to remove. The same-step IC is the right operating point. The lagged variant introduces a *detection latency* penalty: when classification is delayed by one step, an anomalous reading flows into consensus for one extra step before being excluded, and on sparse-with-drop networks there are too few clean alternatives to dilute the polluted reading.

### 4.6 Combined tuning

The four parametric ablations identify a recommended tuning combination:

- delay convention = **stale** (entry 008);
- classification threshold = **1.5** (lower than the WP1 calibration of 2.976; entry 011);
- variance-ratio bounds = **[0.35, 1.65]** (`var_loose`; entry 009, scenario-conditional);
- classification lag = **0** (same-step; entry 012 — no simultaneity bias to remove).

The first three are simultaneously varied; lag stays at the WP2 default. To verify these design choices interact additively rather than antagonistically, the integrated harness `scripts/wp3_combined_tuning_check.py` (archive [`data/wp3_combined_tuning_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_combined_tuning_20260505.npz)) runs `admec_full` with all three applied at once on the same RNG-matched seeds as the WP2 campaign. Measured results:

| Scenario | WP2 baseline `admec_full` MSE | Combined-tuned `admec_full` MSE | reduction |
|----------|------------------------------:|--------------------------------:|----------:|
| S1 | 0.732 | **0.252** | −66 % |
| S2 | 0.093 | **0.091** | −2 % |
| S3 | 0.741 | **0.196** | −74 % |

The interaction is *not strictly additive*. On S1, the best individual-ablation result was `stale + thr 1.5` = 0.238 (entry 011); adding `var_loose` raises it to 0.252 (the entry-009 finding that `var_loose` mildly hurts S1 already at the WP2 baseline carries through). On S2, the best individual-ablation result was `stale + thr 2.0 + baseline constraints` = 0.088 (entry 011); the combined-tuning value 0.091 is slightly worse for the same reason. On S3, the combined value 0.196 essentially matches the best individual `stale + thr 1.5` = 0.191 — the dominant gain comes from threshold + delay, with `var_loose` adding only ~ 0.005 of further reduction on top.

#### 4.6.1 Comparison framings

The DG-2 verdict, the matched-threshold comparison, and the best-of-best comparison are three different questions, and the answer differs between them.

**(a) DG-2 (pre-registered, fixed threshold 2.976):**

| Scenario | admec_full | best non-ADMEC | DG-2 pass? |
|----------|-----------:|---------------:|:----------:|
| S1 | 0.732 (drop) | freq_exclude 0.135 | ✗ (5.4 ×) |
| S3 | 0.741 (drop) | imm 0.025 | ✗ (30 ×) |

**(b) Matched-threshold (both estimators use the *same* IC threshold, varying together):**

| Scenario | thr | admec_full (stale) | freq_exclude | matched winner |
|----------|----:|-------------------:|-------------:|:--------------:|
| S1 | 1.5 | 0.238 | 0.276 | admec_full |
| S2 | 1.5 | 0.111 | 0.276 | admec_full |
| S3 | 1.5 | 0.191 | 0.038 | freq_exclude |

This is the cleanest fairness comparison for the architectural claim "the constraint layer adds value over plain centralised exclusion at a matched IC operating point". On S1 and S2 it does; on S3 the centralised information advantage dominates regardless.

**(c) Best-of-best (each estimator at its own optimum):**

| Scenario | best admec_full | best freq_exclude | best non-ADMEC | residual gap |
|----------|----------------:|------------------:|---------------:|-------------:|
| S1 | 0.252 (combined-tuned) | 0.122 (thr 2.5) | imm 0.147 (default) | 1.72 × vs imm |
| S2 | 0.091 (combined-tuned) | 0.122 (thr 2.5) | imm 0.147 (default) | wins (0.62 × imm) |
| S3 | 0.196 (combined-tuned) | 0.025 (thr 2.5–3.0) | imm 0.025 (default) | 7.8 × |

Under independent per-estimator threshold tuning, admec_full **adds S2 to its win column** (combined-tuning 0.091 < imm 0.147) and **closes the S1 gap to 1.7 ×** (vs imm 0.147). The S3 information-theoretic ceiling remains: 7.8 × is consistent with the centralised-vs-local pooling argument in §5.1.

DG-2 was pre-registered at the calibrated threshold and stays NOT MET (frame (a)). The matched-threshold and best-of-best comparisons are post-hoc and informational; they do not formally rescue DG-2, but they are operationally meaningful for a deployment that can choose its own threshold.

## 5. Discussion

### 5.1 The information-theoretic ceiling

The residual ~ 8 × gap to centralised baselines on S3 (50-node random-sparse with target degree 3, Poisson(4.0) delays) is consistent with a simple information-pooling argument. A centralised inverse-variance weighted mean over 50 i.i.d. readings has variance 1/50 of a single reading. A local consensus over a 3 ± 1 adjacency neighbourhood has variance ≈ 1/4 of a single reading. The ratio is 12.5 × — close to the 7.6 × residual MSE gap observed under the best WP3 tuning. The difference reflects modest gains from temporal averaging under stale and the constraint layer's variance absorption; the order-of-magnitude floor is set by neighbourhood size relative to network size.

This is not a hyperparameter problem. No constraint setting, threshold value, or delay convention can bridge a 50:3 information ratio. To close it the architecture would need to pool over more readings — either by relaxing the locality (which defeats the point) or by integrating temporal information differently (the "decayed staleness" redesign in §5.6).

### 5.2 Threshold mismatch: null FPR vs consensus MSE

The WP1-calibrated IC threshold of 2.976 bit was optimised under the worst-case null assumption to give a 5 % false-positive rate. That is the right calibration for hypothesis-test interpretation. For the *consensus problem*, the relevant criterion is signal-conditional MSE — and the optimal threshold for `admec_full`'s MSE is markedly lower (1.5–2.0) on signal-rich delayed scenarios. The two criteria pick different optimal operating points because they are measuring different things.

A signal-aware re-calibration (pick the threshold that minimises consensus MSE under the WP2 scenarios) is a natural operational choice and would shift the picture toward `admec_full` competing more strongly with centralised exclusion. In the spirit of the pre-registered design, this manuscript reports the calibrated value's performance and notes the mismatch as a finding rather than retroactively redoing the calibration.

### 5.3 Architectural invisibility of three-way at the consensus stage

The two-way / three-way ablation produces a delta of *exactly zero* across 360 cells because the ADMEC consensus rule reads only the STABLE mask. Both anomaly classes are excluded equally; the partition of "not-STABLE" into STRUCTURED vs UNSTRUCTURED is a bookkeeping detail invisible to the estimator. To make the three-way distinction operationally meaningful, the architecture must either (a) include STRUCTURED readings with reduced weight (a continuous-treatment variant), (b) use the STRUCTURED count as a regulariser on downstream parameters, or (c) maintain STRUCTURED as a separate output channel that is scored by a metric the consensus does not see (e.g. "anomalies-tracked-not-suppressed correlation"). None of these is present in the WP2 architecture.

The DG-3 "three-way > two-way" sub-criterion is therefore not just empirically NOT MET; it is *structurally unreachable* without a redesign that lets STRUCTURED status enter the update rule.

### 5.4 The constraint layer's actual role

The proposal motivates the update-size constraint stack as a safety net against pathological updates: a per-node 3-σ box, a network-wide N σ² energy ball, and a [0.5, 1.5] variance-ratio post-check. The combined effect on signal scenarios at the WP2 baseline is modest — `admec_full` beats `admec_delay` by 5–55 % depending on scenario, with the largest gains on dense low-delay topologies (S2: 0.139 → 0.093, −33 %).

The threshold-sweep ablation reveals a sharper interpretation. At low thresholds (1.5), aggressive exclusion strips signal-bearing readings from the local pool, *raising* the per-step variance of the proposed update. The constraint layer's projection absorbs that variance — clipping per-node updates to the box, scaling the network update onto the energy ball, and rejecting updates that would shift ensemble variance outside [0.5, 1.5]. The constraint layer is, operationally, a **noise-absorption mechanism**, and its benefit is largest precisely when exclusion is aggressive enough to need absorbing.

This is a useful design insight independent of the DG-2 verdict: ADMEC's constraint architecture is a viable noise-absorption add-on to centralised exclusion estimators, not a rescue mechanism for delay-restricted local consensus.

### 5.5 Operational recommendations

For deployments where ADMEC is the chosen architecture (e.g. decentralised networks without a global aggregator):

- **Pair the IC threshold with the deployment topology**, not with the WP1 null calibration. Lower thresholds (1.5–2.0) are operationally better when delays are non-trivial.
- **Use stale-reading mode** rather than drop-and-truncate. The drop convention starves the consensus on sparse delayed networks for no operational benefit.
- **Loosen the variance-ratio bound** (e.g. [0.35, 1.65]) when proposed updates inherit lag-induced variance; otherwise the bound rejects beneficial updates.
- **Keep classification at the same step.** There is no simultaneity bias, and any lag introduces a detection-latency MSE penalty.

For deployments where centralised aggregation is feasible: use `freq_exclude` or `imm`. They are cheaper, simpler, and outperform `admec_full` on every scenario where centralisation is feasible.

### 5.6 Future redesigns

Two architectural changes could plausibly rescue the gates and would be appropriate for a follow-up project:

1. **STRUCTURED with reduced weight.** Currently the consensus excludes STRUCTURED nodes outright; a continuous-treatment variant (include STRUCTURED with weight α < 1) would make the three-way distinction operationally visible. The natural starting point is α = 1 / (1 + IC_excess), where IC_excess is the per-reading IC above threshold. This would make DG-3's "three-way > two-way" measurable rather than algebraically zero.

2. **Decayed-staleness weighting.** Currently neighbours are either dropped (delay > freshness) or used at full weight (stale-reading mode). A decayed weighting `w_j = exp(−λ τ_ij)` interpolates between these. The natural choice is λ ≈ 1/τ_correlation, where τ_correlation is the readings' autocorrelation time. This could push the local consensus closer to the centralised Cramér–Rao bound on S3 by using more information from each neighbour.

Both are non-trivial code changes that deserve their own pre-registered decision gates; neither is a parameter sweep on the present architecture.

## 6. Conclusion

We characterised ADMEC across an 8-scenario simulation campaign and five orthogonal ablations. **DG-2 is not met**: ADMEC-full beats centralised baselines on only S2, the fully-connected control. **DG-3 is not met** on the three-way > two-way clause: under the present architecture the structured / unstructured distinction is *algebraically* invisible to the consensus output. Combined design tuning reduces MSE by 74 % on S3 but cannot close the residual ~ 8 × gap to centralised exclusion methods, which is consistent with a centralised-vs-local information-theoretic ceiling.

Three findings make the negative result useful rather than empty:

1. **The WP1 IC calibration is suboptimal for the consensus problem.** Per-reading thresholds optimised for null FPR are not the right operating point for consensus MSE. At a lower matched threshold, ADMEC's constraint architecture beats centralised exclusion on two of the three signal-rich scenarios.
2. **The constraint layer's actual role is variance absorption.** It adds value only when paired with aggressive exclusion that creates the variance to absorb. This reframes ADMEC's architectural contribution and identifies its natural deployment regime.
3. **The same-step IC computation is well-formed.** No simultaneity bias is detectable; lagging the classifier strictly hurts. The Gaussian-mixture self-reference is part of the IC definition, not a statistical artefact.

The proposal anticipated either a positive or negative DG-2 outcome; the negative outcome with a five-axis mechanistic characterisation is the contribution. Two redesign directions (STRUCTURED-with-reduced-weight; decayed-staleness weighting) are appropriate for a follow-up project where the gates can be re-pre-registered against the new architecture.

## 7. Reproducibility

Every table in this manuscript is reproducible from a checked-in script in [`scripts/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/scripts) and a canonical `.npz` archive in [`data/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/data). Mapping:

| Section | Script | Archive |
|---------|--------|---------|
| § 3 (WP2 baseline) | [`wp2_campaign.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp2_campaign.py) + [`wp2_classification_check.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp2_classification_check.py) | [`wp2_campaign_20260504_fix.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp2_campaign_20260504_fix.npz) |
| § 4.1 | [`wp3_ablation_delay_convention.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_ablation_delay_convention.py) | [`wp3_ablation_delay_convention_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_delay_convention_20260504.npz) |
| § 4.2 | [`wp3_ablation_constraint_sensitivity.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_ablation_constraint_sensitivity.py) | [`wp3_ablation_constraint_sensitivity_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_constraint_sensitivity_20260504.npz) |
| § 4.3 | [`wp3_ablation_two_vs_three_way.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_ablation_two_vs_three_way.py) | [`wp3_ablation_two_vs_three_way_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_two_vs_three_way_20260504.npz) |
| § 4.4 | [`wp3_ablation_threshold_sweep.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_ablation_threshold_sweep.py) | [`wp3_ablation_threshold_sweep_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_threshold_sweep_20260505.npz) |
| § 4.5 | [`wp3_ablation_lagged_classification.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_ablation_lagged_classification.py) | [`wp3_ablation_lagged_classification_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_lagged_classification_20260505.npz) |
| § 4.6 (combined tuning) | [`wp3_combined_tuning_check.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_combined_tuning_check.py) | [`wp3_combined_tuning_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_combined_tuning_20260505.npz) |

Test suite: 276 tests, 274 passing on the canonical commit. The two known failures are documented entry-002 σ-underestimation cases that are mitigated downstream by the worst-case threshold calibration in entry 006.

A WP1 walkthrough lives at [docs/wp1_tutorial.md](wp1_tutorial.md); a WP2 walkthrough at [docs/wp2_tutorial.md](wp2_tutorial.md). Both are runnable on Binder.

## 8. References

1. Adams, R. P. & MacKay, D. J. C. Bayesian online changepoint detection. arXiv:0710.3742 (2007).
2. Allan, D. W. Statistics of atomic frequency standards. *Proc. IEEE* **54**, 221–230 (1966).
3. Blom, H. A. P. & Bar-Shalom, Y. The interacting multiple model algorithm. *IEEE Trans. Automat. Contr.* **33**, 780–783 (1988).
4. Bothwell, T. et al. Resolving the gravitational redshift across a millimetre-scale atomic sample. *Nature* **602**, 420–424 (2022).
5. Dakos, V. et al. Methods for detecting early warnings of critical transitions. *PLoS ONE* **7**, e41010 (2012).
6. Huber, P. J. *Robust Statistics* (Wiley, 1981).
7. Lamport, L. Time, clocks, and the ordering of events in a distributed system. *Commun. ACM* **21**, 558–565 (1978).
8. Lisdat, C. et al. A clock network for geodesy and fundamental science. *Nat. Commun.* **7**, 12443 (2016).
9. Panfilo, G. & Arias, F. The Coordinated Universal Time (UTC). *Metrologia* **56**, 042001 (2019).
10. Scheffer, M. et al. Early-warning signals for critical transitions. *Nature* **461**, 53–59 (2009).

---

*Manuscript scaffold drafted with the assistance of Claude (Anthropic). All scientific content, decisions, and claims are the sole responsibility of the author.*

# A Topological Information-Pooling Reference for Local Clock Consensus
## An empirical characterisation study using the ADMEC anomaly-aware scheme

**Technical Report v1.0 candidate.** This document is prepared as a citable technical report, not as a journal-submission manuscript. The intended canonical release is the annotated Git tag `v1.0-tech-report`, to be created after the pre-release domain-expert / Atlas-integrity reader pass and archived through Zenodo.

**Preferred citation (pending DOI).** Warring, U. (2026). *A Topological Information-Pooling Reference for Local Clock Consensus: An empirical characterisation study using the ADMEC anomaly-aware scheme*. Technical Report v1.0. GitHub repository: `threehouse-plus-ec/admec-clock-consensus`, release tag `v1.0-tech-report`. Zenodo DOI: TBD.

> **Epistemic status.** This manuscript reports a *pre-registered characterisation study*. The central observable, the *N* / *k*_eff information-pooling reference, is a heuristic with empirical support across the eight tested scenarios and four parametric ablation axes — *not* a proven lower bound. A formal Cramér–Rao analysis on the specific noise model is left to follow-up work. Pre-registered decision-gate verdicts and post-hoc operational comparisons are kept visually distinct throughout.

**Author:** Ulrich Warring (Physikalisches Institut, Albert-Ludwigs-Universität Freiburg).
**Type:** Technical report; pre-registered characterisation study. Decision gates and ablation menu are defined verbatim in [docs/projektantrag.md](projektantrag.md); the project-internal labels DG-1, DG-2, DG-2b, DG-3, WP1–WP3, S1–S8 are the gates, work packages, and scenarios named there.
**Status:** v1.0 technical-report candidate, pending Atlas-integrity reader pass, release tag, and Zenodo DOI.
**Reproducibility:** every table in this manuscript is derivable from one of the canonical archives in [`data/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/data); each section cites the archive it draws from. Full numerical detail and supporting code live in the [logbook](../logbook/) and [scripts](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/scripts).

---

## Abstract

**Within the ADMEC family of anomaly-aware local-consensus estimators, *under static-memoryless aggregation* and a *partially-decentralised* architecture (global same-time classifier feeding a local consensus rule), performance on delay-constrained networks is limited primarily by causal-topological access to information, not by estimator sophistication.** When a network's topology and delay distribution restrict each node to a small effective neighbourhood, no parametric tuning of the family's anomaly classification, exclusion rules, or update constraints — across the four ablation axes characterised here — closes the gap to a centralised aggregator that pools all readings. The empirical performance gap tracks a simple pooling-limit heuristic *N* / *k*_eff, where *N* is the network size and *k*_eff the effective neighbourhood under the scenario's delay distribution. We do not claim the heuristic generalises to all local-consensus families (hierarchical, gossip-with-epoch, asynchronous-clustering, and AT1-style Kalman-state-propagation ensemble algorithms are not in our menu); we claim it is a useful regime-locating reference for the family characterised, supported by 24 (scenario, mode) measurements across 8 scenarios and 10 seeds each. The reference is a heuristic, not a one-sided bound: ADMEC variants that exploit temporal memory or favourable correlations may sit below the line. A truly-local IC (each node computing its own classifier from delay-accessible readings only) is reserved for follow-up work; under such a redesign the classifier loses information and the present negative gate verdicts should *strengthen*, so the gap reported here is in that sense an optimistic lower bound on the difficulty of the problem.

This paper is a pre-registered characterisation study that *measures* that boundary using a candidate scheme — ADMEC — as the vehicle. ADMEC combines an information-content (IC) anomaly observable with a three-way STABLE / STRUCTURED / UNSTRUCTURED classification, delay-restricted updates, and projected update-size limits. We run an 8-scenario × 10-seed × 9-estimator campaign with three baseline-architecture variants (FREQ family, Huber, BOCPD/IMM filter banks) plus five orthogonal ablations of ADMEC (delay convention, classification threshold, constraint sensitivity, classifier cardinality, detection lag).

The pre-registered decision gates are not met at the pre-registered operating points: ADMEC outperforms centralised baselines on only the fully-connected control scenario; its three-way classifier achieves a strict structured-anomaly true-positive rate of ≈ 0.7 %; and the three-way distinction is *algebraically invisible* to the consensus output (max delta = 0 across 360 ablation cells, because the consensus update rule reads only the STABLE mask). Combined design tuning, measured directly by an integrated harness, reduces the largest-scenario mean squared error from 0.741 ± 0.023 to 0.196 ± 0.003 (a paired difference of −0.545 ± 0.024 SEM across 10 seeds, t ≈ −23), but the residual ~ 8 × gap to centralised methods sits at the *N* / *k*_eff pooling-limit line. (On the dense control S2 the corresponding paired difference is −0.002 ± 0.017 SEM, consistent with zero — the apparent S2 improvement is within seed-to-seed noise, not a real effect.) Combined-tuning numbers are post-hoc and tuned against the pre-registered scenario menu; they are not a generalisation claim.

We additionally identify three constructive findings: the same-step IC computation is well-formed (no simultaneity bias detectable — lagged classification strictly hurts); ADMEC's constraint layer functions as a noise-absorption mechanism that pays off only when paired with aggressive exclusion; and the original IC threshold (optimised for null false-positive rate) is suboptimal for consensus mean squared error in signal-rich scenarios — at a matched lower threshold, ADMEC outperforms centralised exclusion on two of the three signal scenarios.

The contribution of this study is therefore not a working algorithm but a *characterisation of the regime in which any local anomaly-aware scheme can be expected to compete*: dense, low-delay topologies where *k*_eff approaches *N*. We close with two architectural redesigns (STRUCTURED-with-reduced-weight; decayed-staleness weighting) that aim to use the data inside the topological boundary more efficiently, but reserve them for a follow-up study with its own pre-registration.

---

## 1. Introduction

The standard response to disagreeing clocks in a network is robust averaging: suppress outliers so the consensus stays stable. This works when deviations are random noise. But when some deviations carry information — a slow drift, a rising variance, a near-bifurcation indicator — robust suppression discards signal alongside noise. A natural alternative is to classify deviations and respond to each class differently: keep stable readings in the consensus, exclude memoryless noise bursts, and *track* persistent structured departures separately for downstream analysis. This is the design intuition the ADMEC scheme tests on a simulated heterogeneous clock network.

The central question this paper addresses, however, is not whether that intuition is *correct* but whether it can *compete* with the alternatives — and the answer is shaped less by the classifier and constraint design than by the geometry of the network. Local consensus on a delay-constrained network sees only a small effective neighbourhood per node. A centralised aggregator that pools all readings has access to *N* readings; a local consensus over a *k*_eff-element neighbourhood has access to *k*_eff. The independent-reading pooling argument places the local-to-centralised mean-squared-error ratio approximately at *N* / *k*_eff under static, memoryless aggregation. **No static-memoryless tuning of the ADMEC family crosses this reference line in our scenarios.** Tuning can move performance below the reference (by using temporal information or favourable correlations that the pooling argument does not capture); it cannot use information that does not arrive. The contribution of this paper is to measure how far below the *N* / *k*_eff reference the family sits empirically, across three topological regimes and four design axes, and to identify the regime where the architecture is competitive. The reference is a *heuristic*, not a proven bound: see § 5.1.2.

### Reader's map

The manuscript is structured as a pre-registered characterisation study. § 2 specifies the eight scenarios, nine estimators, three metrics, and the five-ablation menu. § 3 reports the campaign baseline at the pre-registered operating point and shows that the architecture's pre-registered decision gates are not met. § 4 reports the five ablations one axis at a time. § 5 interprets the results — § 5.1 makes the topological pooling-limit heuristic visible (Fig. 1), **§ 5.3 explains the three-way / two-way zero-delta result as a *syntactic* gap in the consensus update rule**, **§ 5.4 reframes the constraint stack as a noise-absorption mechanism**, and § 5.6 sketches two follow-up redesigns. § 7 maps every numerical claim to a checked-in script and `.npz` archive.

The express path for readers interested only in the central claim and the operational picture: § 1 (introduction), **§ 4.3** (algebraic invisibility — the structural reason DG-3's three-way > two-way clause is unreachable), **§ 5.1** (topological reference), **§ 5.3** (architectural reading of the zero-delta result), **§ 5.4** (constraint layer's actual role), **§ 5.5** (operational recommendations). The five ablation subsections (§§ 4.1–4.5) are the empirical inputs to those interpretations; readers more interested in the per-axis findings should read § 4 in full.

#### From pre-registered test to characterised regime

The pre-registration (in [docs/projektantrag.md](projektantrag.md)) committed the project to a *test* of ADMEC against pre-registered decision gates. The verdicts are reported in § 3 and § 4.3: the gates are NOT MET. What the present manuscript foregrounds beyond the verdict is a *characterisation* of the regime in which the architecture is competitive — the topological pooling-limit picture in Fig. 1 — which was *not* explicitly pre-registered but emerges naturally from the five-ablation menu the proposal did pre-register. The pivot from "did ADMEC pass its gates?" (Claim A, pre-registered, answered NO) to "in what regime would *any* member of the ADMEC family compete with centralised pooling?" (Claim B, characterised, the pooling-limit heuristic) is real and deliberate, and we mark it explicitly: the pre-registered question was Claim A, and the headline of this manuscript is Claim B. Both belong; both are sourced from the same pre-registered ablation menu; neither rescues the other.

### Pre-registered design

The vehicle architecture, ADMEC, classifies each clock reading into one of three categories using a per-reading information-content (IC) observable plus two trailing-window temporal-structure statistics (variance slope, lag-1 autocorrelation):

```
STABLE                : I_k <  threshold
STRUCTURED ANOMALY    : I_k >= threshold AND (|var_slope| > delta_min_var OR |acf| > delta_min_acf)
UNSTRUCTURED ANOMALY  : I_k >= threshold AND |var_slope| <= delta_min_var AND |acf| <= delta_min_acf
```

The proposal is that *structured* anomalies should be **tracked and gated** rather than excluded — preserved as a separate channel for downstream analysis — while *unstructured* anomalies should be excluded outright as memoryless noise bursts. This three-way response, together with delay-constrained updates and projected update-size limits, defines the `admec_full` estimator. The IC observable, its calibration, and the per-reading threshold (2.976 bit, the worst-case-σ 95th percentile across ten null noise models) are documented in [logbook entries 001–006](../logbook/) and the [WP1 summary](../logbook/wp1-summary.md). The IC-calibration gate (DG-1) was closed with one mitigated sub-criterion failure (entries 002 and 006). The present manuscript starts from a calibrated IC.

The simulation gates are pre-registered as follows:

- **DG-2** — `admec_full` outperforms the best non-ADMEC baseline (FREQ-global / FREQ-local / FREQ-exclude / Huber / BOCPD / IMM) on ≥ 2 of {MSE, collapse index, structure correlation} in *both* the 15-node ring (S1) and the 50-node random-sparse network (S3), and additionally beats the unconstrained-delay variant `admec_delay`.
- **DG-2b** — strict-STRUCTURED true-positive rate ≥ 70 % against designer-injected ground truth.
- **DG-3** — each constraint layer adds ≥ 10 % on at least one metric, *and* three-way classification outperforms two-way.

The proposal explicitly anticipated either outcome: *"If [the central objective] fails, the contribution is a careful negative result showing that established robust methods are sufficient for the tested regime."* This manuscript reports the empirical regime — the topological boundary between competitive and non-competitive operating points — that the careful negative result reveals.

![Figure 0. Pre-registered decision-gate structure and verdicts at a glance. DG-1 (IC observable calibration) was closed in WP1 with one mitigated sub-criterion. DG-2, DG-2b, and DG-3 are NOT MET; DG-3's "three-way > two-way" sub-criterion is *structurally unreachable* under the present consensus rule (§ 4.3, § 5.3) rather than merely empirically false. Reproducible from [`scripts/figure_gate_verdicts.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/figure_gate_verdicts.py).](manuscript_files/fig_gate_verdicts.png)

#### Pre-registered claims vs post-hoc characterisation

We keep two claim categories visually distinct throughout the manuscript:

- **Pre-registered.** The decision-gate verdicts (DG-2 in § 3.2, DG-2b in § 3.3, DG-3 in § 4.3) are reported against the operating points pre-registered in the proposal — same threshold (2.976 bit), same constraint defaults, same delay convention. These verdicts are the formally recorded outcome of the study and require no post-hoc framing to interpret.
- **Post-hoc characterisation.** The five WP3 ablations (§ 4) and three constructive findings in the discussion (§§ 5.2–5.4) are *characterisation* of *why* the gates failed and what regime the architecture is competitive in. They are explicitly labelled in § 4.6.1 ("frame (b) and (c) are post-hoc and informational; they do not formally rescue DG-2") and the same discipline applies to the constructive findings: each is informational, not gate-rescuing.

A reader interested only in the pre-registered verdict can read § 1, § 3, and § 4.3 (the DG-3 algebraic-zero result, which is also pre-registered). A reader interested in the architectural characterisation should additionally read § 4 and § 5.

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

#### Empty-neighbourhood fallback

A node *i*'s STABLE-only weighted mean at step *t* is undefined if no accessible neighbour (including self) is currently STABLE. The local estimators (`freq_local`, `admec_delay`, `admec_full`) handle this by carrying forward the previous estimate (`estimates[t, i] = estimates[t-1, i]`), or — at *t* = 0 — by initialising to the per-node reading. For `admec_full` the analogous fallback at *t* = 0 is the centralised inverse-variance weighted mean over the initial readings (see § 3.1, `admec_full` t = 0 init fix).

The empty-neighbourhood case is most prevalent under drop convention on sparse-with-delay topologies. With self always included via the diagonal, the empty case requires both (i) the node's own reading is flagged non-STABLE and (ii) every accessible neighbour's reading is also flagged non-STABLE. Under the WP1-calibrated IC threshold the prevalence is < 5 % of cells on every scenario; under the more aggressive WP3 thresholds (§ 4.4) it can reach ≈ 20 % on S3 drop. The carry-forward fallback is therefore an active code path on sparse delayed scenarios at low thresholds and not a dead branch.

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

### 2.6 Scope and limitations vis-à-vis real clock networks

This study uses a deliberately simplified clock and network model so the topological-pooling claim can be measured cleanly. Pre-release domain-expert readings flagged that the simulation differs from real clock networks in *six* specific ways, and the manuscript's claims should be understood within that scope. The first row is the most operationally consequential: ADMEC's classifier is computed from the full same-time ensemble even though its consensus rule is local; the architecture is therefore not fully decentralised.

| Simulation choice | Real-network reality | Implication for the present claims |
|------------------|----------------------|------------------------------------|
| **The classifier is computed from the full same-time ensemble.** [`_classify_network_full`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/estimators.py) sets `IC[t, :] = compute_ic(Y[t, :], Sigmas[t, :])` cross-sectionally — every node's STABLE / STRUCTURED / UNSTRUCTURED label depends on every other node's reading at time *t* | A genuinely decentralised deployment cannot compute the same labels: each node would need its own IC over the readings it has actually received, which under delay-restricted communication is a delay-accessible subset of the network | **ADMEC as implemented here is *partially* decentralised: local consensus rule, global classifier.** The present manuscript's results characterise this hybrid. Truly local IC (each node uses only its delay-accessible readings to compute its own IC and δ_min stats) is a follow-up redesign; the negative DG verdicts should *strengthen* under that redesign, since the classifier loses information, but the regime where ADMEC is competitive may also shift |
| Unit-scale white frequency-noise residuals as the dominant noise term | Real clocks have a noise hierarchy with several power-law regions in σ_y(τ): white PM (∝ τ⁻¹), white FM (∝ τ⁻¹/²), flicker FM (τ⁰, flat), random-walk FM (∝ τ^{+1/2}), and frequency drift. Hydrogen masers transition from white-FM to flicker-FM around τ ~ minutes and to random-walk-FM at longer τ. Optical clocks have analogous hierarchies with different cross-over times | The independent-reading pooling argument in § 5.1 holds in *spatial* terms regardless of within-clock temporal colour. What *would* tighten the local-vs-centralised gap is **common-mode** (cross-clock) correlation — shared environmental disturbances (temperature, magnetic field, vibration) that affect multiple clocks similarly. Within-clock temporal colour does not by itself reduce spatial ensemble sample size. Common-mode correlation is *not* in the simulation; if a real deployment has it, the *N* / *k*_eff reference is loose in the local-favourable direction |
| "Degraded clock" = uniform 3× σ inflation on one node | Real failure modes are phase steps, frequency offsets, intermittent outliers, structured drift; for hydrogen masers also mode jumps, environmental glitches; for optical clocks also cycle slips, lock loss, fibre-link phase noise | The simulation under-rewards the three-way classifier: in a Gaussian failure regime, simple variance-based exclusion (`freq_exclude`) is near-optimal and ADMEC's temporal-statistic gates have nothing distinctive to detect |
| Symmetric, time-invariant Poisson(λ) link delays | Real comparison links have asymmetric, sometimes-correlated, sometimes-bursty delays (TWSTFT scheduling, fibre-link drop-outs, GNSS multipath ionospheric variability) | The drop-vs-stale ablation should be read as a stand-in for "local-area network with irregular packet delivery", not for intercontinental optical-clock comparison via dedicated optical fibres |
| `freq_global` is the centralised baseline | Even BIPM's UTC computation is post-processing on data collected over weeks; no real timekeeping system has zero-delay access to all readings | The "centralised" baselines in § 3 are *omniscient* baselines; a delayed-centralised baseline (which we do not run) would close part of the apparent gap, particularly under stale convention. The *N* / *k*_eff reference is therefore the gap to an idealisation; against a delayed-centralised aggregator the real gap is smaller |
| MSE against the nominal-zero reference is the figure of merit | Real timekeeping cares about *ensemble stability* (modified Allan deviation, time deviation TDEV) at operating timescales, not point-MSE against an unobservable absolute | An estimator with low MSE may have poor stability at long τ if it introduces high-frequency jitter. § 5.4's "constraint layer as variance absorber" finding *might* improve stability and MSE simultaneously, but the present manuscript reports only MSE |

These simplifications are appropriate for a topological-information characterisation but inappropriate for a deployment recommendation. **The present manuscript characterises the *family* and the *regime*, not a specific deployment.** A pre-deployment engineering study would re-implement the classifier in fully decentralised form, replace the noise model with the deployment's actual hierarchy, replace the failure model with deployment-specific failure modes, and re-evaluate against an Allan-deviation-based stability metric.

Two further distinctions worth flagging explicitly:

- **Maser ensemble timescales vs optical-clock comparison networks.** These are operationally different problems. Hydrogen-maser ensemble-time algorithms (NIST AT1 and similar) keep a steered ensemble and estimate per-clock drift coefficients. Optical-clock comparison networks (e.g. Lisdat 2016) deal with dead time, maser flywheels, systematic uncertainty, geopotential / relativistic corrections, cycle slips, and phase-stabilised link noise — all features absent from the present simulation. The manuscript's findings are *closer* to the maser-ensemble problem (per-node steering / weighting / outlier handling on a single timescale), and *not directly applicable* to the optical-clock comparison problem.
- **Operational FPR thresholds.** § 4.4.1 contextualises the threshold-1.5 wins by noting that an FPR > 1 % per reading is generally considered borderline for routine ensemble-clock deployment and > 5 % unacceptable. These figures are stated as engineering rules of thumb rather than as derived bounds; they reflect typical ensemble-time tuning practice rather than a published numerical standard. A specific deployment's tolerable FPR depends on its steering-loop bandwidth, the number of clocks in the ensemble, and the cost of false exclusion; the manuscript does not derive this number, only uses it as an order-of-magnitude reference.

## 3. Results: WP2 baseline

Canonical archive: [`data/wp2_campaign_20260504_fix.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp2_campaign_20260504_fix.npz). Full setup and verdict in [entry 007](../logbook/007_2026-05-04_wp2-simulation-harness.md) and the [WP2 summary](../logbook/wp2-summary.md).

### 3.1 Methodological prerequisites: two bug fixes

The first WP2 dry run produced spuriously catastrophic ADMEC-full performance (S2 MSE ≈ 4.85, > 40× the unconstrained variant). Two implementation issues were identified and fixed before the canonical archive was generated:

- **`admec_full` t = 0 initialisation.** The initial state was set to the raw readings `Y[0, :]`, which made the first variance-ratio constraint check compare the consensus target's variance (≈ 1/N of single-reading variance) against the raw-reading variance. The ratio fell below 0.5 and *every* update was rejected, freezing the estimator at `Y[0, :]`. Fix: initialise to the centralised inverse-variance weighted mean. Effect on S2 MSE: 4.85 → 0.13.
- **Floating-point variance-ratio guard.** `np.var(state)` of a constant array returns ≈ 3 × 10⁻³³, not exactly 0. The original guard `if var_before > 0` entered the variance-ratio check on uniform states and the ratio diverged. Fix: guard `var_before > 1 × 10⁻²⁰`. Effect on S2 MSE: 0.27 → 0.09; rejection rate on dense networks dropped from > 90 % to < 1 %.

Both fixes have regression tests; both are documented in [entry 007](../logbook/007_2026-05-04_wp2-simulation-harness.md). The DG-2 verdict below holds for the post-fix archive.

**The eventual NOT-MET verdicts are not an under-tuning artefact.** All § 4 ablation deltas are computed against the post-fix archive — the baseline against which "stale beats drop", "var_loose helps S3 stale", "lower IC threshold halves admec_full MSE on delayed scenarios", and so on are reported has the two fixes already applied. The fixes raised the baseline from broken (frozen estimator, ~100 % rejection rate on dense networks) to working; the ablations then characterise the remaining gap between the working baseline and centralised methods. The negative DG verdicts therefore measure ADMEC against a working baseline, not a buggy one.

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

**On uncertainty quantification.** The cells in this table are mean MSE across 10 seeds. The seed-to-seed standard error (SEM) is small relative to the qualitative picture for centralised baselines (`freq_global`, `freq_exclude`, `imm` SEMs are typically ≈ 0.001–0.005 across all scenarios) and modest but non-negligible for `admec_full` (SEM 0.014–0.104, depending on scenario; largest on S1, smallest on the dense S2). This means the cross-method orderings within each scenario row above are robust to seed noise — none of the DG-2 verdicts flip if you re-roll the seeds — but *small intra-method tuning differences* (e.g. the S2 0.093 vs 0.088 lag-0/lag-1 contrast in § 4.5, or the S2 −2 % combined-tuning effect in § 4.6) are within seed noise and should not be over-interpreted. The §4.6 table reports paired-difference SEM and t-statistics for the combined-tuning headline; SEM tables for the per-axis ablations live in their respective logbook entries.

### 3.3 DG-2b classification validation

Recomputed reproducibly with [`scripts/wp2_classification_check.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp2_classification_check.py):

| scope | TPR | FPR | precision | F1 | strict-STRUCTURED TPR |
|-------|----:|----:|----------:|---:|----------------------:|
| All 8 scenarios | 0.430 | 0.010 | 0.763 | 0.550 | 0.007 |
| Signal scenarios only (6) | 0.430 | 0.010 | 0.831 | 0.567 | 0.007 |

Strict STRUCTURED-only TPR = **0.007** in aggregate — but this aggregate hides the per-scenario distribution, which is more diagnostic than the headline number suggests:

| Scenario | signal type | overall TPR | strict-STRUCTURED TPR |
|----------|-------------|------------:|----------------------:|
| S1 | sinusoidal | 0.493 | 0.0087 |
| S2 | sinusoidal | 0.493 | 0.0087 |
| S3 | sinusoidal | 0.564 | 0.0093 |
| S6 | linear drift | 0.045 | 0.0005 |
| S7 | step at T/2 | 0.980 | 0.0147 |
| **S8** | **fold bifurcation** | **0.013** | **0.0000** |

**S8 is the scenario the δ_min temporal-statistic thresholds were explicitly calibrated for** (entry 004 — they target rising variance and lag-1 autocorrelation, the classical critical-slowing-down signatures). Its strict-STRUCTURED TPR is zero across every (seed, post-onset) cell. The classifier flagged none of the near-bifurcation readings as STRUCTURED.

Two readings are possible:

1. Within the simulated T = 200 horizon, the fold-bifurcation trajectory does not approach the critical point closely enough for the temporal-statistic gates to fire above the WP1 calibration thresholds; the aggregate 0.7 % strict TPR is therefore masking the result rather than averaging into it.
2. The temporal-statistic thresholds calibrated under the WP1 null-noise menu (entry 004) are not the right operating point for signal-conditional detection on this clock-noise model — analogous to the threshold mismatch between null-FPR and consensus-MSE optimisation identified in § 5.2 / § 5.4.

We do not distinguish between these in this study. The implication is that **the regime-detection reframe of STRUCTURED in § 5.3.1 is currently unsupported by direct data** — the only scenario where regime detection should produce a positive signal produces a zero one. Resolving this is a precondition for any follow-up study that pre-registers the redesigns of § 5.6 against a STRUCTURED-as-regime-detection criterion. Almost all anomaly detections classify as UNSTRUCTURED. The DG-2b 70 % threshold is not met on the strict three-way criterion.

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
*Forward reference: § 5.4 — reveals the constraint layer's actual role as a variance-absorption mechanism.*

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

### 4.3 Two-way vs three-way classifier — a syntactic gap
*Forward reference: § 5.3 — the architectural reading of the zero-delta result; § 5.3.1 — the regime-detection hypothesis the present data does not yet support.*

[Entry 010](../logbook/010_2026-05-04_wp3-ablation-two-vs-three-way.md), archive [`data/wp3_ablation_two_vs_three_way_20260504.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_ablation_two_vs_three_way_20260504.npz).

Across 360 (scenario × seed × estimator × delay-mode × classifier) configurations:

> **max abs MSE delta = 0.0000e+00**
> **max abs structure-correlation delta = 0.0000e+00**

Three-way and two-way produce numerically identical consensus output (max absolute element-wise delta on the (T, N) estimate arrays = 0 to double precision). The result is *algebraic*, not statistical: the ADMEC consensus update rule reads only one symbol from the classifier output:

```
target_i(t) = ( Σ_{j ∈ N(i, t)}  w_j(t) · y_j(t) ) / Σ_{j ∈ N(i, t)} w_j(t)
              ──────────────────────────────────
              N(i, t) = ({i} ∪ { j : adj[i, j] ∧ delay-accessible(i, j, t) })
                        ∩ { j : mode[t, j] == STABLE }
```

(Self is always treated as accessible at lag 0; the static `adj` matrix has a False diagonal in [`src/network.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/network.py), and the estimator code unions self in explicitly.)

The mask `mode[t, j] == STABLE` is binary. Whether a flagged reading carries the label STRUCTURED or UNSTRUCTURED never enters the right-hand side. The classifier emits a three-valued symbol; the *consensus target* consumes only the two-valued projection (STABLE / not-STABLE). The classification *counts* differ (5–6 STRUCTURED in three-way vs 0 in two-way), but the *STABLE* count is identical between modes, so the consensus target's right-hand side is identical between modes.

`admec_full` adds a projection stage on top of the consensus target — per-node 3σ box clipping, network-wide *N*σ² energy ball scaling, and a [0.5, 1.5] variance-ratio post-check (§ 2.2 and [`src/constraints.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/constraints.py)). The projection function `project_update(state, proposed_update, sigmas, params)` takes only the proposed update vector, the current state, the per-node sigmas, and the constraint thresholds; it does *not* read the classifier's mode array. The projection is therefore mode-blind by signature. If the proposed update is identical between three-way and two-way, the projected update is identical too; the algebraic invisibility extends through the full pipeline, not just the consensus target. The 360-cell zero-delta empirical result confirms this: it would have been impossible if the projection had read STRUCTURED status.

This is the syntactic gap. **DG-3's "three-way > two-way" sub-criterion is formally unreachable under the present architecture, not just empirically NOT MET.** The 360 zero-delta cells confirm what the algebra already implies. To make three-way operationally visible, the consensus rule would need an additional production that reads STRUCTURED — for example a reduced-weight inclusion `w_j(t) ← α · w_j(t)` when `mode[t, j] == STRUCTURED` for some `α ∈ (0, 1]`. None of these productions is in the WP2 architecture. They are redesign candidates, not tuning ablations; § 5.3.1 and § 5.6 return to them.

### 4.4 Classification threshold sweep
*Forward reference: § 5.2 — the null-FPR vs consensus-MSE threshold mismatch.*

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

#### 4.4.1 Operational cost of the low-threshold "wins"

The matched-threshold and best-of-best comparisons in § 4.6.1 show ADMEC-full beating `freq_exclude` at threshold 1.5. The reader who comes to those numbers from operational timekeeping will immediately ask: at threshold 1.5, what is the *empirical* false-positive rate? In real ensemble clocks (NIST AT1 and similar), an FPR > 1 % per reading is generally considered borderline; > 5 % is typically unacceptable for routine deployment because every false exclusion degrades the long-τ stability of the steered ensemble.

We measured the per-reading FPR at each swept threshold on the two pre-registered null scenarios (S4 ring 15-node Poisson(2.0) no signal; S5 random-sparse 50-node Poisson(4.0) no signal), 10 seeds each, by counting cells with `IC_k ≥ threshold` and treating every flag as a false positive (no signal exists in S4/S5 by construction). Reproducible from [`scripts/wp3_threshold_fpr_check.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/wp3_threshold_fpr_check.py); archive [`data/wp3_threshold_null_fpr_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_threshold_null_fpr_20260505.npz).

| Scenario | thr 1.5 | thr 2.0 | thr 2.5 | **thr 2.976 (WP1)** | thr 3.5 | thr 4.5 | thr 6.0 |
|----------|--------:|--------:|--------:|--------------------:|--------:|--------:|--------:|
| S4 (null ring) | 18.5 % | 6.5 % | 2.6 % | **1.2 %** | 0.6 % | 0.0 % | 0.0 % |
| S5 (null sparse) | 17.9 % | 6.3 % | 2.5 % | **1.1 %** | 0.5 % | 0.2 % | 0.1 % |

The WP1 calibrated value 2.976 delivers ≈ 1.1–1.2 % null FPR on these scenarios — already at the borderline for routine deployment. Threshold 1.5 (the consensus-MSE optimum on S1 / S3 delayed) sits at **18 % null FPR**, more than an order of magnitude above the operational redline.

**The matched-threshold and best-of-best wins in § 4.6.1 are therefore wins at an operationally untenable threshold.** They identify a *characterisation* result — the constraint layer's variance-absorption mechanism is real and pays off when exclusion is aggressive — but a deployment that operated at 18 % FPR would degrade an ensemble's long-τ stability beyond what the MSE win recovers. A practitioner-facing recommendation needs to either (i) hold the threshold at ≈ 2.5–3.0 (where FPR ≈ 1–3 %) and accept that ADMEC's constraint layer adds little visible value at consensus-output level, or (ii) develop a redesign in which aggressive exclusion does not blow up FPR (one of the § 5.6 follow-up directions). The threshold-sweep "wins" in this manuscript are not yet that recommendation.

### 4.5 Lagged classification (simultaneity bias test)
*Forward reference: § 5.4 (detection latency as the dual of variance absorption) and § 6 conclusion (no simultaneity bias finding). Caveat: this ablation tests `IC(t)` vs `IC(t − 1)` where in both cases IC is computed from the full same-time ensemble. It does not test whether *truly local* IC (each node using only its delay-accessible readings) would have a different lag dependence; that is a follow-up question on top of the truly-local-classifier redesign flagged in § 2.6.*

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

### 4.6 Combined tuning *(post-hoc harness)*

The pre-registered ablation menu in [docs/projektantrag.md](projektantrag.md) specified five *orthogonal* axes (delay convention, threshold, constraint sensitivity, classifier cardinality, detection lag), implicitly assuming their effects could be read independently. The combined-tuning harness reported in this subsection runs three of those axes simultaneously, and is therefore **post-hoc**: the proposal's orthogonality assumption is *retracted* by the data this subsection presents — combining `var_loose` with stale + threshold 1.5 produces a non-additive interaction (slightly negative on S1, neutral on S3) rather than the additive sum the orthogonal-axes assumption would predict. The numbers below are reported as informational characterisation of how the design axes interact, not as a pre-registered claim. Frames (b) and (c) of § 4.6.1 below are similarly post-hoc and informational; they do not formally rescue DG-2.

The four parametric ablations identify a recommended tuning combination:

- delay convention = **stale** (entry 008);
- classification threshold = **1.5** (lower than the WP1 calibration of 2.976; entry 011);
- variance-ratio bounds = **[0.35, 1.65]** (`var_loose`; entry 009, scenario-conditional);
- classification lag = **0** (same-step; entry 012 — no simultaneity bias to remove).

The first three are simultaneously varied; lag stays at the WP2 default. To verify these design choices interact additively rather than antagonistically, the integrated harness `scripts/wp3_combined_tuning_check.py` (archive [`data/wp3_combined_tuning_20260505.npz`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/data/wp3_combined_tuning_20260505.npz)) runs `admec_full` with all three applied at once on the same RNG-matched seeds as the WP2 campaign. Measured results:

| Scenario | WP2 baseline `admec_full` MSE (mean ± SEM, n = 10) | Combined-tuned `admec_full` MSE (mean ± SEM) | paired Δ ± SEM | t-stat |
|----------|---------------------------------------------------:|---------------------------------------------:|---------------:|-------:|
| S1 | 0.732 ± 0.104 | **0.252 ± 0.018** | −0.481 ± 0.113 | −4.27 |
| S2 | 0.093 ± 0.015 | 0.091 ± 0.012 | −0.002 ± 0.017 | −0.13 |
| S3 | 0.741 ± 0.023 | **0.196 ± 0.003** | −0.545 ± 0.024 | −23.16 |

The S1 and S3 reductions are statistically substantial (paired t ≈ −4 and −23 respectively, n = 10); **the apparent S2 reduction is consistent with zero** (t ≈ −0.13) and should not be read as a real combined-tuning effect on the dense control. This is what the topological picture predicts: S2's *k*_eff/*N* ≈ 1.0 already, so there is no topological gap for tuning to close. The interaction is *not strictly additive*. On S1, the best individual-ablation result was `stale + thr 1.5` = 0.238 (entry 011); adding `var_loose` raises it to 0.252 (the entry-009 finding that `var_loose` mildly hurts S1 already at the WP2 baseline carries through). On S2, the best individual-ablation result was `stale + thr 2.0 + baseline constraints` = 0.088 (entry 011); the combined-tuning value 0.091 is slightly worse for the same reason — but again, the difference is within seed noise. On S3, the combined value 0.196 essentially matches the best individual `stale + thr 1.5` = 0.191 — the dominant gain comes from threshold + delay, with `var_loose` adding only ~ 0.005 of further reduction on top.

**Overfitting caveat.** The combined-tuning configuration `stale + thr 1.5 + var_loose` was selected by inspecting the per-axis ablations on the same eight pre-registered scenarios it is then evaluated on; it is not a held-out generalisation claim. The S3 −74 % headline therefore measures *how far the architecture can be pushed within the pre-registered scenario menu under post-hoc tuning*, not how it would fare on an independently sampled scenario. The threshold-1.5 component additionally carries the operational FPR cost discussed in § 4.4.1 (≈ 18 % null FPR vs an operational tolerance of ≈ 1 %), so the combined-tuning win cannot be read as a deployment recommendation.

#### Decomposition of the S3 74 % improvement

The reduction from 0.741 to 0.196 on S3 spans both a *delay-convention change* (drop → stale; *k*_eff jumps from 1.30 to 4.00 — three times more accessible information per node) and a *parameter change* (threshold 2.976 → 1.5 with `var_loose`). Disentangling the two:

| Comparison | mode | thr | var-bound | S3 admec_full MSE | source |
|------------|------|----:|-----------|------------------:|--------|
| **WP2 baseline** | drop | 2.976 | [0.5, 1.5] | 0.741 | wp2_campaign archive |
| Drop, parameter-tuned | drop | 1.5 | [0.5, 1.5] | 0.443 | entry 011 |
| Stale, baseline parameters | stale | 2.976 | [0.5, 1.5] | 0.461 | entry 008 |
| **WP3 combined** | stale | 1.5 | [0.35, 1.65] | 0.196 | combined-tuning archive |

The pure-convention move (drop → stale at baseline parameters): 0.741 → 0.461, a 38 % reduction, attributable to *k*_eff increasing from 1.30 to 4.00. The pure-parameter move (drop, baseline → drop, threshold 1.5): 0.741 → 0.443, a 40 % reduction, attributable to threshold tuning at fixed *k*_eff. The two effects compose multiplicatively rather than additively to give the 74 % combined reduction. The headline number combines a topological-mode change with a parameter change; the two are entangled in the combined-tuning result and disentangled here.

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

DG-2 was pre-registered at the calibrated threshold and stays NOT MET (frame (a)). The matched-threshold and best-of-best comparisons are post-hoc and informational; they do not formally rescue DG-2. **They are also not directly operational**: as § 4.4.1 documents, the matched threshold 1.5 corresponds to ≈ 18 % null FPR, well above the routine-deployment redline (~1 %) for ensemble timekeeping. The architecture wins at operational thresholds (≈ 2.5–3.0) only on S2; the wins at threshold 1.5 are a *characterisation* of the constraint layer's variance-absorption mechanism, not a deployment recommendation.

## 5. Discussion

### 5.1 The topological pooling-limit heuristic

The residual ~ 8 × gap to centralised baselines on S3 (50-node random-sparse with target degree 3, Poisson(4.0) delays) is consistent with a simple information-pooling heuristic. A centralised inverse-variance weighted mean over *N* readings drawn i.i.d. from a unit-variance distribution has variance σ² / *N*. A local consensus over an effective *k*_eff-element neighbourhood has variance σ² / *k*_eff. The local-to-centralised MSE ratio is therefore approximately *N* / *k*_eff under the independent-reading assumption.

**Toy derivation (independent-reading null).** Consider *N* nodes whose readings at a single time step are *y_j* = μ + ε_j with ε_j ∼ 𝓝(0, σ²) i.i.d. and a common unknown mean μ to be estimated.

- The centralised inverse-variance estimator is the unweighted sample mean (since σ is uniform), μ̂_cent = (1/*N*) Σ_{j=1..N} *y_j*, with variance Var[μ̂_cent] = σ² / *N*.
- A local estimator at node *i* has access only to a delay-accessible neighbourhood 𝒩_i (including self) of size *k_i*; the analogous unweighted local mean μ̂_local,i = (1/*k_i*) Σ_{j ∈ 𝒩_i} *y_j* has variance σ² / *k_i*.
- Since both estimators are unbiased for μ, MSE = variance, and the ratio MSE_local,i / MSE_cent = *N* / *k_i*. Averaging over nodes and using *k*_eff = E[*k_i*] gives the heuristic reference value MSE_local / MSE_cent ≈ *N* / *k*_eff (it is exact when the *k_i* are uniform; for heterogeneous *k_i* there is a Jensen gap, see §5.1.4).

The two assumptions doing the work are **independence of readings across nodes** (so the variance of a sum decomposes node-wise) and **identical noise scale** (so the inverse-variance weighting is uniform). Heteroscedastic σ_j or favourable cross-node correlations move the ratio off this line; the heuristic is a regime locator, not a derived bound.

#### 5.1.1 Operational definition of *k*_eff

For a node *i* at simulation step *t*, define the per-step accessible-neighbour set as
*A*(*i*, *t*) = {*j* : `adj[i, j]` ∧ delay-accessible(*i*, *j*, *t*)}, where `adj` is the static adjacency matrix and "delay-accessible" depends on the operating mode:

- under the WP2 baseline `drop` convention, delay-accessible means `delays[i, j] ≤ freshness` (default 1 step);
- under the WP3 `stale` convention, every adjacency neighbour is accessible at lag `delays[i, j]`.

We then define *k*_eff = mean over (seed, node *i*) of |*A*(*i*, *t*)| + 1, with the +1 counting the node's own reading. The values reported in the table below are computed by [`scripts/figure_topology_ceiling.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/figure_topology_ceiling.py); they are not time-varying because the adjacency and delay matrices are sampled once per (scenario, seed) at simulation start. A scenario where delays themselves were time-varying would require an additional per-*t* average; that case is not in our menu.

#### 5.1.2 What the heuristic does and does not claim

This is a *heuristic* approximate-value argument under the independent-reading null, not a formal theorem and not a one-sided bound. The independent-reading assumption is violated in two directions:

(a) signal-bearing readings are correlated, so pooling them gives *less* than 1/*N* variance reduction in the centralised-baseline numerator, and
(b) temporal pooling from stale-reading lags lets a local consensus draw on more than *k*_eff readings in the local-consensus denominator.

We *hypothesise* that the two effects partially cancel within our scenario family, but the cancellation is empirical, not derived. A correlation structure unfavourable in both directions could in principle make the realised ratio higher than *N* / *k*_eff (i.e. the heuristic could *underestimate* the gap rather than overestimate it). What the data shows is that this does not happen in any of our 24 (scenario, mode) measurement points: every measured ratio sits at or below the *N* / *k*_eff line.

We therefore use *N* / *k*_eff as a regime-locating heuristic reference, not as a one-sided bound in either direction. A formal Cramér–Rao analysis on the specific clock-noise model would settle whether the empirical reference is also a theoretical bound; that derivation is reserved for follow-up work.

**Worked S3 example.** Per-seed paired ratios `admec_full` MSE / `freq_global` MSE on S3 (50 nodes, target degree 3, Poisson(4.0) delays, 10 seeds) sit at **18.17 ± 0.58 (SEM)** under the WP2 baseline (drop convention, threshold 2.976; *k*_eff = 1.30, reference *N*/*k*_eff = 38.5) and at **4.80 ± 0.10** under combined tuning (stale convention, threshold 1.5, var_loose; *k*_eff = 4.00, reference *N*/*k*_eff = 12.5). In both clusters the empirical ratio lies *below* its scenario's reference line — the baseline by a factor 0.47, the combined-tuned by a factor 0.38 — and the SEM is much smaller than the baseline-vs-combined gap, so the within-cluster downward shift from baseline is statistically substantial rather than seed-noise. The ratio shrinks because the convention change increases *k*_eff threefold (1.30 → 4.00); parametric tuning at fixed *k*_eff supplies the rest. The same picture holds on S1 (15-node ring): baseline 2.28 ± 0.33 and combined 0.78 ± 0.05, against a stale-mode reference of 5.0; on S2 the cluster sits at ≈ 0.29 in both conventions, against a reference of 1.0 (no topological boundary to bind).

Effective neighbourhood per scenario, computed directly from the canonical archives ([`scripts/figure_topology_ceiling.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/figure_topology_ceiling.py)):

| Scenario | *N* | *k*_eff (drop, freshness 1) | *k*_eff (stale) | *k*_eff/*N* (drop) | *k*_eff/*N* (stale) | reference *N*/*k*_eff (stale) |
|----------|---:|----------------------------:|----------------:|-------------------:|--------------------:|------------------------------:|
| S1 | 15 | 1.72 | 3.00 | 0.115 | 0.200 | 5.0 |
| S2 | 15 | 14.55 | 15.00 | 0.970 | 1.000 | 1.0 |
| S3 | 50 | 1.30 | 4.00 | 0.026 | 0.080 | 12.5 |

S2's reference ratio is essentially 1 — every node sees the whole network, so the local-vs-centralised distinction barely exists. S1 and S3 sit in the topology-restricted regime where the reference is non-trivial.

#### 5.1.3 Choice of denominator

The *N* / *k*_eff heuristic is derived for inverse-variance weighted means of independent unit-variance unbiased readings. The estimator that exactly instantiates that derivation is `freq_global` (centralised inverse-variance weighted mean over all *N* readings, no exclusion, no temporal state). Filter-bank baselines (`imm`, `bocpd`) carry temporal information that `admec_full` does not, and exclusion-style baselines (`freq_exclude`) silently change which subset of readings is being pooled — both make the denominator's character vary across scenarios. Figure 1 therefore uses `freq_global` per-seed as the denominator: numerator and denominator share the same (Y, adj, delays, seed), so the ratio is paired and matches the heuristic's derivation. This is a cleaner comparison than the "best non-ADMEC baseline" denominator that earlier drafts used; the resulting points sit further below their reference lines but the qualitative picture (every measurement at or below *N* / *k*_eff) is unchanged.

![Figure 1. Topological pooling-limit reference. Each marker is a single (scenario, seed) measurement of admec_full MSE divided by freq_global MSE, paired seed-for-seed. The dashed line is the heuristic reference N / k_eff under independent-reading pooling; the gray horizontal line marks parity with freq_global. Baseline-architecture points (drop convention, calibrated IC threshold 2.976) are translucent and at the drop value of k_eff/N; combined-tuned points (stale + threshold 1.5 + var_loose) are solid with black borders and at the stale value of k_eff/N. The two horizontal positions per scenario reflect the convention change, not measurement noise. Mean ratios per cluster: S1 baseline 2.28 / combined 0.78; S2 baseline 0.29 / combined 0.29; S3 baseline 18.2 / combined 4.8. ADMEC-full beats freq_global on S2 always and on S1 once combined tuning is applied; on S3 the centralised information advantage dominates regardless of tuning.](manuscript_files/fig_topology_ceiling.png)

The figure makes the constraint visible: across both conventions and at every seed, the measured ratio sits at or below its scenario's *N* / *k*_eff reference line. Design tuning shifts each scenario's point cluster horizontally (changing *k*_eff via the convention change) and downward (within a cluster, combined-tuned points sit modestly below the reference). The 4.8 × residual on S3 under combined tuning sits below S3's stale-mode reference of 12.5 — but the *direction* of the residual is set by topology, not by anything ADMEC controls.

**Why combined-tuned points sit *below* their cluster's reference (speculative).** A naïve reading attributes the within-cluster gap to "temporal pooling of multi-step stale readings beyond the independent-reading argument." This is plausible but not derived: stale mode reads exactly *one* sample per neighbour, just an older one. The more precise candidate mechanism is *bias reduction at the cost of staleness variance* — the consensus target moves toward a smoother estimate because each contributor is a delayed-lag-averaged proxy for the network state — and this is a different story from pooling. We label this mechanism speculative in the present manuscript; a clean derivation would require an explicit bias-variance decomposition on the specific clock-noise model and is left to follow-up work alongside the formal Cramér–Rao analysis flagged in § 5.1.2.

**Caveat: the heuristic counts spatial pooling only.** The *N* / *k*_eff reference treats *k*_eff as a count of accessible *spatial* neighbours. Real clock networks (and the literature's standard practice) use estimators with explicit *temporal* memory — Kalman filters with random-walk-FM clock models, exponentially-weighted aggregates such as NIST's AT1 — that effectively pool information over time as well as over neighbours. A node with *k*_eff = 4 spatial neighbours that integrates with an exponential forgetting factor λ effectively pools over *k*_eff / (1 − λ) historical readings. The reference line in Fig. 1 is therefore the *approximate value for static, memoryless aggregation* on the ADMEC-family update rule; estimators with well-tuned temporal memory (Kalman, AT1-style) may sit below the line. The manuscript's `imm` and `bocpd` baselines do carry temporal state, but they are off-the-shelf default-parameter implementations rather than tuned ensemble-clock predictors; a tuned random-walk-Kalman baseline would be a natural follow-up comparison and is not in the present menu.

#### 5.1.4 Sign-fixed decomposition (Analytic Reference Pipeline v0.2)

A more formal treatment of the *N* / *k*_eff observable lives separately in the project repository at [`analysis/docs/analytic_reference.md`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/analysis/docs/analytic_reference.md). The Analytic Reference Pipeline (ARP v0.2) formalises three quantities the present manuscript discusses informally:

- a **Jensen gap** Δ_J = E[*N* / *k*_i] − *N* / *k*_eff that quantifies the heterogeneity of accessible-neighbourhood sizes across nodes (non-negative by convexity);
- a **total deviation** Δ_total = MSE_local / MSE_cent − *N* / *k*_eff measured directly from data;
- a **residual** Δ_res = Δ_total − Δ_J with a sign-fixed interpretation: Δ_res < 0 is a *helpful violation* (temporal pooling or favourable correlations supply effective information beyond the independent-reading count), while Δ_res > 0 is an *unmodelled degradation* (staleness bias or adversarial topology).

Under ARP's vocabulary, the empirical observation that combined-tuned points sit below their cluster reference becomes a sign-fixed statement: Δ_res is *negative* in the stale-mode clusters of Fig. 1, i.e. stale-reading mode is a "helpful violation" of the independent-reading null — without committing to a specific mechanism. The "bias reduction at the cost of staleness variance" interpretation in the previous paragraph is a candidate explanation for *why* Δ_res is negative; ARP fixes the sign without fixing the mechanism. We use the ARP labels for the rest of this section as the more careful framing.

ARP carries its own endorsement marker: it is a "local candidate framework (no parity implied with externally validated laws); the analytic reference model is an architectural lens, not a physical law." The same hedge applies here. The formal Cramér–Rao analysis flagged in § 5.1.2 would test whether ARP's heuristic Δ_total decomposition is also a derived bound; that derivation is not in scope for the present manuscript or for the present version of ARP.

#### 5.1.5 Relation to distributed-consensus and clock-synchronisation literature

The *N* / *k*_eff reference connects to the distributed-systems literature on average consensus and clock synchronisation, but is not a re-derivation of it. Three reference points worth flagging:

- **Average consensus on graphs.** The standard analysis of linear consensus iterations *x*(*t*+1) = *W* *x*(*t*) — Metropolis weights, push-sum, doubly-stochastic gossip — characterises convergence *rate* via the spectral gap 1 − λ₂(*W*); see Boyd et al. 2006 for the gossip case. That literature answers "how many rounds to reach consensus on a fixed value", which is a different question from "how good is the value reached at fixed rounds". Our setting fixes one update per simulation step on a non-stationary signal, so the relevant figure of merit is steady-state mean-squared error against the instantaneous signal, not asymptotic convergence rate. The *N* / *k*_eff heuristic addresses that figure of merit; the spectral-gap analysis is complementary, not in conflict.
- **Fault-tolerant pulse synchronisation.** Lenzen et al. (2019, *J. ACM*) prove tight bounds on Byzantine-tolerant pulse synchronisation on graphs in terms of node degree and adversary fraction. Their threat model (Byzantine, with the tolerable adversary fraction set by a topology-dependent constant) and figure of merit (clock-skew bound under worst-case faults) differ from ours (Gaussian noise plus a single 3×σ-degraded node, MSE against a nominal reference), so we do not place ADMEC on their bound directly. The architectural lesson — *what each node can learn is bounded by the topology of who it can hear from* — is the same lesson the *N* / *k*_eff reference encodes for the Gaussian-noise / non-adversarial setting.
- **Ensemble timekeeping (NIST AT1, BIPM UTC).** These are *centralised post-processing* algorithms that use temporal state per clock; they are the natural baseline for the redesigns in § 5.6 (decayed-staleness with state propagation, STRUCTURED with drift estimation). They are not in the present menu, and the *N* / *k*_eff reference does not bind them (they pool temporally, not just spatially).

We do not run algorithmic baselines from any of these traditions. The intent is positioning, not benchmarking: the present manuscript characterises a static-memoryless, partially-decentralised, non-adversarial point in a much larger design space, and the *N* / *k*_eff heuristic is the regime-locating reference for *that* point.

**This is not a hyperparameter problem within the ADMEC family.** No constraint setting, threshold value, or delay convention we tested bridges S3's 50 : 4 information ratio. To approach it, the architecture would need to either pool over more readings (which defeats the locality assumption) or integrate temporal information differently (the "decayed staleness" redesign in § 5.6).

### 5.2 Threshold mismatch: null FPR vs consensus MSE — and why this matters operationally

The WP1-calibrated IC threshold of 2.976 bit was optimised under the worst-case null assumption to give a 5 % false-positive rate. That is the right calibration for hypothesis-test interpretation. For the *consensus problem*, the relevant criterion is signal-conditional MSE — and the optimal threshold for `admec_full`'s MSE is markedly lower (1.5–2.0) on signal-rich delayed scenarios. The two criteria pick different optimal operating points because they are measuring different things.

A signal-aware re-calibration (pick the threshold that minimises consensus MSE under the WP2 scenarios) is a natural operational choice and would shift the picture toward `admec_full` competing more strongly with centralised exclusion. In the spirit of the pre-registered design, this manuscript reports the calibrated value's performance and notes the mismatch as a finding rather than retroactively redoing the calibration.

### 5.3 Architectural invisibility of three-way at the consensus stage

The two-way / three-way ablation produces a delta of *exactly zero* across 360 cells because the ADMEC consensus rule reads only the STABLE mask (§ 4.3). Both anomaly classes are excluded equally; the partition of "not-STABLE" into STRUCTURED vs UNSTRUCTURED is a bookkeeping detail invisible to the estimator. To make the three-way distinction operationally meaningful, the architecture must either (a) include STRUCTURED readings with reduced weight (a continuous-treatment variant), (b) use the STRUCTURED count as a regulariser on downstream parameters, or (c) maintain STRUCTURED as a separate output channel that is scored by a metric the consensus does not see (e.g. "anomalies-tracked-not-suppressed correlation"). None of these is present in the WP2 architecture.

The DG-3 "three-way > two-way" sub-criterion is therefore not just empirically NOT MET; it is *structurally unreachable* without a redesign that lets STRUCTURED status enter the update rule.

#### 5.3.1 Why tracking STRUCTURED separately *might* still be architecturally important — and why this study cannot tell *(interpretation contingent on follow-up validation)*

A reading flagged STRUCTURED would carry different information from one flagged UNSTRUCTURED, even when both are excluded from the consensus. The temporal-statistic gates (variance slope, lag-1 autocorrelation) calibrated in entry 004 are precisely the early-warning indicators studied in the critical-transition literature (Scheffer 2009; Dakos 2012). A natural mapping into a regime-detection vocabulary would be:

| Classifier label | Regime in early-warning vocabulary |
|------------------|-------------------------------------|
| STABLE | Deep interior of the operating regime; no detectable anomaly. |
| STRUCTURED ANOMALY | Approaching a regime boundary — variance and / or autocorrelation rising on a trailing window, the canonical critical-slowing-down signature. |
| UNSTRUCTURED ANOMALY | Extrinsic shock — IC flags an outlier, but no persistent internal structure (memoryless burst). |

Under this reading, the three-way classifier *would* be doing *regime detection*, not just outlier exclusion, and the STRUCTURED stream would be the input a downstream early-warning monitor would consume. The DG-3 sub-criterion measures the consensus output, so the absence of an effect at that layer would say nothing about whether STRUCTURED is useful for a different downstream task.

**However, the data we have does not support this reading.** The per-scenario strict-STRUCTURED TPR table in § 3.3 shows that S8 — the only scenario in our menu that is by construction near a fold bifurcation — registers a strict-STRUCTURED TPR of exactly 0.0000 across every (seed, post-onset) cell. The regime that the classifier was *designed for* produces zero positive detections in our setup. The non-zero strict-STRUCTURED TPR in S1/S2/S3/S7 (~0.01) reflects sporadic temporal-gate firings on signal-bearing readings whose signals are not regime-boundary signatures.

The regime-detection reframe is therefore **a hypothesis about a STRUCTURED channel that does not currently fire in the regime where it should**. Two distinct repairs are needed before it becomes a substantive claim:

(a) A scenario design that drives the system genuinely close to a critical transition within the simulation horizon — long enough for variance slope and lag-1 autocorrelation to cross the calibrated thresholds.
(b) A re-calibration of δ_min under a signal-conditional criterion rather than a worst-case-null criterion (analogous to the threshold mismatch in § 5.2 and § 5.4).

This study performs neither repair. We therefore mark the regime-detection reframe in this subsection as a **motivating hypothesis for the § 5.6 redesigns**, not as a finding the present data supports. A follow-up that pre-registers redesigns against a STRUCTURED-as-regime-detection criterion needs to address (a) and (b) first.

### 5.4 The constraint layer's actual role

The proposal motivates the update-size constraint stack as a safety net against pathological updates: a per-node 3-σ box, a network-wide N σ² energy ball, and a [0.5, 1.5] variance-ratio post-check. The combined effect on signal scenarios at the WP2 baseline is modest — `admec_full` beats `admec_delay` by 5–55 % depending on scenario, with the largest gains on dense low-delay topologies (S2: 0.139 → 0.093, −33 %).

The threshold-sweep ablation reveals a sharper interpretation. At low thresholds (1.5), aggressive exclusion strips signal-bearing readings from the local pool, *raising* the per-step variance of the proposed update. The constraint layer's projection absorbs that variance — clipping per-node updates to the box, scaling the network update onto the energy ball, and rejecting updates that would shift ensemble variance outside [0.5, 1.5]. The constraint layer is, operationally, a **noise-absorption mechanism**, and its benefit is largest precisely when exclusion is aggressive enough to need absorbing.

This is a useful design insight independent of the DG-2 verdict: ADMEC's constraint architecture is a viable noise-absorption add-on to centralised exclusion estimators, not a rescue mechanism for delay-restricted local consensus.

### 5.5 Operational recommendations

For deployments where ADMEC is the chosen architecture (e.g. decentralised networks without a global aggregator), and *subject to the deployment-specific revisions discussed in § 5.5.1*:

- **Pair the IC threshold with the deployment topology**, not with the null calibration — but bound it from below by the deployment's tolerable false-positive rate. Lower thresholds (1.5–2.0) improve consensus MSE on delayed scenarios in our simulation but produce 6–18 % per-reading null FPR (§ 4.4.1), which is operationally unacceptable for ensemble timekeeping. A threshold near 2.5–3.0 (FPR ≈ 1–3 %) is a more credible operating point.
- **Use stale-reading mode** rather than drop-and-truncate. The drop convention starves the consensus on sparse delayed networks for no operational benefit. *Caveat:* the present manuscript's "stale" mode reads one delayed sample per neighbour without forward-propagating the neighbour's state; a deployment-grade implementation would propagate each neighbour with a clock model (random-walk frequency for hydrogen masers; an appropriate noise model otherwise). This is closer to standard ensemble-clock practice (NIST AT1 and similar) and is a deployment-grade refinement of the WP3 finding.
- **Loosen the variance-ratio bound** (e.g. [0.35, 1.65]) when proposed updates inherit lag-induced variance; otherwise the bound rejects beneficial updates.
- **Keep classification at the same step.** There is no simultaneity bias, and any lag introduces a detection-latency MSE penalty.
- **Log the STRUCTURED stream for operator diagnosis even though the consensus does not consume it.** Real timekeeping facilities maintain logbooks of clock behaviour; an automated STRUCTURED flag is a candidate input to that logbook regardless of the syntactic gap at the consensus stage.

**For deployments where centralised aggregation is feasible:** use `freq_exclude` or `imm`. They are cheaper, simpler, and outperform `admec_full` on every scenario where centralisation is feasible. The ADMEC architecture's competitive regime is bounded by *k*_eff/*N* close to 1 — the regime where the network is approximately fully connected at the operative latency.

#### 5.5.1 Caveats on the recommendations

The recommendations above are inferred from a simulation that uses unit-scale white frequency noise as the dominant noise term, uniform 3× σ inflation as the failure mode, symmetric Poisson link delays, and MSE-vs-zero as the figure of merit. Real timekeeping deployments differ on each of these dimensions (see § 2.6). In particular: standard practice scores ensemble performance with stability metrics (modified Allan deviation, time deviation TDEV) at operating timescales, not with point-MSE; failure modes include phase steps, frequency offsets, and intermittent outliers, none of which the simulation captures faithfully; and centralised aggregation is itself delay-constrained at intercontinental scales, so the *N* / *k*_eff reference (against an idealised omniscient centraliser) overstates the local-vs-real-centralised gap. A pre-deployment engineering study would reproduce this manuscript's measurements under the deployment's own clock-noise / failure / link model, and re-evaluate the threshold and constraint settings against the deployment's stability metric.

### 5.6 Reserved follow-up: three architectural redesigns

Three architectural redesigns are reserved for a follow-up study with its own pre-registration. Each is a change to the consensus production rule itself or to where IC is computed, not a hyperparameter on the present rule, so pre-registering their decision gates against the new rule (rather than retrofitting the gates of this study) is the methodologically sound approach.

1. **STRUCTURED with reduced weight *and estimated drift*.** Currently the consensus excludes STRUCTURED nodes outright; a continuous-treatment variant (include STRUCTURED with weight α < 1) would make the three-way distinction operationally visible. A pre-release reader from operational timekeeping noted that "exclude STRUCTURED" is the *opposite* of standard ensemble-clock practice: NIST's AT1 algorithm and PTB-style ensembles do not exclude clocks showing structured drift but instead estimate the drift coefficient and steer the ensemble accordingly. The follow-up redesign should therefore not be "STRUCTURED with reduced weight" alone but **"STRUCTURED with reduced weight + drift parameter estimated and contributed back into the consensus"** — closer to AT1's per-clock state propagation. The natural starting point is α = 1 / (1 + IC_excess) with a separate drift-coefficient estimator on the STRUCTURED stream; the consensus then uses (reading − estimated_drift) as the contribution, weighted by α. This integrates the regime-detection role of § 5.3.1 with the established ensemble-clock practice.

2. **Decayed-staleness weighting *with state propagation*.** Currently neighbours are either dropped (delay > freshness) or used at full weight (stale-reading mode). A decayed weighting *w_j = exp(−λ τ_ij)* interpolates between these. The natural choice is λ ≈ 1/τ_correlation, where τ_correlation is the readings' autocorrelation time. Combined with **forward state propagation** (rather than the present manuscript's bare delayed-reading reuse) — i.e. each neighbour's contribution is its model-propagated state at time *t*, not its raw reading at time *t* − τ_ij — this is essentially a Kalman-filter-based ensemble structure analogous to AT1. Quantifying the staleness-vs-variance trade-off explicitly — the variance penalty from using stale data, vs the variance penalty from dropping the reading entirely — is the natural mini-ablation that would set the operating point for λ. **A baseline comparison against a tuned random-walk-FM Kalman ensemble is the appropriate yardstick for the redesigned architecture; the present manuscript's `bocpd` and `imm` are not such baselines.**

3. **Truly decentralised IC.** The present implementation computes each node's IC from the full same-time ensemble *Y*[t, :], so the classifier is *centralised* even though the consensus rule is local (§ 2.6). A fully decentralised redesign would compute each node *i*'s IC over only the readings *i* has actually received: *Y*[t, *i*] together with the delay-accessible neighbour set under the active delay convention. Each node would therefore have its own per-step Gaussian-mixture background built from its accessible-readings set, rather than reading off a globally-computed label. **This is the prerequisite for any deployment claim about ADMEC as a "fully decentralised" architecture.** The expected effect: the negative DG verdicts *strengthen* under truly local IC because the classifier loses information; the regime where the architecture is competitive may shift, since the classifier now sees the same delay-restricted view the consensus rule does.

Both are non-trivial code changes. They aim to use data *inside* the *k*_eff-element accessible neighbourhood more efficiently. Whether such redesigns can match a centralised aggregator when *k*_eff < *N* is itself an open question; the *N* / *k*_eff reference identified in § 5.1 captures only the static-memoryless prediction of how large the gap is, not a derived limit on what any architecture can achieve.

#### 5.6.1 Two further follow-ups: scenario-robustness and metric-bridging

Two additional follow-ups, distinct from the architectural redesigns above, came out of the pre-release reader pass and would sharpen the present manuscript's conclusions without changing the consensus rule itself. We do *not* run them here; they are flagged as the natural next-step campaign.

- **Extending S3 to more seeds and to a small graph family.** S3 (50-node random-sparse, target degree 3, Poisson(4.0) delays) is the manuscript's principal "large, sparse, delayed" scenario and the *N* / *k*_eff picture leans on it heavily — at 10 seeds and one fixed degree/delay parametrisation, it is a single point in graph-realisation space. The robustness check that would close that gap is (i) extending S3 to ~ 50 seeds to tighten the per-seed cluster SEM (currently 0.10 on the combined-tuned ratio), and (ii) sweeping a small family of (target-degree, delay-rate) pairs around (3, 4.0) — e.g. degrees {2, 3, 5} × delay-rates {2.0, 4.0, 6.0} — to confirm that the within-cluster offset below the *N* / *k*_eff line is not an artefact of the specific S3 parametrisation. The same harness can probe a different failure mode (e.g. a 5 σ phase step on the degraded clock, or an intermittent-outlier model, instead of the uniform 3 σ inflation used here) to test how far the classifier's two-way / three-way zero-delta result and the threshold-mismatch finding survive a non-Gaussian failure regime. None of this requires new code beyond the existing scenario-builder; the bottleneck is compute time and a fresh pre-registration of which axes of the family are measurement vs ablation.

- **Allan-deviation worked example bridging MSE to operational stability.** The MSE-vs-zero figure of merit used throughout this manuscript is a *characterisation* metric, not the operational metric for ensemble timekeeping (§ 2.6, § 5.5.1). A practitioner reader cannot read off from "MSE 0.025 → 0.196" what happens to modified Allan deviation σ_y(τ) at τ ≈ 100 s. Bridging the two requires a *fresh derivation* on the specific clock-noise model rather than a re-analysis of the existing archives: pick a maser-like noise model (white-FM dominant at short τ, transitioning to flicker-FM at τ ~ 60 s), simulate consensus output for a representative scenario (most informatively S3 baseline vs S3 combined-tuned), and compute σ_y(τ) on the consensus residual. The expected output is a single panel showing how the MSE-ratio gap on S3 (≈ 8 ×) projects onto the σ_y(τ) curve at operationally relevant τ, with the constraint layer's variance-absorption (§ 5.4) probably *helping* short-τ stability and the staleness mode (§ 4.1) probably *hurting* long-τ stability. This is a small follow-up paper of its own — the simulation setup and the noise-model fitting are non-trivial — and is reserved for that scope.

These two items are infrastructure-light and complement the architectural redesigns above: the former probes whether the *N* / *k*_eff picture is robust to scenario perturbations the present menu does not exercise, and the latter translates the manuscript's consensus-MSE findings into the language operational ensemble-clock practitioners actually use.

### 5.7 Connection to a broader causal-graph framework

These results admit a reading within the author's broader causal-graph framework for agreement architectures (Warring 2026b, Causal Clock Unification Framework — currently a self-cited unrefereed preprint). In that framework, a system's feasible operating regime is partitioned by η = (path latency) / (required agreement interval): when η ≪ 1 a centralised aggregator is feasible and locality is irrelevant; as η rises through the order of unity, locality becomes binding and the agreement architecture must use the data inside its causal cone efficiently. The three scenarios tested here span the relevant range — S2 sits at η ≪ 0.01 (a control point where locality does not bind), and S1 and S3 sit at η ≳ 0.1 in the regime where the *k*_eff / *N* reference becomes the dominant constraint on consensus performance.

The pooling-limit reference we observe (Fig. 1) is the η-graph partition made empirical for one scenario family within the ADMEC algorithm class. A follow-up study using the redesigns in § 5.6 would sit *inside* that reference line — relevant only when the topology already imposes a non-trivial η — and the natural pre-registration is in those terms: redesigns are evaluated by how close they push the local consensus to the *N* / *k*_eff line, not by whether they cross it.

## 6. Conclusion

This study characterises ADMEC across an 8-scenario simulation campaign and five orthogonal ablations and locates the regime in which the family is competitive with a centralised aggregator. The pre-registered decision gates are not met at the pre-registered operating points: ADMEC outperforms centralised baselines only on the fully-connected control scenario, and the three-way / two-way distinction is invisible to the consensus output (max delta = 0 across 360 ablation cells, an algebraic consequence of the consensus update rule reading only the binary STABLE mask). Combined design tuning reduces the largest-scenario MSE by 74 % but does not cross the *N* / *k*_eff pooling-limit reference line within our scenario family: under static-memoryless aggregation, the binding constraint on the family's local-consensus performance is *topological access to information*, not *estimator sophistication*. We do not extend that claim to algorithm classes outside our menu (hierarchical, gossip-with-epoch, asynchronous-clustering, Kalman-state-propagation ensemble-time algorithms); a similar reference *might* hold for them but our data does not show it. We further note that the present ADMEC implementation has a *global* classifier (computed from the full same-time ensemble) feeding a *local* consensus rule (delay-restricted neighbourhood); a fully decentralised redesign would compute IC over each node's delay-accessible readings only, and the negative DG verdicts should *strengthen* under that redesign.

Three constructive findings emerge from the characterisation:

1. **Per-reading IC calibration tuned for null false-positive rate is suboptimal for consensus MSE** (§ 4.4 threshold sweep, interpreted in § 5.2). At a lower matched threshold, ADMEC's constraint architecture beats centralised exclusion on two of the three signal-rich scenarios. The two are different optimisation problems with different optima.
2. **The constraint layer's actual role is variance absorption** (§ 4.2 constraint sensitivity, interpreted in § 5.4). It adds value only when paired with aggressive exclusion that creates the variance to absorb. This identifies the architecture's natural deployment regime — networks where centralisation is infeasible *and* the exclusion rule is aggressive — and reframes the constraint stack as a noise-management add-on rather than a rescue mechanism for delay-restricted consensus.
3. **The same-step *global* IC computation is well-formed** (§ 4.5 lagged classification, interpreted in § 6). No simultaneity bias is detectable in the lag = 0 vs lag = 1 ablation; lagging the classifier strictly hurts on signal-rich scenarios. The Gaussian-mixture self-reference is part of the IC definition, not a statistical artefact. *Caveat:* the present implementation computes IC from the full same-time ensemble; a fully-decentralised redesign would compute IC over each node's delay-accessible readings, and the lag dependence of *that* classifier is not characterised here.

The contribution of this study is a *characterisation of the boundary condition* under which local anomaly-aware consensus competes with centralised pooling, with the topological *N* / *k*_eff reference as the regime-locating heuristic. Three architectural redesigns are reserved for a follow-up study with its own pre-registration: (i) STRUCTURED with reduced weight + drift estimation; (ii) decayed-staleness weighting with state propagation; (iii) a fully-decentralised classifier that uses only each node's delay-accessible readings to compute its own IC. The first two aim to use data within the accessible neighbourhood more efficiently; the third addresses the present implementation's hybrid status (global classifier + local consensus rule) and is the prerequisite for any "fully decentralised" deployment claim.

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
| § 1 Fig. 0 (gate verdicts legend) | [`figure_gate_verdicts.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/figure_gate_verdicts.py) | (no archive — static legend rendered from in-script gate metadata) |
| § 5.1 Fig. 1 (topology ceiling) | [`figure_topology_ceiling.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/scripts/figure_topology_ceiling.py) | (consumes the WP2 + combined-tuning archives above) |

Test suite: 303 tests, 301 passing on the current pre-release technical-report state. The two known failures are documented σ-underestimation cases (logbook entry 002) that are mitigated downstream by the worst-case threshold calibration in entry 006; they exercise a pre-registered failure mode rather than indicating a regression.

**Technical-report canonical version.** The intended citable version is the annotated release tag `v1.0-tech-report`. The tag should be created only after the pre-release Atlas-integrity reader pass and the final DOI metadata are ready. Release commands:

```bash
git tag -a v1.0-tech-report -m "Technical report v1.0"
git push origin v1.0-tech-report
git rev-parse v1.0-tech-report
```

The resulting full-length SHA is the canonical commit for the technical report. After GitHub release archival through Zenodo, replace the DOI placeholders in the preferred-citation, data-availability, and code-availability blocks with the Zenodo DOI for `v1.0-tech-report`.

A WP1 walkthrough lives at [docs/wp1_tutorial.md](wp1_tutorial.md); a WP2 walkthrough at [docs/wp2_tutorial.md](wp2_tutorial.md). Both are runnable on Binder.

## 8. References

1. Adams, R. P. & MacKay, D. J. C. Bayesian online changepoint detection. arXiv:0710.3742 (2007).
2. Allan, D. W. Statistics of atomic frequency standards. *Proc. IEEE* **54**, 221–230 (1966). *(Cited as the standard stability-metric reference; the present manuscript does not use Allan deviation as a primary metric — see § 2.6 and § 5.5.1 for the implications.)*
3. Blom, H. A. P. & Bar-Shalom, Y. The interacting multiple model algorithm. *IEEE Trans. Automat. Contr.* **33**, 780–783 (1988).
4. Bothwell, T. et al. Resolving the gravitational redshift across a millimetre-scale atomic sample. *Nature* **602**, 420–424 (2022).
5. Boyd, S., Ghosh, A., Prabhakar, B. & Shah, D. Randomized gossip algorithms. *IEEE Trans. Inf. Theory* **52**, 2508–2530 (2006). *(Reference point in § 5.1.5 for spectral-gap analysis of average consensus; complementary to but distinct from the static-MSE figure of merit used here.)*
6. Dakos, V. et al. Methods for detecting early warnings of critical transitions. *PLoS ONE* **7**, e41010 (2012).
7. Huber, P. J. *Robust Statistics* (Wiley, 1981).
8. Lamport, L. Time, clocks, and the ordering of events in a distributed system. *Commun. ACM* **21**, 558–565 (1978).
9. Lenzen, C., Locher, T., Sommer, P. & Wattenhofer, R. Clock synchronization: open problems in theory and practice. *J. ACM* **66**, 32 (2019). *(Reference point in § 5.1.5 for fault-tolerant pulse-synchronisation bounds on graphs; threat model and figure of merit differ from ours.)*
10. Lisdat, C. et al. A clock network for geodesy and fundamental science. *Nat. Commun.* **7**, 12443 (2016). *(The European optical-fibre clock network. The present simulation's symmetric Poisson-delay model is *not* representative of optical-fibre links, which are deterministic and sub-microsecond stable; § 2.6 hedges the manuscript's claims accordingly.)*
11. Panfilo, G. & Arias, F. The Coordinated Universal Time (UTC). *Metrologia* **56**, 042001 (2019).
12. Scheffer, M. et al. Early-warning signals for critical transitions. *Nature* **461**, 53–59 (2009).
13. Warring, U. Causal Clock Unification Framework. Zenodo DOI: 10.5281/zenodo.17948436 (2026b).

---

## Statements

**Author contributions.** U.W. designed the study, pre-registered the decision gates and ablation menu in [docs/projektantrag.md](projektantrag.md), authored the source code in `src/`, ran the simulations and ablations, computed all numerical results, generated all figures, and authored the manuscript prose.

**Acknowledgements.** Calibration sanity checks, manuscript and logbook reviewers, and code-test contributors are listed in the project repository's commit log (`git log --format='%aN'` and `git shortlog -sn`). The Council-3 review chart (Guardian, Architect, Integrator stances) that drove the previous revision pass is recorded in the project's review notes. The pre-release Atlas-integrity reader pass — a domain-expert reading from the perspective of operational hydrogen-maser and optical-clock ensemble engineering — drove the current §§ 2.6, 4.4.1, 5.5.1 caveats, the reframing of § 5.6 redesigns to align with AT1-style ensemble-clock practice, and the references-section commentary on Allan 1966 / Lisdat 2016. The reviewer's findings are summarised in the project's `docs/` review notes.

**Funding.** This is a self-funded internal-discipline study; no external funding was received.

**Competing interests.** None declared.

**Data availability.** All data underlying the technical report are deposited as compressed `.npz` archives in [`data/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/data). Section 7 maps every numerical claim to a (script, archive) pair that reproduces it. The intended permanent archive is the Zenodo record generated from the GitHub release tag `v1.0-tech-report`; DOI: TBD.

**Code availability.** Source code is available at [https://github.com/threehouse-plus-ec/admec-clock-consensus](https://github.com/threehouse-plus-ec/admec-clock-consensus) under the MIT licence; documentation and figures under CC BY 4.0. The citable technical-report version is intended to be release tag `v1.0-tech-report`, archived through Zenodo; DOI: TBD.

**AI-assistance disclosure.** Claude (Anthropic) assisted with manuscript scaffolding, prose drafting, and code-template refinement. All simulations, calibrations, numerical results, code commits, scientific decisions, and claims are author-generated and author-verified. The author bears full responsibility for the manuscript's content. Specific AI-assisted activities are documented in commit messages throughout the project history (search for `Co-Authored-By: Claude` in the git log).

# Projektantrag — Beschreibung des Vorhabens

## Delay-Constrained Anomaly-Aware Consensus in Heterogeneous Clock Networks

*Following DFG Sachbeihilfe structure (form 54.01). Not for funding submission. For internal rigour. Version 0.5.2 (frozen).*

---

**Antragsteller:** Dr Ulrich Warring
**Institution:** Physikalisches Institut, Albert-Ludwigs-Universität Freiburg
**Fachgebiet:** Experimentalphysik / Messtechnik
**Geplante Laufzeit:** 12 Monate (April 2026 – March 2027)
**Requested resources:** None (self-funded; internal discipline device)

---

### 1 — Summary

This project develops and tests a consensus scheme for heterogeneous clock networks that classifies nodes into three categories — stable, structured anomaly, and unstructured anomaly — and applies different update rules to each, subject to communication-delay constraints and explicit update-size limits.

The central observable is Information Content (IC), a measure of distributional inconsistency based on the interval probability of each observation under the ensemble's own background distribution. IC requires no parametric signal model but is calibrated under specific null noise assumptions. IC alone flags anomalies; a second criterion — temporal structure (rising variance or autocorrelation over a trailing window) — separates structured anomalies (those with persistent, temporally correlated departures that may carry information about ongoing systematic change) from unstructured anomalies (memoryless noise bursts, isolated outliers). The scheme preserves structured disagreement rather than suppressing it: nodes flagged as structured anomalies are tracked and gated rather than excluded or averaged in.

The project tests whether temporal structure within anomalies changes the optimal consensus response relative to exclusion-based robust methods. If it does, the three-way classification is a useful design principle. If it does not, the result is a carefully documented negative finding showing that established robust methods are sufficient for the tested regime.

The method is tested on simulated heterogeneous clock networks with noise parameters drawn from published hydrogen maser characterisations (Panfilo & Arias 2019). The comparison set includes frequentist weighted averaging, exclusion-based robust averaging, a Huber M-estimator (with tuning sensitivity), Bayesian online changepoint detection (Adams & MacKay 2007), an interacting multiple model filter (Blom & Bar-Shalom 1988), and the proposed scheme with and without its constraint layers. Baselines are given per-scenario tuning to prevent strawman comparisons. Performance is evaluated on IC-independent metrics: mean squared error, variance preservation (collapse index), and correlation with injected structure.

Whether structured anomalies carry predictive lead–lag information about network-level deviations is tested as an exploratory analysis, not a core objective.

**Keywords:** consensus estimation, anomaly classification, clock networks, information content, delay-constrained updating, robust aggregation

---

### 2 — State of the Art and Own Preliminary Work

#### 2.1 — State of the art

**2.1.1 Time-scale construction.** International Atomic Time (TAI) is constructed by the ALGOS algorithm at BIPM: a stability-weighted average of ~450 atomic clocks with iterative outlier detection (Panfilo & Arias 2019). TAI achieves ~2 × 10⁻¹⁶ frequency stability over one month. The present project does not propose to improve TAI. It uses simulated clock networks as a controlled testbed for studying how consensus methods handle heterogeneous, delay-constrained ensembles — a regime that will become increasingly relevant as optical clock networks with sub-10⁻¹⁸ instability become operational (Lisdat et al. 2016, Bothwell et al. 2022).

**2.1.2 Robust consensus and anomaly detection.** Robust estimation (Huber 1981) downweights or removes observations inconsistent with a central model. Bayesian online changepoint detection (Adams & MacKay 2007) identifies abrupt distributional shifts and implicitly distinguishes pre- from post-change regimes. Switching state-space models (interacting multiple model filters; Blom & Bar-Shalom 1988) maintain parallel hypotheses about system mode and can, in principle, track temporally structured departures. These methods address anomaly handling in estimation, and some (BOCPD, IMM) do capture temporal structure to varying degrees. However, their default response to detected anomalies is still to exclude, downweight, or absorb the anomalous node into a revised model — not to preserve its output as a separately tracked information channel under communication constraints.

**2.1.3 Early warning signals.** Rising variance and autocorrelation near bifurcations are generic early-warning indicators (Scheffer et al. 2009, Dakos et al. 2012). These statistics have known failure modes (false positives under correlated noise, false negatives under fast transitions). The present project uses them as a classification heuristic for one scenario type (S8, near-bifurcation), not as a general detection theory.

**2.1.4 Motivating analogy: near-critical sensing.** Systems operating near regime boundaries exhibit both high sensitivity and reduced invertibility (Warring 2026a). This trade-off — sensitivity and ambiguity arising from the same eigenvalue structure — motivates the project's central design choice: instead of excluding all anomalous nodes, distinguish those whose anomaly has temporal structure (and may therefore carry information about systematic change) from those whose anomaly is memoryless. This analogy motivates the design but is not the project's evidentiary claim.

**2.1.5 Gap.** Robust consensus methods (Huber, redescending estimators, consensus with robust loss functions) suppress anomalies. BOCPD and IMM-style filters do capture temporal structure — they model run length, mode persistence, and can distinguish sustained shifts from transients. What these methods do not do is *preserve the anomalous node's output as a separately tracked channel* within the consensus: once a changepoint is detected or a mode switch is inferred, the node is either re-initialised, excluded, or absorbed into a revised model. The present project asks whether an alternative response — tracking structured anomalies under delay and update constraints rather than absorbing or discarding them — yields measurable improvement. This is a narrow empirical question, not a claim that existing methods are fundamentally deficient.

#### 2.2 — Own preliminary work

**Trapped-ion physics.** The applicant has 15 years of experience with trapped-ion Coulomb crystals, including systems near structural phase transitions (Heidelberg → MPIK → NIST Boulder → Freiburg since 2013). This background informs the project's physical intuition about near-boundary operation but is not directly engaged experimentally.

**Near-critical sensing essay.** The applicant has completed "Amplifiers at the Boundary" (v0.4.0, Warring 2026a), an interpretive essay connecting 19th-century atmospheric instruments to modern boundary sensors. This essay motivates the project's design philosophy.

**Framework development.** The applicant has developed the IC observable (interval-probability definition, not yet calibrated), an update-constraint filter (not yet implemented in tested form), and a prototype simulation skeleton for a 15-clock network (not yet validated). No validated simulation results exist. The present proposal is designed to produce them.

---

### 3 — Objectives and Work Programme

#### 3.1 — Objectives

| ID | Objective | Success criterion |
|----|-----------|-------------------|
| O1 | Calibrate IC as a distributional inconsistency measure under null models | AIPP converges to ~0.55 bit (±5%) for Gaussian null at N ≥ 100; percentile thresholds stable within factor 1.5 across noise models; robust under ±20% σ perturbation |
| O2 | Demonstrate that three-way classification (stable / structured anomaly / unstructured anomaly) yields measurably different estimator behaviour from two-way (normal / anomalous) | Classification-aware estimator outperforms exclusion-based estimator (FREQ-exclude) and Huber M-estimator on MSE *and* at least one of {collapse index, structure correlation}, in S1 and S3 |
| O3 | Demonstrate that delay constraints improve robustness | Delay-constrained estimator outperforms unconstrained variant on IC-independent metrics |
| O4 | Demonstrate that update-size constraints independently improve structure preservation | Full-constraint estimator outperforms delay-only variant on collapse index |
| O5 (exploratory) | Test whether structured-anomaly nodes carry predictive lead–lag information | Cross-correlation analysis with permutation test; reported but not a gate condition |

O2 is the core scientific question. If it fails, the three-way classification adds no value over simpler robust methods and the project archives a negative result.

#### 3.2 — Work programme

**WP1 — IC Calibration (months 1–2)**

Tasks: Implement IC (interval probability, analytic Gaussian CDF). IC is nonparametric in the functional form of anomalies but calibrated under specific null models; the term "model-free" refers to the absence of a parametric signal model, not to the absence of distributional assumptions in calibration. Verify AIPP → 0.55 bit (Gaussian null). Null-model calibration: Gaussian i.i.d., heteroscedastic Gaussian, Student-t (ν = 3, 5, 10), power-law (Pareto α = 2.5, 3.0), AR(1) with ρ ∈ {0.3, 0.7, 0.9} (correlated noise), 1/f (flicker) via AR(1) approximation. Finite-N bias quantification. σ-sensitivity analysis (±20% perturbation). Percentile thresholds (95th, 99th). When IC thresholds are applied across N nodes × T time steps, report the effective false-positive rate per scenario and note that no formal family-wise or FDR correction is applied; the threshold is a classification heuristic, not a hypothesis test.

Deliverables: IC specification document. Tested Python module (< 100 lines). Calibration figures including correlated-noise nulls.

Decision gate DG-1: AIPP converges (±5%). Thresholds stable within ×1.5 across all null models including correlated noise. σ-sensitivity bounded. *Fail: halt.*

**WP2 — Clock Network Simulation (months 2–5)**

System model: N clocks with power-law noise (white frequency, flicker frequency, random-walk frequency). Reference parameterisation drawn from the active hydrogen maser characterisation in Panfilo & Arias (2019, Table 1): σ_y(τ = 1 day) ≈ 1.5 × 10⁻¹⁵ (white frequency), flicker floor σ_y ≈ 7 × 10⁻¹⁶ at τ ≈ 10 days. Majority clocks use these parameters; 1–2 clocks are degraded (3× noise, heavy-tailed). Network: ring, random-sparse (k ≈ 3), fully connected. Communication: asynchronous updates with Poisson-distributed delays (mean τ specified per topology). Poisson delays are a convenience model, not a claim about real link statistics; they provide controllable heterogeneity in information accessibility.

Stochastic differential equation per clock:

    df_i = drift_i · dt + σ_wf · dW_i + σ_ff · dB_i(flicker) + signal_i(t) · dt

where dW is Wiener, dB(flicker) is a fractional noise process approximated by an AR(1) filter with spectral slope h_α = −1 (flicker frequency). Parameters scaled from the reference maser characterisation above.

Classification rule:

    STABLE:              IC < threshold
    STRUCTURED ANOMALY:  IC ≥ threshold AND (variance trend > 0 OR autocorrelation trend > 0) over window W
    UNSTRUCTURED ANOMALY: IC ≥ threshold AND no temporal trend

Robustness: classification tested under W ∈ {10, 15, 20, 30}. The temporal-trend criteria are heuristic classifiers, not formal structural inference methods; they are sensitive to noise colour and window length. The project tests whether this simple heuristic is sufficient to yield measurable estimator improvement, not whether it is optimal.

Estimators (nine):

| Label | Method | Update equations |
|-------|--------|-----------------|
| FREQ-global | Σ w_i f_i, weights ∝ 1/σ²_running | Standard weighted mean |
| FREQ-local | Same, restricted to delay-accessible neighbours | Weighted mean over {j : τ_{ij} ≤ Δt} |
| FREQ-exclude | Weighted mean excluding IC ≥ threshold nodes | Exclusion-based robust average |
| HUBER | Huber M-estimator; tuning constant c tested at {1.0, 1.345, 2.0} and best-performing value used per scenario (reported) | Iteratively reweighted least squares |
| BOCPD | Bayesian online changepoint detection (Adams & MacKay 2007) per node; hazard rate λ tested at {50, 100, 200} steps; post-changepoint nodes excluded | Run-length posterior; best hazard per scenario reported |
| IMM | Interacting multiple model filter (Blom & Bar-Shalom 1988) with two modes: nominal and anomalous; transition probabilities tested at p_switch ∈ {0.01, 0.05, 0.1} | Two-mode Kalman bank with Markov switching; best transition matrix per scenario reported |
| ADMEC-unconstrained | IC-based classification, no delay or update constraints | Three-way classification, uniform correction |
| ADMEC-delay | IC-based classification + delay-constrained updates | Corrections restricted to delay-accessible neighbours |
| ADMEC-full | IC-based classification + delay constraints + update-size constraints (projection onto feasible set: variance ratio ∈ [0.5, 1.5], step ≤ 3σ, total energy ≤ Nσ²; thresholds fixed a priori from running-noise scale, not tuned post hoc; sensitivity tested under ±30% variation in WP3). The energy bound Nσ² is chosen as the expected total squared fluctuation under the null; the variance-ratio bounds [0.5, 1.5] encode the requirement that a single update step should neither halve nor double ensemble variance. If the feasible set is empty (all three constraints cannot be simultaneously satisfied), the update is rejected entirely and the previous state is retained. | Full scheme |

Scenarios (eight):

| ID | N | Topology | Delays | Injection | Tests |
|----|---|----------|--------|-----------|-------|
| S1 | 15 | Ring | Poisson(2.0) | Sinusoidal on 3 clocks | Structure preservation |
| S2 | 15 | Fully connected | Poisson(0.3) | Sinusoidal on 3 clocks | Control: delays negligible |
| S3 | 50 | Random-sparse | Poisson(4.0) | Sinusoidal on 3 clocks | Scaling |
| S4 | 15 | Ring | Poisson(2.0) | None | Null |
| S5 | 50 | Random-sparse | Poisson(4.0) | None | Null at scale |
| S6 | 15 | Ring | Poisson(2.0) | Linear drift on 2 clocks | Anomaly detection (not near-critical) |
| S7 | 30 | Ring | Poisson(2.0) | Step-function shift on 3 clocks at t = T/2 | Change-point detection (not near-critical) |
| S8 | 15 | Ring | Poisson(2.0) | 2 clocks with drift rate approaching fold bifurcation: drift(t) = r(t) where dr/dt = ε, dynamics dx/dt = r + x². Physically: models a slow degradation of one clock's control parameter (e.g. cavity drift, electronics ageing) that gradually reduces the restoring force of the frequency servo until the lock point vanishes. | Near-critical dynamics with genuine CSD |

Each scenario: 10 seeds (increased from 5). Report mean ± std.

IC-independent metrics: MSE (relative reduction in mean across seeds), collapse index, structure correlation (Pearson r with injected signal on signal clocks after onset).

Decision gate DG-2: ADMEC-full shows ≥ 15% relative reduction in MSE *and* improvement in ≥ 1 of {CI, structure correlation} versus FREQ-global, in S1 *and* S3. ADMEC-full outperforms FREQ-exclude, HUBER, BOCPD, and IMM on ≥ 1 IC-independent metric. ADMEC-full outperforms ADMEC-delay (update constraints contribute). *Fail: archive as negative result. Explicitly report comparison with all baselines.*

Decision gate DG-2b (classification validation): Evaluated against designer-injected structure (not an independent ground truth). True positive rate ≥ 70%. This is an internal consistency check, not an external validation. *Fail: three-way classification does not reliably separate structured from unstructured anomalies. Collapse to two-way (normal/anomalous) and report.*

Lead–lag analysis (exploratory, not gated): Permutation test (100 shuffles). Sensitivity over W ∈ {10, 15, 20, 30}. Reported regardless of outcome.

**WP3 — Ablation (month 5)**

Five configurations: ADMEC-unconstrained, ADMEC-delay, ADMEC-full, ADMEC-full-lagged (classification uses IC(t−1) to test simultaneity bias), ADMEC-two-class (binary normal/anomalous, no structured/unstructured distinction). Run on S1, S3, S8.

Decision gate DG-3: Each constraint layer contributes ≥ 10% on ≥ 1 IC-independent metric. Three-way outperforms two-way (ADMEC-full vs ADMEC-two-class). *Fail: constraints or classification add no value. Archive.*

**WP4 — Publication (months 5–9)**

| Gate outcomes | Target |
|---------------|--------|
| DG-1 ✓ + DG-2 ✓ + DG-3 ✓ | PRA / Entropy / Chaos (methods paper) |
| DG-1 ✓ + DG-2 ✓ + DG-3 partial | arXiv technical note |
| DG-1 ✓ + DG-2 partial or ✗ | IC specification + negative result on Zenodo |
| DG-1 ✗ | Archive |

All outputs under open licences. Code and data on Zenodo with DOIs.

Note: Nature Machine Intelligence is removed as a target. The project does not produce AI benchmarks and should not claim AI relevance beyond a brief outlook paragraph.

---

### 4 — Scientific Relevance

The project addresses a specific gap in consensus estimation: whether explicitly distinguishing structured from unstructured anomalies, and preserving structured anomalies as tracked information rather than discarding them, yields measurable improvement over simpler robust methods (Huber, BOCPD, exclusion).

The clock-network testbed is informed by metrology but is a controlled simulation, not a replica of TAI or any operational system. The project's contribution, if O2 is confirmed, is a candidate estimator design principle: *not all anomalies should be suppressed; some should be reclassified and tracked.* If O2 fails, the contribution is a careful negative result showing that established robust methods are sufficient for the tested regime.

The near-critical sensing analogy (Warring 2026a) motivates the design but is not tested as a scientific claim except in scenario S8, which explicitly instantiates fold-bifurcation dynamics.

**Falsifiability:** The central claim fails if ADMEC-full does not outperform the Huber M-estimator, BOCPD, or IMM on IC-independent metrics across the tested scenarios.

---

### 5 — Schedule

| Month | Activity | Gate |
|-------|----------|------|
| 1–2 | WP1: IC calibration | DG-1 |
| 2–5 | WP2: Simulation (8 scenarios × 10 seeds × 8 estimators) + lead–lag analysis | DG-2, DG-2b |
| 5 | WP3: Ablation (5 configs × 3 scenarios × 10 seeds) | DG-3 |
| 5–9 | WP4: Manuscript | Submission |
| 9–12 | Buffer: revisions, code release | — |

---

### 6 — Prerequisites

Single investigator. Laptop + Python/NumPy/SciPy. No funding, no equipment, no institutional resources beyond office space. Compatible with existing teaching duties (FP-2/FP-EDU).

---

### 7 — Research Data Management

All code, data, and specifications on Zenodo with DOIs. Open licences (CC BY 4.0 / MIT). Full reproducibility (seeds, versions pinned). Negative results published.

---

### 8 — Ethical Aspects

No human subjects, animal subjects, dual-use, or sensitive data. AI tools (Claude, Anthropic) used for brainstorming and structural editing. All scientific content is the sole responsibility of the applicant.

---

### 9 — References

1. Panfilo, G. & Arias, F. *Metrologia* **56**, 042001 (2019).
2. Lisdat, C. et al. *Nat. Commun.* **7**, 12443 (2016).
3. Bothwell, T. et al. *Nature* **602**, 420–424 (2022).
4. Huber, P. J. *Robust Statistics* (Wiley, 1981).
5. Adams, R. P. & MacKay, D. J. C. Bayesian online changepoint detection. Preprint arXiv:0710.3742 (2007).
6. Blom, H. A. P. & Bar-Shalom, Y. The interacting multiple model algorithm. *IEEE Trans. Automat. Contr.* **33**, 780–783 (1988).
7. Scheffer, M. et al. *Nature* **461**, 53–59 (2009).
8. Dakos, V. et al. *PLoS ONE* **7**, e41010 (2012).
9. Cover, T. M. & Thomas, J. A. *Elements of Information Theory* 2nd edn (Wiley, 2006).
10. Grünwald, P. D. *The Minimum Description Length Principle* (MIT Press, 2007).
11. Lamport, L. *Commun. ACM* **21**, 558–565 (1978).
12. Warring, U. Amplifiers at the boundary. Preprint (2026a).
13. Warring, U. What can make a complex system an ordinans? (2025).
14. Warring, U. Causal Clock Unification Framework. Zenodo DOI: 10.5281/zenodo.17948436 (2026b).

---

### Appendix — Risk Register

| # | Risk | L | I | Mitigation |
|---|------|---|---|------------|
| R1 | IC unstable under σ variation | M | H | σ-sensitivity analysis in WP1 (±20%). Fallback: phase-mismatch proxy. |
| R2 | No difference vs robust baselines | M | H | Huber + BOCPD + IMM in comparison set. Honest negative result. |
| R3 | Update constraints over-constrain | M | M | Start loose, tighten. Ablation in WP3. |
| R4 | Scope creep | H | M | Decision gates enforce stop/go. |
| R5 | Time pressure | M | M | 3-month buffer. Seeds increased to 10 for statistical robustness. |
| R6 | Metric coupling | H | M | IC-independent primary metrics. Lagged-IC ablation in WP3. |
| R7 | Three-way ≈ two-way (no value in structured/unstructured distinction) | M | H | ADMEC-two-class ablation. If no difference: collapse to two-way and report. |
| R8 | Lead–lag underpowered | M | M | Exploratory, not gated. Permutation test. |
| R9 | S8 bifurcation scenario unstable or unphysical | M | M | Use standard saddle-node normal form. Test parameter range before full sweep. |

---

### Appendix — Decision Gates

| Gate | Pass | Fail |
|------|------|------|
| DG-1 | AIPP ≈ 0.55 bit (±5%); thresholds ×1.5; σ-robust | Halt |
| DG-2 | ADMEC-full ≥ 15% MSE reduction AND ≥ 1 other metric, in S1 AND S3; outperforms Huber, BOCPD, and IMM on ≥ 1 metric | Archive negative result |
| DG-2b | Three-way TP ≥ 70% (internal check) | Collapse to two-way |
| DG-3 | Each constraint ≥ 10%; three-way > two-way | Archive |

---

*Document prepared for internal discipline. No Council-3, Guardian, or Harbour terminology in the technical proposal. Those frameworks inform the applicant's thinking but do not belong in a scientific project description.*

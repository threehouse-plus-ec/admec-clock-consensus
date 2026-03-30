# Rebuttal and Revised Projektantrag

## Part I — Point-by-Point Rebuttal

---

### Response to the hostile review of ADM-EC Projektantrag v0.4

The review is substantially correct in its diagnosis of the proposal's main weaknesses. The revision implements the three recommended cuts and addresses each major criticism. Where the review overstates, I note this briefly; where it is right, I concede and cut.

---

#### 1.1 "The central scientific object is still unclear"

**Conceded.** The proposal tried to be three things simultaneously (new observable, new gating scheme, new epistemic vocabulary) and was convincing as none of them. The revision contracts the claim to:

*A delay-constrained, anomaly-aware consensus scheme that explicitly preserves structured disagreement rather than suppressing it.*

The "dual-mode epistemology" language is removed from the main text. If the results warrant it, the interpretation can be offered in a discussion section; it does not belong in the objectives.

#### 1.2 "Sentinel remains under-justified and partly decorative"

**Partially conceded.** The reviewer is right that the operational distinction between "sentinel" and "anomalous" is thin in the current implementation. The revision:

- Demotes "sentinel" from an epistemic category to a *working label* for structured anomalies (high IC + temporal correlation). No philosophical claims are attached.
- Removes the phrase "different epistemic mode" everywhere.
- Retains the three-way classification as a *testable hypothesis* (does the structured/unstructured anomaly distinction yield different estimator behaviour?) rather than as an established fact.

#### 1.3 "Generative models do not support conceptual claims"

**Conceded.** This is the most damaging criticism. The revision:

- Removes near-critical sensing from the project's evidentiary backbone. It is demoted to a *motivating analogy* in one paragraph of §2.1, not a claimed mechanism.
- Adds one scenario (S8) with a genuine nonlinear bifurcation: a clock whose drift rate is a function of a control parameter approaching a fold bifurcation. This is the minimal scenario that actually instantiates critical slowing down.
- Explicitly states that S6 (linear drift) and S7 (step change) do not test near-critical dynamics. They test anomaly detection and change-point detection respectively. Only S8 tests the near-critical claim.

#### 1.4 "Benchmark is too synthetic"

**Partially conceded.** All benchmarks are synthetic — that is inherent to a proposal without existing data. The revision:

- Specifies the clock noise model using standard power-law noise types from the time-scale literature (white frequency, flicker frequency, random-walk frequency) with parameters drawn from published characterisations of hydrogen masers and caesium fountain clocks.
- Specifies the network communication model (asynchronous update with Poisson-distributed delays).
- Drops the claim that the benchmark "represents" real optical clock networks. It is a *controlled testbed* with parameters informed by metrology, not a replica of TAI.

#### 1.5 "AI connection is opportunistic"

**Conceded.** The revision moves all AI references to a single outlook paragraph. The project is a metrology-inspired simulation study. If the method works, the AI connection can be explored in a separate project with AI-native benchmarks. It is not tested here and should not be claimed here.

#### 1.6 "May reduce to a robust statistics result"

**Partially conceded — this is the key scientific risk.** The revision:

- Adds three stronger baselines to the comparison set: a Huber M-estimator, a Bayesian online changepoint detector (Adams & MacKay 2007), and a switching state-space model (interacting multiple model filter). These are the minimum credible comparators.
- Explicitly states: if ADM-EC does not outperform the Huber estimator or the changepoint detector on IC-independent metrics, the contribution reduces to "a gating heuristic with no advantage over established robust methods." That is a legitimate negative result.

#### 2.1 "O1 is fragile"

**Partially conceded.** The revision:

- Tightens the DG-1 threshold stability criterion from "within factor 2" to "within factor 1.5."
- Adds a sensitivity analysis: AIPP computed under ±20% perturbation of declared σ values.

#### 2.2 "O2 is under-motivated"

**Conceded.** O2 is demoted from a scientific objective to a technical sanity check. It no longer appears in the objectives table.

#### 2.3 "DG-2 is vulnerable to cherry-picking"

**Partially conceded.** The revision:

- Changes "MSE *or* structure correlation" to "MSE *and* at least one of {CI, structure correlation}." Both accuracy and diversity preservation must improve.
- Requires improvement in S1 *and* S3 (both, not either).
- Specifies: 15% means relative reduction in mean MSE across seeds.

#### 2.4 "DG-2b uses circular synthetic ground truth"

**Conceded in spirit.** The revision explicitly states that DG-2b validates classifier behaviour against designer-injected structure, not against an independently established "sentinel" category. It is an internal consistency check, not an external validation.

#### 2.5 "Lead–lag is statistically shaky"

**Partially conceded.** The revision:

- Adds a permutation test (100 shuffles per scenario) as the primary significance test, replacing the percentile-of-null approach.
- Adds sensitivity analysis over window size W ∈ {10, 15, 20, 30}.
- Downgrades O7 from a core objective to an *exploratory analysis*. If it works, it is reported; if not, no claim is made.

#### 2.6 "Ordinans remains underdefined"

**Conceded.** The revision:

- Specifies the Ordinans filter as a projection operator: proposed updates are projected onto the feasible set defined by three explicit constraints (variance ratio ∈ [0.5, 1.5], step size ≤ 3σ per node, total correction energy ≤ Nσ²). The projection is Euclidean (closest-point).
- Removes the Ordinans framework's broader vocabulary (Affectio, Habitus, Integratio, etc.) from the proposal. These belong to the interpretive essay, not to a technical project description.

#### 2.7 "Causal language is stronger than the method"

**Conceded.** The revision:

- Replaces "causal gating" with "delay-constrained updating" throughout.
- Removes the Pearl citation. The method does not perform causal inference; it respects communication delays. That is a network constraint, not a causal model.

#### 3.1 "Weak fit to review board 303"

**Acknowledged.** The project is a methods study with physics motivation, not an experimental physics project. The revision reframes it accordingly and suggests review board 312 (Mathematik / Informatik) or an interdisciplinary panel as potentially more appropriate.

#### 3.2 "Too much essay logic"

**Conceded.** The revision removes: "dual-mode epistemology," "sentinel tradition," "routes around non-invertibility," "principled distinction." What remains is technical description.

---

## Part II — Revised Projektantrag v0.5

---

# Projektantrag — Beschreibung des Vorhabens

## Delay-Constrained Anomaly-Aware Consensus in Heterogeneous Clock Networks

*Following DFG Sachbeihilfe structure (form 54.01). Not for funding submission. For internal rigour. Version 0.5.3 (frozen).*

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

**2.1.2 Robust consensus and anomaly detection.** Robust estimation (Huber 1981) downweights or removes observations inconsistent with a central model. Bayesian online changepoint detection (Adams & MacKay 2007) identifies abrupt distributional shifts and implicitly distinguishes pre- from post-change regimes. Switching state-space models (interacting multiple model filters; Blom & Bar-Shalom 1988) maintain parallel hypotheses about system mode and can, in principle, track temporally structured departures. These methods address anomaly handling in estimation, and some (BOCPD, IMM) do capture temporal structure to varying degrees. However, their default response to detected anomalies is still typically to exclude, downweight, or absorb the anomalous node into a revised model — not to preserve its output as a separately tracked information channel under communication constraints.

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
| O1 | Calibrate IC as a distributional inconsistency measure under null models | AIPP converges to theoretical limit ≈ 1.25 bit (±5%) for Gaussian null at N ≥ 100; percentile thresholds stable within factor 1.5 across noise models including correlated noise; robust under ±20% σ perturbation |
| O2 | Demonstrate that three-way classification (stable / structured anomaly / unstructured anomaly) yields measurably better consensus than both two-way classification and established robust baselines | ADMEC-full outperforms the best non-ADMEC baseline on ≥ 2 IC-independent metrics in S1 and S3 (DG-2). ADMEC-full also outperforms ADMEC-two-class (DG-3), confirming the structured/unstructured distinction adds value beyond binary anomaly handling. |
| O3 | Demonstrate that delay constraints improve robustness | Delay-constrained estimator outperforms unconstrained variant on IC-independent metrics |
| O4 | Demonstrate that update-size constraints independently improve structure preservation | Full-constraint estimator outperforms delay-only variant on collapse index |
| O5 (exploratory) | Test whether structured-anomaly nodes carry predictive lead–lag information | Cross-correlation analysis with permutation test; reported but not a gate condition |

O2 is the core scientific question. If it fails, the three-way classification adds no value over simpler robust methods and the project archives a negative result.

#### 3.2 — Work programme

**WP1 — IC Calibration (months 1–2)**

Tasks: Implement IC (interval probability, analytic Gaussian CDF). IC is nonparametric in the functional form of anomalies but calibrated under specific null models; the term "model-free" refers to the absence of a parametric signal model, not to the absence of distributional assumptions in calibration. Verify AIPP convergence to the theoretical large-N limit (≈ 1.25 bit for σ_data = σ_declared = 1; derived from the convolution of the data distribution with the Gaussian kernel). Null-model calibration: Gaussian i.i.d., heteroscedastic Gaussian, Student-t (ν = 3, 5, 10), power-law (Pareto α = 2.5, 3.0), AR(1) with ρ ∈ {0.3, 0.7, 0.9} (correlated noise), 1/f (flicker) via AR(1) approximation. Finite-N bias quantification. σ-sensitivity analysis (±20% perturbation). Percentile thresholds (95th, 99th). Thresholds are used only to define operating regions for the classifier and are not interpreted as formal significance levels. When applied across N nodes × T time steps, the effective false-positive rate per scenario is reported; no formal family-wise or FDR correction is applied.

Deliverables: IC specification document. Tested Python module (< 100 lines). Calibration figures including correlated-noise nulls.

Decision gate DG-1: AIPP converges (±5%). Thresholds stable within ×1.5 across all null models including correlated noise. σ-sensitivity bounded. *Fail: halt.*

**WP2 — Clock Network Simulation (months 2–5)**

System model: N clocks with power-law noise (white frequency, flicker frequency, random-walk frequency). Reference parameterisation drawn from the active hydrogen maser characterisation in Panfilo & Arias (2019, Table 1): σ_y(τ = 1 day) ≈ 1.5 × 10⁻¹⁵ (white frequency), flicker floor σ_y ≈ 7 × 10⁻¹⁶ at τ ≈ 10 days. Majority clocks use these parameters; 1–2 clocks are degraded (3× noise, heavy-tailed). Network: ring, random-sparse (k ≈ 3), fully connected. Communication: asynchronous updates with Poisson-distributed delays (mean τ specified per topology). Poisson delays are a convenience model, not a claim about real link statistics; they provide controllable heterogeneity in information accessibility.

Stochastic differential equation per clock:

    df_i = drift_i · dt + σ_wf · dW_i + σ_ff · dB_i(flicker) + signal_i(t) · dt

where dW is Wiener, dB(flicker) is a fractional noise process approximated by an AR(1) filter with spectral slope h_α = −1 (flicker frequency). Parameters scaled from the reference maser characterisation above.

Classification rule:

    STABLE:              IC < threshold
    STRUCTURED ANOMALY:  IC ≥ threshold AND (variance trend slope > δ_min OR autocorrelation trend slope > δ_min) over window W
    UNSTRUCTURED ANOMALY: IC ≥ threshold AND no trend exceeding δ_min

where δ_min is a minimum effect-size threshold fixed a priori as the median absolute slope observed under the null scenarios (S4/S5). A positive trend is counted only if it exceeds this null-calibrated floor.

Robustness: classification tested under W ∈ {10, 15, 20, 30}. The temporal-trend criteria are heuristic classifiers, not formal structural inference methods; they are sensitive to noise colour and window length. The project tests whether this simple heuristic is sufficient to yield measurable estimator improvement, not whether it is optimal.

Estimators (nine):

| Label | Method | Update equations |
|-------|--------|-----------------|
| FREQ-global | Σ w_i f_i, weights ∝ 1/σ²_running | Standard weighted mean |
| FREQ-local | Same, restricted to delay-accessible neighbours | Weighted mean over {j : τ_{ij} ≤ Δt} |
| FREQ-exclude | Weighted mean excluding IC ≥ threshold nodes | Exclusion-based robust average |
| HUBER | Huber M-estimator; tuning constant c tested at {1.0, 1.345, 2.0}; best c selected on null scenarios (S4/S5) and then fixed for all signal scenarios | Iteratively reweighted least squares |
| BOCPD | Bayesian online changepoint detection (Adams & MacKay 2007) per node; hazard rate λ tested at {50, 100, 200}; best λ selected on null scenarios (S4/S5) and fixed for all signal scenarios; post-changepoint nodes excluded | Run-length posterior |
| IMM | Interacting multiple model filter (Blom & Bar-Shalom 1988) with two modes: nominal and anomalous; p_switch tested at {0.01, 0.05, 0.1}; best selected on null scenarios (S4/S5) and fixed | Two-mode Kalman bank with Markov switching |
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
| S8 | 15 | Ring | Poisson(2.0) | 2 clocks with drift rate approaching fold bifurcation: drift(t) = r(t) where dr/dt = ε, dynamics dx/dt = r + x². Physically: models a slow degradation of one clock's control parameter (e.g. cavity drift, electronics ageing) that gradually reduces the restoring force of the frequency servo until the lock point vanishes. The bifurcation enters the simulation as a slow loss of restoring behaviour, producing increased variance and autocorrelation in the measured frequency residuals before loss of lock. | Near-critical dynamics with genuine CSD |

Each scenario: 10 seeds (increased from 5). Report mean ± std.

IC-independent metrics: MSE (relative reduction in mean across seeds), collapse index, structure correlation (Pearson r with injected signal on signal clocks after onset).

Decision gate DG-2: ADMEC-full must outperform the best-performing non-ADMEC baseline (whichever of FREQ-global, FREQ-exclude, HUBER, BOCPD, or IMM scores highest) on at least two IC-independent metrics (from {MSE, CI, structure correlation}), in S1 *and* S3. ADMEC-full must also outperform ADMEC-delay (update constraints contribute independently). *Fail: archive as negative result. Explicitly report comparison with all baselines.*

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
13. Warring, U. Causal Clock Unification Framework. Zenodo DOI: 10.5281/zenodo.17948436 (2026b).

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
| DG-1 | AIPP ≈ 1.25 bit (±5%); thresholds ×1.5 across all nulls including correlated; σ-robust | Halt |
| DG-2 | ADMEC-full outperforms best non-ADMEC baseline on ≥ 2 IC-independent metrics in S1 AND S3; outperforms ADMEC-delay | Archive negative result |
| DG-2b | Three-way TP ≥ 70% against synthetic ground truth (internal check) | Collapse to stable / anomalous (two-way) |
| DG-3 | Each constraint ≥ 10%; three-way > two-way (ADMEC-full > ADMEC-two-class) | Archive |

---

*Document prepared for internal discipline. No Council-3, Guardian, or Harbour terminology in the technical proposal. Those frameworks inform the applicant's thinking but do not belong in a scientific project description.*

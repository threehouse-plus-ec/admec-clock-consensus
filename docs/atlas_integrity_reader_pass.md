# Atlas-Integrity Reader Pass — Pre-release Domain-Expert Review

**Date:** 2026-05-05
**Reader perspective:** Operational hydrogen-maser and optical-clock ensemble engineering; clock-comparison network design (TWSTFT, optical fibre links, GNSS common-view, ensemble-time algorithms such as NIST AT1).
**Manuscript reviewed:** [`docs/manuscript.md`](manuscript.md) at commit prior to v1.0-tech-report tag.
**Outcome:** manuscript revised in [commit pending] to incorporate the reader's findings as new sections (§§ 2.6, 4.4.1, 5.5.1) and as targeted edits to §§ 5.1, 5.5, 5.6, references, and Acknowledgements.

This file records the reader's findings verbatim so that the revision history is traceable. The associated revision is summarised in CHANGELOG `[0.8.5]`.

---

## Findings (reader's wording, abridged)

### 1. The Clock Model: Oversimplification That Matters

**1.1 White-noise-only residuals at σ = 1.0.** Real clocks display flicker FM (τ⁻¹ Allan deviation) at 1–100 s, random-walk FM (τ⁻¹/²) at longer times, strongly coloured noise from environmental sensitivity, and dead time / asynchronous measurement in TWSTFT and optical-fibre links. The choice of white noise changes the structure of the optimal estimator: under flicker FM the sample variance does not converge, the independent-reading pooling argument is qualitatively wrong (readings are not independent at any timescale), and effective *k*_eff is a count of *decorrelated* samples, not just neighbours. Recommendation: paragraph in § 2.1 / § 5.1.2 acknowledging this.

**1.2 "One clock degraded (3× noise)".** Real outlier processes are phase steps (fibre-link jumps), frequency offsets (GPS-disciplined maser losing lock), intermittent outliers (TWSTFT multipath, optical-comb cycle slips), and structured drift (aging, temperature coefficients). A 3× σ inflation treats all of these as a single Gaussian inflation. This is why `freq_exclude` performs so well: in a Gaussian world, dropping the noisiest 10 % is near-optimal. The simulation may be **under-rewarding** the ADMEC design.

### 2. The Delay Model

**2.1 Poisson delays.** Reasonable for packet-switched Ethernet or irregularly-scheduled TWSTFT; unreasonable for dedicated optical-fibre links (deterministic, sub-microsecond), TWSTFT (stable bulk delay ~250 ms with occasional dropouts), or GNSS common-view (delay dominated by ionospheric variability). Real networks also have asymmetric delays at the nanosecond level relevant to optical clocks.

**2.2 Stale-vs-drop.** Stale mode is a primitive version of what Kalman-filter-based ensemble clocks do (NIST AT1: propagate each clock's state forward with its own model, and use the propagated states in the ensemble average). The manuscript's stale mode reads `Y[t − delay, j]` without forward-propagating *j*'s state. Recommendation: add a baseline that propagates delayed readings with a simple clock model (e.g. random-walk frequency for masers).

### 3. The "Centralised" Baseline

**3.1 `freq_global` is omniscient, not centralised.** No real network has a central node that sees all readings instantaneously; even BIPM's UTC is post-processing over weeks. The "centralised" baselines in § 3 are *omniscient* baselines. The *N* / *k*_eff reference is the gap to an idealisation; against a delayed-centralised aggregator the real gap is smaller. Recommendation: add a delayed-centralised baseline.

**3.2 Why do `bocpd` and `imm` perform so poorly?** A well-tuned IMM or BOCPD should dominate simple exclusion on scenarios with structured drift (S6, S8). Possible explanations: filter banks mis-tuned for the white-noise model (process-noise covariance too high), changepoint prior mismatched to signal rate, mode-transition matrix assuming too-frequent switching. Without a parameter-sensitivity check for the baselines, the reader cannot tell whether ADMEC is losing to a strong baseline or a poorly-tuned one. Recommendation: brief note on baseline tuning.

### 4. The IC Observable and the 2.976 bit Threshold

**4.1 IC vs Allan deviation.** In real clocks the null distribution is non-Gaussian (heavy tails from flicker; intermittent outliers). The mixture model fitted to all readings is contaminated by the anomalies it should detect. Allan deviation is a second-difference statistic that naturally suppresses frequency drift and is the lingua franca of the field. A practitioner will ask: "Why not just use a three-sample Allan deviation as the anomaly detector?"

**4.2 5 % FPR is operationally catastrophic.** Real ensemble algorithms (NIST AT1) typically operate at FPR < 0.1 % because every false exclusion degrades ensemble stability. The "matched-threshold wins" at 1.5 bit are wins in a regime no practitioner would deploy. Recommendation: report empirical FPR at each tested threshold.

### 5. Three-Way Classification

**5.1 STRUCTURED-as-drift-estimated, not just excluded.** In real timekeeping, a clock showing structured drift is *not excluded*: AT1 estimates a frequency-drift coefficient per clock and uses it to steer the ensemble. ADMEC's "exclude STRUCTURED" is the *opposite* of best practice. The follow-up redesign (§ 5.6) should be "STRUCTURED with reduced weight + drift estimation."

**5.2 Fold bifurcation (S8) is physically unmotivated.** Optical clocks do not bifurcate; they lock or they don't. Masers exhibit mode jumps, but these are discrete events. The critical-slowing-down literature is compelling for ecosystems and climate but tenuous for atomic clocks. Replace S8 with a physically-motivated scenario: intermittent GPS-disciplining loss, or thermal runaway with a thermal time constant.

### 6. Metrics

**6.1 MSE against zero is not the right figure of merit.** The absolute phase or frequency of an ensemble is not knowable; what matters is *ensemble stability* (Allan deviation at τ = 1 day) and *steering noise*. A local consensus that introduces high-frequency jitter may have low MSE but poor stability at long τ. Recommendation: add modified Allan deviation or TDEV on consensus residuals.

**6.2 Structure correlation needs a physical interpretation.** For a stable reference, low correlation is desirable (anomaly suppressed). For a tracking application (steering a maser to an optical clock), high correlation in the consensus is desirable.

### 7. The Topological Claim

**7.1 *N* / *k*_eff for memory-using estimators.** The claim that "no amount of classifier or constraint tuning crosses that bound" is not demonstrated for estimators that use temporal memory. A node with *k*_eff = 4 that integrates with forgetting factor λ effectively pools over *k*_eff / (1 − λ) historical readings, not 4. The manuscript's `imm` and `bocpd` carry temporal state but underperform `freq_exclude`, suggesting their memory is poorly tuned, not that temporal pooling is ineffective. Recommendation: tone down to "no static, memoryless tuning crosses the bound".

**7.2 Stale mode is already temporal pooling.** This undermines the bound's tightness. The reference is *N* / *k*_eff for the *spatial* pool with a separate term for the *temporal* pool.

### 8. Operational Recommendations

Add: clock-model propagation; outlier logbook (STRUCTURED stream for operator diagnosis); adaptive thresholds based on current ensemble stability (cf. NIST AT1 expected-variance flagging).

### 9. Minor Issues

- Allan 1966 cited but never used.
- Lisdat 2016 cited but the optical-clock-network connection is not made.
- "Degraded clock (3× noise)" not a realistic failure mode for masers or optical clocks; realistic would be 1 × 10⁻¹⁵ frequency offset or 1 ns phase step.

### Summary table (reader's priority ranking)

| Priority | Issue | Suggested action |
|----------|-------|------------------|
| **High** | White-noise baseline ignores flicker FM | Caveat in § 5.1.2 (real clocks tighten the bound) |
| **High** | `freq_global` is omniscient, not centralised | Add delayed-centralised baseline for fair comparison |
| **High** | 5 % FPR is unrealistically high for timekeeping | Report FPR at each threshold; contextualise wins at 1.5 bit |
| **Medium** | S8 (fold bifurcation) is physically unmotivated | Replace with intermittent GPS loss or thermal runaway |
| **Medium** | STRUCTURED should be drift-estimated, not just excluded | Reframe § 5.6 redesign (a) |
| **Medium** | Missing standard metric (Allan deviation / TDEV) | Add modified Allan deviation on consensus residuals |
| **Low** | Baseline tuning unexplained | Add parameter-sensitivity note or tuning justification |

> "The manuscript is a solid characterisation study with a strong methodological backbone. Its main weakness is that it is **too pure-mathematics and not enough metrology**. Bringing it into closer contact with the physical reality of clock networks — flicker noise, real delay asymmetries, standard stability metrics, and operational outlier-handling practice — would make the negative results more credible and the positive findings more actionable."

---

## Disposition (what the manuscript revision did)

| Reader item | Manuscript response | Where in manuscript |
|-------------|---------------------|---------------------|
| 1.1 white-noise / 1.2 3× σ failure mode / 2.1 Poisson delays / 3.1 omniscient centraliser / 6.1 MSE-vs-stability | New § 2.6 "Scope and limitations vis-à-vis real clock networks" with a five-row table mapping each simplification to the real-network reality and the implication for the manuscript's claims | new § 2.6 |
| 4.2 operational FPR | New § 4.4.1 "Operational cost of the low-threshold wins" with empirical FPR per threshold from a new null-only run on S4 / S5 (`scripts/wp3_threshold_fpr_check.py`, `data/wp3_threshold_null_fpr_20260505.npz`) | new § 4.4.1 |
| 5.1 STRUCTURED-as-drift-estimated | § 5.6 redesign (a) reframed: "STRUCTURED with reduced weight + drift parameter estimated and contributed back" | § 5.6 |
| 2.2 stale-without-propagation / 7.1 memory-using estimators | § 5.6 redesign (b) reframed: "Decayed-staleness weighting *with state propagation*"; § 5.1 caveat added that the heuristic is for static memoryless estimators; § 5.5.1 added with deployment-grade refinements | §§ 5.1, 5.5.1, 5.6 |
| 5.5 operational recommendations: AT1-style propagation, outlier logbook, FPR coupling | § 5.5 recommendations rewritten with the FPR redline, the propagation caveat, and the STRUCTURED-logbook recommendation | § 5.5 |
| 9 references | Allan 1966 and Lisdat 2016 references annotated to flag what the manuscript does *not* do | Section 8 |
| Atlas-integrity provenance | Acknowledgements section now records the reader pass | Statements |
| 2.2 Kalman-style baseline / 3.2 baseline-tuning sensitivity / 5.2 S8 replacement / 6.1 Allan deviation / 6.2 structure-correlation interpretation | Reserved for follow-up project (the redesigns of § 5.6 are the natural home; pre-registration against a tuned random-walk-FM Kalman baseline is part of that follow-up's scope) | § 5.6 |

The deferred items are explicitly listed in § 5.6 as part of the follow-up's pre-registration scope; they are not silently dropped.

---

## Second pass — code-vs-claim alignment review

A second domain-expert reading focused specifically on whether the manuscript's claims match what the code actually computes. The reader read [`docs/manuscript.md`](manuscript.md), [`analysis/docs/analytic_reference.md`](../analysis/docs/analytic_reference.md), the classifier and topology code, and made no edits.

### Findings (reader's wording, abridged)

**High — the "local" ADMEC classifier is not actually local/causal.** [`src/estimators.py:_classify_network_full`](../src/estimators.py) computes IC from the full same-time `Y[t, :]`, then local estimators consume those *global* labels. For real distributed clock networks this is an omniscient classifier unless every node already has the full same-epoch ensemble. The negative result still holds, but claims about same-step deployment / local causality should be caveated, or rerun with local / delayed IC.

**High — the *N* / *k*_eff language is internally inconsistent.** Some passages call it a lower bound / floor that cannot be crossed; Fig. 1 and § 5.1 treat it as an upper / reference line with points below it. Rewrite everywhere as a "static independent-pooling reference," not a bound, unless a bound is proved.

**High — clock-noise taxonomy in § 2.6 is wrong in Allan-deviation terms.** Flicker FM is *flat* in σ_y(τ); random-walk FM rises as τ^(+1/2); τ^(−1) is white PM; τ^(−1/2) is white FM. Also: temporal coloured noise within a clock does *not* by itself reduce spatial ensemble sample size — only spatial / common-mode correlation does.

**Medium — maser ensembles vs optical-clock comparison networks.** The manuscript still blurs two operationally different problems. Optical-clock networks bring dead time, maser flywheels, systematic uncertainty, relativistic / geopotential corrections, cycle slips, phase-stabilised link noise. Different from AT1-style ensemble steering.

**Medium — operational FPR redline.** Plausible engineering intuition but too absolute without citation. Make it a stated operational assumption or cite an ensemble-time source.

**Medium — lag ablation scope.** Rules out the specific self-reference lag test only. Does not prove "same-step IC is the right operating point" for a real delayed network because the same-step IC currently uses *global* same-time data.

**Low — consensus equation in § 4.3 omits self.** Static `adj` has False diagonal in [`src/network.py`](../src/network.py); estimator code adds self separately. Equation should use `{i} ∪ {j: adj[i, j] ...}`.

> Overall: "the negative ADMEC characterisation is credible, and the manuscript has become appropriately cautious. The remaining risk is overclaiming physical-clock relevance from a simplified, globally classified, point-MSE simulation."

### Disposition (second-pass)

| Reader item | Manuscript response | Where in manuscript |
|-------------|---------------------|---------------------|
| Global classifier vs local consensus | New first row in § 2.6 table making the hybrid status explicit; abstract scope-restricted with a paragraph flagging the partial-decentralisation; § 5.6 redesign list extended to three items, with item (iii) being "truly decentralised IC"; § 6 conclusion acknowledges the hybrid status; § 4.5 lag-ablation caveat acknowledges this is global-IC, not local-IC | abstract, §§ 2.6, 4.5, 5.6, 6 |
| Bound vs reference inconsistency | Introductory paragraph reworded to "places the local-to-centralised ratio approximately at *N* / *k*_eff under static, memoryless aggregation"; § 5.1.2 calls it "approximate-value argument under the independent-reading null, not a one-sided bound"; § 5.1.5 removed "floor" and "cannot exceed"; § 5.6 close-out says the reference captures the static-memoryless prediction, not a derived limit | §§ 1, 5.1, 5.6, 6 |
| Allan-deviation noise-taxonomy errors | § 2.6 row 2 rewritten with the correct σ_y(τ) hierarchy (white PM ∝ τ^{−1}, white FM ∝ τ^{−1/2}, flicker FM flat in τ, random-walk FM ∝ τ^{+1/2}). Implication revised: it is *common-mode* (cross-clock) correlation that strengthens the pooling argument, not within-clock temporal colour | § 2.6 |
| Maser vs optical-clock distinction | New paragraph after § 2.6 table clarifying that the manuscript's findings are closer to the maser-ensemble problem and *not directly applicable* to optical-clock comparison networks, which involve dead time / flywheels / geopotential corrections / cycle slips / phase-stabilised links | § 2.6 |
| FPR redline citation | New paragraph after § 2.6 table marking the "FPR > 1 % borderline / > 5 % unacceptable" figures explicitly as engineering rules of thumb, *not* derived bounds; deployment-specific tolerable FPR depends on steering-loop bandwidth, ensemble size, false-exclusion cost | § 2.6 |
| Lag ablation scope | Forward-reference at § 4.5 head adds a caveat that this tests global-IC vs global-IC-shifted; truly local IC's lag dependence is not characterised here | § 4.5 |
| Consensus-equation self-inclusion | Equation in § 4.3 corrected to `({i} ∪ {j : adj[i, j] ∧ delay-accessible}) ∩ {j : mode == STABLE}` with a parenthetical explaining the convention | § 4.3 |

This second pass surfaces no items that require new simulations; all eight findings are addressed by edits to the manuscript prose and the equation. The negative ADMEC characterisation (DG-2 / DG-2b / DG-3 NOT MET) is unchanged, but the manuscript no longer overclaims architectural locality, terminological consistency, or noise-taxonomy correctness.

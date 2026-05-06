---
title: "Projektantrag — ADM-EC Clock Consensus Phase 2"
subtitle: "Maser- and optical-clock-network redesign campaign with topological-pooling-reference baseline"
author: "Ulrich Warring (Physikalisches Institut, Albert-Ludwigs-Universität Freiburg)"
status: "Draft v0.2 — pending Ledger-identifier confirmation and Handbook §7 initialisation"
date_drafted: "2026-05-06"
canonical_repo: "threehouse-plus-ec/admec-clock-consensus"
phase_namespace: "p2_*"
ledger_entry: "CL-2026-006 (proposed; assignment deferred to v1.0 freeze)"
handbook_anchor: "Handbook §7 Statistical Methodology (create-if-absent provision below)"
primary_audience: "External collaborators in metrology, statistical signal analysis, and distributed timing systems"
---

# Projektantrag — ADM-EC Clock Consensus Phase 2

> *Delay-constrained anomaly-aware consensus in heterogeneous clock networks: a redesign campaign on the topological pooling-reference baseline established in Phase 1.*

---

## 0a. Phase-2 in plain language

When networked clocks — atomic clocks, hydrogen masers, optical frequency standards — need to agree on a common time reference without a single central authority, each clock must combine readings from its neighbours and decide what consensus value to use. Some neighbour readings are noisy; some carry information about real drift or near-instability that should not simply be averaged away. The challenge is to build a local consensus rule that filters noise but preserves information.

Phase 1 of this programme tested one such rule on simulated networks. The main finding was simple and somewhat sobering: the dominant constraint on local consensus quality is not the cleverness of the rule, but the *amount of information each clock can reach* given the network topology and the message delays. A rule running on a sparse, high-delay network sees only a small fraction of the available data; no amount of statistical sophistication can recover information that does not arrive. This topology-access effect was characterised quantitatively in Phase 1 and is treated in Phase 2 as an external constraint, not as a result to overturn.

**Phase 2 asks a narrower question:** given that topology-access remains binding, can we use the delay-accessible data more efficiently? Two redesigns of the consensus rule are tested:

1. One that gives partial weight to readings flagged as carrying *structured* anomalies (rather than excluding them outright).
2. One that decays the weight of older readings smoothly with their delay (rather than choosing sharply between "use" and "drop").

Each redesign is tested independently before any combined version is considered.

**To make the test honest:**

- Realistic clock-noise families (white, flicker, and random-walk frequency modulation, plus broader power-law noise) are added to the previous Gaussian-only test set.
- Two metrology-anchored network scenarios are introduced — a long fibre chain and a hub-and-spoke comparator — alongside the abstract scenarios from Phase 1.
- The noise-detection threshold from Phase 1 is recalibrated for each new noise family *before* any redesign is tested. This recalibration is itself a published step, with explicit logic for what to do if the new noise families turn out to require not just a new threshold value but a different detection model entirely.
- Allan deviation, modified Allan deviation, and time deviation are reported as standard diagnostic figures alongside mean-squared error (MSE), but MSE remains the decision criterion. Allan figures characterise *what kind* of noise the consensus passes through; they do not by themselves determine whether a redesign succeeds.
- Each redesign must improve performance on at least one realistic scenario *without* significantly worsening performance on others — a Pareto-locality requirement that prevents narrow-regime overfitting.

**Honest negative results are anticipated.** If neither redesign closes a meaningful portion of the topological gap, the programme reports that finding directly: topology-access is the binding constraint regardless of consensus-rule sophistication, and the Phase-1 result stands stronger as a consequence. This outcome is publishable and is not treated as a project failure.

The remainder of this Projektantrag formalises these decisions: which noise families are included, which scenarios are tested, what statistical machinery is used for recalibration, what counts as success or failure for each redesign, and how reproducibility of the simulation campaign is guaranteed. The internal governance machinery (standing vetoes, decision gates, pre-registration registry) exists to prevent Phase-2 conclusions from drifting under the pressure of any single result. Readers unfamiliar with that vocabulary may consult the glossary in **Appendix C**.

---

## Endorsement Marker

This Projektantrag is a Coastline-shaped document under Open-Science Harbour template v2.0.

> *Externally endorsed = cited but not replicated; harbour-internal coastlines = our own results treated as constraints; Sail = framing only, not tested.*

**Externally endorsed (citation-only, not replicated):**

- IEEE Standard 1139-2008 / 1139-2022 — frequency-stability noise taxonomy (white, flicker, random-walk; phase and frequency variants).
- Allan, Mod-Allan, TDEV definitions (Allan 1966; Sullivan, Allan, Howe & Walls 1990).
- Bayesian online change-point detection (Adams & MacKay 2007); Interacting Multiple Model filter (Blom & Bar-Shalom 1988); Huber M-estimator (Huber 1981).
- Power-law-noise discrete-time generation (Kasdin 1995).
- Optical-clock-network operational regime (Lisdat et al. 2016; Bothwell et al. 2022).
- UTC / TAI weighting and steering (Panfilo & Arias 2019).

**Harbour-internal coastlines (referenced as constraints):**

- Phase-1 manuscript: *A Topological Information-Pooling Reference for Local Clock Consensus* (this repository, `docs/manuscript.md`). The §5.1 *N* / *k*_eff topological pooling reference is inherited as a regime-locating baseline on this study, not re-tested.
- CL-2026-002 *Topological Thesis* (design isomorphism, not ontology) — invoked under the lock / key discipline (§1).

**Sail (framing only, no decision gate):**

- *Causal Clock Unification Framework* (Warring 2026, Zenodo DOI 10.5281/zenodo.17948436). The η = L_comparison / (cτ) parametrisation is used as scenario-locating language in §7. **Phase 2 does not test CCUF.** Any wording in this document or its outputs that promotes CCUF from framing to load-bearing claim is out of scope and triggers the standing veto (§4).

**Novel boundaries (falsifiable, versioned in this Projektantrag):**

- Two architectural redesigns of the local consensus update rule (WP-γ, WP-δ) and their combination (WP-ε).
- Per-noise-family IC threshold recalibration with three-tier escalation logic (WP-α₀).
- STRUCTURED-channel separability validation as redesign prerequisite (WP-α).
- Cramér–Rao floors per scenario (WP-β).
- Two metrology-anchored scenarios (S9 fibre chain, S10 hub-and-spoke).
- Pareto-locality compliance as a binding evaluation criterion on every redesign decision gate.

---

## 0. Status & Provenance

Phase 2 of the ADM-EC Clock Consensus programme. Same repository, `p2_*` archive namespace, **strictly additive separation from Phase-1 archives** (no migration, no overwrite). Continuity scenarios re-run under Phase 2 produce `p2_continuity_*.npz` distinct from `wp2_*` originals so harness drift is detectable by direct comparison.

The Phase-1 manuscript reports DG-2 NOT MET at the pre-registered operating point and identifies the binding constraint as topological access to information rather than estimator sophistication. Phase 2 evaluates two redesigns of the consensus update rule that aim to use delay-accessible data more efficiently. **The redesigns are evaluated by how they move local consensus relative to the *N* / *k*_eff reference line, not by treating that heuristic as a pass/fail criterion.**

---

## 1. Inheritances from Phase 1 (Locks)

The following are not re-tested in Phase 2. They are external constraints on every WP design and reporting decision.

1. **Topological pooling-reference baseline.** The local-to-centralised MSE ratio empirically tracks the static independent-reading reference *N* / *k*_eff, with corrections in two directions (signal correlation, temporal pooling from staleness). WP-β annotates this heuristic against a per-scenario Cramér–Rao floor.
2. **IC observable definition.** Per-reading information content as defined in Phase-1 logbook entries 001–006. The *value* of the threshold is a Phase-2 variable (key); the *definition* of the observable is a lock.
3. **Simulation-harness signature.** `(Y, Sigmas, adj, delays, **kwargs) → Estimates(T, N)`. Any new estimator in Phase 2 implements this signature.
4. **Parameters-layer SI mapping.** Abstract σ-units inside the harness; SI mapping at the reporting layer. Direct heir of the `single_25Mg-plus` parameters.py contract.
5. **Canonical scenario set S1–S8.** Re-run as continuity anchors; not modified.

## 2. Phase-2 Variables (Keys)

The following are subject to design choices within this Projektantrag.

1. Consensus-rule redesigns (α-rule and λ-rule; WP-γ and WP-δ).
2. Weighting schemes (continuous-treatment of STRUCTURED; staleness-decay).
3. **Per-noise-family IC threshold values** (recalibrated in WP-α₀; one per ratified family).
4. τ-grid resolution beyond the named anchors (§6).
5. Per-scenario hyperparameters (S9 link distribution, S10 hub stability tier).

---

## 3. Reporting Clause (frozen)

> **Phase-2 Reporting Clause.**
>
> 1. **MSE governs decision gates.** All DG-α₀ through DG-ε are stated and evaluated on MSE.
> 2. **Allan-family observables (σ_y(τ), Mod-σ_y(τ), TDEV) are mandatory diagnostic auxiliaries.** Every output table reports them at the named τ-anchors falling inside the scenario *T* window.
> 3. **Paired-headline rule.** Every reported gain figure on MSE pairs with the residual *N* / *k*_eff gap (or the WP-β Cramér–Rao gap, once available) at the same operating point, on the same line.
> 4. **Allan-family observables are diagnostic, not governing.** They may motivate future redesign of the governing observable, but cannot retroactively govern a completed campaign.
> 5. **Diagnostic stays diagnostic; the decision observable stays the decision observable.**

---

## 4. Veto Inventory (Phase-2 standing list)

| Status | Veto | Citation |
|---|---|---|
| ARCHIVED | Silent LOCAL_CANDIDATE promotion | satisfied by Guardian explicit-tag ratification (§5) |
| STANDING | Post-hoc Allan reinterpretation of MSE-based decision gates | Violation of Clarity |
| STANDING | Infrastructure-fidelity wording from scenario mnemonics ("models the European fibre network", etc.) | Violation of Clarity |
| STANDING | Promotion of CCUF (Endorsement Marker Sail) from framing to load-bearing Coastline within Phase 2 | Violation of Clarity |
| STANDING | Bundling WP-γ and WP-δ before each passes its independent gate | Violation of Structure |
| STANDING | Reuse of Phase-1 decision-gate identifiers (DG-2 / DG-2b / DG-3) for Phase-2 gates | Violation of Clarity |
| STANDING | Citation of EXPLORATORY-tagged results (§8.4.5) as evidence for DG passage, threshold validity, or estimator robustness | Violation of Clarity |
| STANDING | Narrow-regime overfitting in any redesign WP — gain on one scenario reported without the Pareto-locality compliance check (§§8.4–8.6) across the full S1–S10 set | Violation of Clarity |

---

## 5. Noise-Family Interface

Per-node tagged-tuple `NoiseSpec`, additive over independent draws.

### 5.1 Canonical (endorsed) families

```
("white",        sigma)
("flicker_fm",   h_minus_1)            # Kasdin–Walter generator
("rw_fm",        h_minus_2)
("power_law",    {0: h_0, -1: h_-1, -2: h_-2, -3: h_-3, -4: h_-4})
```

These four are Phase-2 calibration targets. WP-α₀ produces a recalibrated IC threshold per family.

### 5.2 LOCAL_CANDIDATE families (no parity implied)

```
("student_t",    df, sigma)            # heavy-tailed link noise (exploratory)
("burst",        lambda_rate, sigma_burst)  # phase glitch / cycle-slip stress (exploratory)
```

**LOCAL_CANDIDATE marker (mandatory wherever these are referenced):**

> *No parity with endorsed metrological clock-noise families implied. These are exploratory stress-test injectors, not endorsed physical models of any specific clock technology unless separately justified in a scenario document. Any result materially dependent on these families states that dependence explicitly in the scenario-level reporting layer.*

LOCAL_CANDIDATE families do **not** enter WP-α₀ calibration scope (§8.1). They appear only in dedicated stress-test sweeps within WP-γ / WP-δ and are reported with the marker on every dependent figure.

### 5.3 Composition rule (bounded)

Phase-2 noise composition is **additive in fractional frequency**, applied per-node and per-step. Multiplicative or convolved noise (e.g. amplitude-modulated phase noise) is **out of scope** for Phase 2; it requires a separate convention-freeze decision rather than retrofit. The additive rule is bounded, not universal.

### 5.4 Per-node specification

Network-level noise is `noise_specs: list[NoiseSpec]` of length *N*, enabling heterogeneous-clock networks (S10 requirement). Homogeneous-network scenarios (S9, continuity S1–S8) populate `noise_specs` with a uniform entry.

---

## 6. Observable Layer

```
allan_dev(y, taus, dt)        -> ndarray   # σ_y(τ)
mod_allan_dev(y, taus, dt)    -> ndarray   # Mod-σ_y(τ)
tdev(y, taus, dt)             -> ndarray   # τ · Mod-σ_y / √3
```

`y` = fractional-frequency residual, `(T, N)` array; routine returns `(N, len(taus))`.

**Canonical τ-grid:** log-spaced from *dt* to *T* / 4. **Named reporting anchors:** {10⁻³, 10⁻², 10⁻¹, 1, 10, 10², 10³, 10⁴} s after parameters-layer time-mapping.

### 6.1 Why these anchors

The named anchors span the operating decade of contemporary metrology comparators:

- **10⁻³–10⁻¹ s** is the short-term regime relevant to optical lattice clocks where individual servo cycles and laser-noise integration matter (Bothwell et al. 2022).
- **1–10² s** corresponds to typical lab integration windows for both optical and microwave standards.
- **10³–10⁴ s** is the long-term regime relevant to hydrogen masers and Lisdat-style fibre-network averaging (Lisdat et al. 2016).

Per-scenario tables report the subset of anchors falling inside the scenario *T* window with the others marked `n/a`. Optical-regime scenarios may extend the grid below 10⁻³ s under a parameters-layer time-mapping declaration; this does not require Projektantrag amendment.

### 6.2 Implementation intent

`allantools` v2024.x is the intended implementation, subject to code audit during the WP-α₀ harness build. Deviation from this choice (alternative library or in-house re-implementation) requires a convention-freeze amendment with regression-test verification against the previous reference output.

---

## 7. Scenarios

### 7.1 Scenario-semantics discipline (frozen)

> **Scenario labels are analogy labels, not representational claims.** "Sr–Sr-like", "TWSTFT-like", "H-maser-like", "fibre chain", "hub-and-spoke" denote parameter-regime inspiration only. They do not imply validated infrastructure fidelity. The harness maps behavioural regimes, not operational facilities.

This rule applies wherever scenarios are described in any Phase-2 output.

### 7.2 Continuity scenarios

S1–S8 from Phase 1, re-run unchanged. Archives in `p2_continuity_*.npz`. Direct comparison against `wp2_*` originals is the harness-drift sanity check.

### 7.3 New metrology-anchored scenarios

| ID | N | Topology | Per-hop delay | Noise (per node) | Inspiration | η anchor (derived) |
|---|---|---|---|---|---|---|
| **S9** | 10 | linear chain | 1–10 ms (Gaussian, mean 5 ms) | power-law FM, H-maser-like coefficients | continental fibre comparison | ~10⁻⁵ |
| **S10** | 12 | hub-and-spoke (1 hub + 11) | hub <1 ms; spoke 100 ms | hub: optical-like; spokes: Cs-ensemble-like | hierarchical comparator | ~10⁻³ |

**Concrete LOCAL_CANDIDATE example (S9 illustration).** S9 is parametrised with H-maser-like noise coefficients drawn from the IEEE 1139 envelope; no fidelity claim to any specific clock or fibre installation is made or implied. The "continental fibre comparison" label denotes the parameter regime (link length scale, dominant noise process, agreement-interval order of magnitude), not any particular operational network.

### 7.4 η anchors are derived, not target

η anchors above are *expected ranges* given typical link length, signal velocity, and required-agreement-interval values. The harness validation requires the *measured* η at runtime to match the parameters-layer mapped η to within the documented tolerance (§7.5). Mismatch flags a parameters-layer bug.

### 7.5 η tolerance with covariance audit

η tolerance is propagated from parameters-layer uncertainties (link length, signal velocity, agreement interval).

> **Covariance audit (mandatory).** If parameters-layer tolerances are correlated — e.g. fibre link length and signal velocity sharing a temperature dependence — propagate via full covariance matrix or worst-case bound. **Independent-quadrature propagation is not the default; it is a result of a covariance audit that found independence.**
>
> **Safety-margin clause.** If the covariance audit finds material coupling, the η-tolerance widens to the worst-case bound (not the quadrature-correlated estimate). Independent-quadrature propagation applies only after explicit independence finding.

S9 must declare its temperature-dependence assumption explicitly. S10 link-budget independence is plausible (heterogeneous link technologies) but requires the same explicit audit statement.

---

## 8. Work Packages — sequential gating

Sequential order is **gated**, not advisory. Each WP must close before the next opens. WP-ε is unique: it requires WP-γ *and* WP-δ to pass independent gates first.

### 8.1 WP-α₀ — IC threshold recalibration

**Question.** Does the IC observable threshold transfer from the Phase-1 Gaussian-null calibration to the four Phase-2 canonical noise families, or does the calibration regime change?

**Scope.** Four ratified canonical families only (white, flicker_fm, rw_fm, power_law). LOCAL_CANDIDATE families excluded from calibration scope (§5.2).

**Method (reference: Handbook §7).**

- Generate per-reading IC distributions under each family by Monte Carlo simulation (replicate count *R* frozen in §10, RNG protocol per §10).
- Compare per-family null distribution to Gaussian-null reference by Anderson–Darling test on Monte-Carlo-generated null distribution (*not* asymptotic critical values; estimated parameters invalidate them).
- Report worst-case-σ 95th-percentile threshold per family (analogous to Phase-1 entry-006 calibration).

**Three-tier outcome (Guardian-frozen).**

| Tier | Trigger | Action |
|---|---|---|
| **T1 — Shift only** | distribution location shifts; shape compatible with Gaussian-null within both materiality thresholds | same estimator family; per-family threshold update; in-chart recalibration |
| **T2 — Shape change with stable ordering** | shape changes (one or both materiality thresholds triggered) but per-reading rank ordering of suspicious vs nominal readings is preserved within a documented Spearman-ρ floor | estimator family survives; calibration *model* changes (e.g. quantile-based threshold replaces single-σ rule); WP-α₀ extends with sub-task |
| **T3 — Ordering instability / discriminatory collapse** | rank ordering of suspicious vs nominal readings does not survive the noise-family change | true estimator-family challenge; **chart-transition triggered** (§8.1.3) |

#### 8.1.1 Dual materiality threshold for T1 vs T2

Shape-change is declared if **both** of the following trigger:

- Statistical: Monte-Carlo-derived AD-test p-value below pre-registered α (suggested α = 0.01).
- Effect-size: Kolmogorov distance Δ_max > 0.05 **or** tail-ratio deviation > 20 % at the 95th-percentile reference.

If exactly one triggers, WP-α₀ produces a sensitivity-analysis appendix documenting the deviation magnitude and direction; threshold is reported with a caveat range, not a single point. This is the operational definition of "in-chart recalibration with caveat".

**Verbal justification of the numerical choices.**

- *α = 0.01* is chosen for low false-escalation rate at *R* = 10⁴ (§10); it leaves room for genuine shape changes to be detected without amplifying small statistical fluctuations into false chart transitions.
- *Δ_max = 0.05* reflects insensitivity to bulk CDF perturbations below 5 %, which would not materially affect threshold-setting at the 95th-percentile operating point.
- *Tail-ratio 20 %* targets 95th-percentile divergence directly — the regime where threshold values are actually set — rather than penalising distribution-bulk differences.
- *Spearman-ρ ≥ 0.85* (§8.1.2) leaves room for noise-family-induced rank shuffling without permitting full discriminatory collapse.

These four numbers are pre-registered. Empirical tuning during WP-α₀ campaign requires a convention-freeze amendment with documented rationale.

#### 8.1.2 T2 vs T3 ordering check

Spearman-ρ between per-reading IC ranks under the family in question and under the Gaussian-null reference, on a paired Monte-Carlo draw. Floor: **ρ ≥ 0.85** (pre-registered).

#### 8.1.3 Chart-transition triad — available at trigger point

If T3 triggers, the transition map is produced **at the moment of escalation**, not deferred to the WP-α₀ closing report:

- *Invariant preserved.* Typically the IC observable definition itself.
- *Transformed representation.* The threshold value, the calibration model class, or — in the strongest case — the estimator family.
- *Information gained / lost.* Which noise regime the original calibration was implicitly specific to; what discriminating information the original estimator family is unable to use under the new regime.

The triad enters the Phase-2 deliberation log at the transition moment and is mirrored in the WP-α₀ closing report.

#### 8.1.4 Decision gate — DG-α₀

> **DG-α₀.** WP-α₀ closes when each of the four canonical families has either (a) a recalibrated threshold under T1 or T2, **or** (b) a chart-transition triad logged under T3 with explicit guidance on which downstream WPs the transition affects.

### 8.2 WP-α — STRUCTURED-channel separability

**Question.** Do the temporal-statistic gates (var_slope, lag-1 ACF; calibrated in Phase-1 entry 004) reliably separate STRUCTURED from UNSTRUCTURED anomalies on signal types beyond the fold-bifurcation regime they were tuned for?

**Scope.** Continuity scenarios S1, S3, S6, S7, S8 (signal-bearing). Strict-STRUCTURED TPR computed against designer-injected ground truth. Joint with the Phase-1 0.7 % strict TPR result as the baseline.

#### 8.2.1 Decision gate — DG-α

> **DG-α.** Strict-STRUCTURED TPR ≥ 50 % across S1, S3, S6, S7, S8 at matched threshold (per WP-α₀). FPR ≤ 5 %.

**Failure disposition.** If DG-α fails, the main path of WP-γ does **not** open (the redesign that consumes STRUCTURED would otherwise be built on a noisy label). Failure of DG-α is itself a publishable result: *the Phase-1 entry-004 temporal-gate calibration does not generalise beyond critical-slowing-down dynamics.* WP-δ may proceed independently. WP-γ-lite (§8.4.5) is permitted as a separately-tagged exploratory channel.

### 8.3 WP-β — Cramér–Rao floor per scenario

**Question.** Replace the Phase-1 §5.1 heuristic *N* / *k*_eff reference with a per-scenario Cramér–Rao bound under the Phase-2 noise families.

**Scope.** All ten scenarios (S1–S10) under the four canonical families. Bound computed analytically where tractable, by score-function Monte Carlo where not.

#### 8.3.1 Estimand and model specification

The Cramér–Rao floor is computed for the **minimum-variance unbiased estimator of the network-average fractional-frequency offset** (the canonical quantity Phase-1 MSE evaluates). The bound is derived under the **centralised omniscient model with full noise-family knowledge** — every reading from every clock at every step is available, and the noise-family parameters are known. This bound represents the theoretical floor for *any* unbiased estimator of the network-average offset given the underlying statistical model; it is **not** a constraint that follows from the local-graph structure.

Local-graph constraints (which readings each node can access, and at what staleness) enter Phase 2 as constraints on what information any local consensus can use. The gap between the local-consensus baseline and the centralised CR floor is therefore the well-defined "topological pooling gap" that WP-γ / WP-δ aim to narrow without expecting to close.

#### 8.3.2 Decision gate — DG-β

> **DG-β.** WP-β closes when each (scenario — family) cell has a documented Cramér–Rao floor with a stated assumption set, and the heuristic *N* / *k*_eff line in Phase-1 §5.1 is annotated against the bound at every point it appears in Phase-2 outputs.

**Failure disposition.** If WP-β cannot derive a tractable bound for some cells (e.g. heavy-tail families with intractable Fisher information), those cells retain the heuristic with explicit annotation; the failure is reported but not blocking for WP-γ / WP-δ.

### 8.4 WP-γ — α-rule (STRUCTURED with reduced weight)

**Question.** Does including STRUCTURED readings with continuous reduced weight α = 1 / (1 + IC_excess) close any portion of the *N* / *k*_eff gap on signal-rich delayed scenarios beyond the WP3 combined-tuned baseline?

**Scope.** Single axis: α-rule against WP3 combined-tuned baseline at matched threshold and matched delay convention. Continuity scenarios S1, S2, S3 plus new S9, S10. LOCAL_CANDIDATE noise sweep separately reported with marker per §5.2.

#### 8.4.1 Decision gate — DG-γ (Pareto-locality clause)

> **DG-γ.** The α-rule reduces MSE by ≥ 20 % over its matched baseline (`admec_full` without the α-rule) on at least one signal-rich scenario, **and** does not increase MSE by more than 10 % above the matched baseline on any other scenario in the Phase-2 set (S1–S10), at the same operating point. Both conditions must hold simultaneously.

Allan-family auxiliaries reported per §3 paired-headline rule; residual to Cramér–Rao floor (per WP-β) reported.

**Prerequisite.** DG-α PASS. (Without separable STRUCTURED labels, the main-path α-rule consumes noise.)

#### 8.4.5 WP-γ-lite (exploratory)

> **WP-γ-lite (exploratory).** If DG-α fails materially (TPR ≪ 50 % across all five scenarios), exploratory α-rule runs with looser STRUCTURED labels are permitted under explicit `EXPLORATORY` tag, parallel to LOCAL_CANDIDATE discipline. Tagged runs do not enter DG-γ evaluation. Findings are reported with the tag on every figure and table. **Exploratory-tagged results may generate future hypotheses but may not be cited as evidence for DG passage, threshold validity, or estimator robustness.** Looser STRUCTURED labels are documented with their relaxation parameters and treated as a separate label class throughout WP-γ-lite outputs.

### 8.5 WP-δ — λ-rule (decayed-staleness weighting)

**Question.** Does decayed-staleness weighting *w_j = exp(−λ τ_ij)* with λ ≈ 1 / τ_correlation close any portion of the *N* / *k*_eff gap beyond the WP3 stale-mode baseline?

**Scope.** Single axis: λ-rule against WP3 stale-mode `admec_full` baseline. Continuity scenarios + S9, S10. Includes a small staleness-vs-variance-trade-off mini-ablation to set the operating λ per scenario.

#### 8.5.1 Decision gate — DG-δ (Pareto-locality clause)

> **DG-δ.** The λ-rule reduces MSE by ≥ 20 % over its matched baseline (`admec_full` without the λ-rule, i.e. WP3 stale-mode without decayed weighting) on at least one signal-rich scenario, **and** does not increase MSE by more than 10 % above the matched baseline on any other scenario in the Phase-2 set (S1–S10), at the same operating point. Both conditions must hold simultaneously.

Allan-family auxiliaries reported per §3; residual to Cramér–Rao floor reported.

**Prerequisite.** DG-α₀ PASS or T2/T3 closure with downstream guidance. WP-δ does **not** require WP-α (the λ-rule does not depend on STRUCTURED labels).

### 8.6 WP-ε — combined α + λ

**Opens only if DG-γ PASS *and* DG-δ PASS.** No combined campaign without independent passes (Article III §3 standing veto, §4).

#### 8.6.1 Decision gate — DG-ε (paired-seed interaction-noise definition)

> **DG-ε.** Combined α + λ achieves
>
> *Δ_combined > max(Δ_γ, Δ_δ) + n_σ × SE(Δ_combined − max(Δ_γ, Δ_δ))*
>
> on at least one signal-rich scenario, where SE is the standard error of the per-seed paired difference across the 10-seed ensemble; *n_σ* = 2.0 pre-registered (one-sided ~95 %). The Pareto-locality clause applies: combined α + λ must not increase MSE by more than 10 % above the per-scenario better-of(γ-only, δ-only) baseline on any other scenario in the Phase-2 set.

#### 8.6.2 Sign convention

> Negative *Δ_MSE* denotes improvement relative to baseline. All DG-ε inequalities are evaluated after sign-normalisation into "improvement-positive" convention (i.e. *Δ* := −Δ_MSE so that larger *Δ* means better performance).

#### 8.6.3 What "interaction noise" means here

> **"Interaction noise" in DG-ε refers exclusively to uncertainty in the estimated interaction gain arising from finite Monte Carlo ensemble sampling, not to an additional physical noise process.** Specifically:
>
> - *Generative mechanism.* Seed-to-seed variability in the Monte Carlo campaign. Each seed produces an independent realisation of noise draws, signal-phase offsets, and delay distributions.
> - *Insertion layer.* Seed-aggregation step. Per-(scenario, seed, estimator) MSE values are produced by the harness; gain figures Δ_γ, Δ_δ, Δ_combined are computed per seed and then aggregated across the 10-seed ensemble.
> - *Observability pathway.* Standard error of the mean across seeds, computed *separately* for Δ_γ, Δ_δ, and Δ_combined, with the relevant SE for DG-ε computed on the **per-seed paired difference** *(Δ_combined — max(Δ_γ, Δ_δ))* (paired-t-style; not the difference of independent SEs — the seeds are matched).
> - *Expected covariance signature.* Under a null of "no synergistic interaction beyond additive", the per-seed paired difference clusters near *min(Δ_γ, Δ_δ)*; a genuine super-additive interaction shifts it upward by more than seed-noise allows.

---

## 9. Failure-disposition clause

> If neither DG-γ nor DG-δ narrows the *N* / *k*_eff residual gap on at least one signal-rich scenario at matched threshold and delay convention, the Phase-2 contribution is empirical confirmation that topological access is the binding constraint on local consensus regardless of consensus-rule sophistication. The §5.6 Sail of the Phase-1 manuscript is then closed; the §5.1 Coastline stands as the stronger result. This outcome is publishable and is not a project failure.

This clause descends directly from the Phase-1 Projektantrag's negative-result disposition.

---

## 10. RNG governance (frozen)

Monte Carlo calibration without RNG governance becomes irreproducible surprisingly quickly. The following are frozen for Phase 2:

1. **Generator family.** `numpy.random.default_rng` (PCG64). Any deviation requires a convention-freeze amendment.
2. **Seed derivation.** Master seed S₀ drawn from a cryptographically secure source (`secrets.randbits(64)`) at campaign start and logged. Per-stream seeds:
   ```
   S(family, replicate, scenario) = SHA-256(S₀ || family_name || str(replicate) || scenario_id)[:8]  → uint64
   ```
3. **Replicate count.** **Frozen at *R* = 10⁴ for WP-α₀ Monte Carlo null distributions** (pre-registered in this Projektantrag, not delegated to handbook). Replicate counts for WP-γ / WP-δ campaigns are scenario-dependent and pre-registered in the respective WP draft under the §3 paired-headline cost-benefit rule, with floor *R* ≥ 10² per (scenario, seed) cell.
4. **Parallelisation determinism.** Embarrassingly-parallel replicates are independent by seed derivation. Reduction (mean, percentile) is performed in pre-registered replicate-index order; no associativity-fragile parallel reductions.
5. **Software-stack pins.** numpy ≥ 2.0; Python `hashlib` SHA-256 (CPython reference implementation); endianness explicitly little-endian for cross-platform replay.
6. **Bit-identical replay mandate.** *On identical software stack (numpy version, hash library, OS endianness), Phase-2 calibration runs are bit-identical-replayable.* Software-stack drift requires re-running with archived original output for cross-check.

---

## 11. Pre-registration registry pattern (frozen)

Two-layer architecture:

- **Claim Analysis Ledger entry CL-2026-006** (proposed; *Integrator confirms against live registry state at v1.0 freeze*). Records: the WP-α₀ recalibration claim shape, the discriminant condition (T1 / T2 / T3 outcome), the feasibility flag, and outcome classification under Ledger v1.0-rc. Anti-aggregation discipline preserved: WP-α through WP-ε do **not** create new Ledger entries unless they themselves are claim-shaped; their methodology is captured in the handbook (below) and their outcomes in this Projektantrag's audit trail.

- **Handbook §7 Statistical Methodology** (create-if-absent provision). One-time chapter creation if §7 does not currently exist, via a one-line convention-freeze note referencing this Projektantrag as precedent. Contents:
  - Monte Carlo null generation procedure (AD-test under estimated parameters).
  - Dual materiality threshold (statistical α, effect-size Δ_max, tail-ratio bound).
  - Spearman-ρ ordering floor.
  - Cross-reference to RNG governance (§10 of this Projektantrag).

> **Boundary sentence (frozen).** *The handbook defines procedures; the Ledger records outcomes and discriminant conditions.* Methodology does not migrate into the Ledger; outcomes do not migrate into the handbook.

---

## 12. Decision-gate summary

| Gate | WP | Headline criterion | Pareto-locality | Prerequisite |
|---|---|---|---|---|
| DG-α₀ | WP-α₀ | Per-family recalibration or chart-transition triad logged | n/a | — |
| DG-α | WP-α | Strict-STRUCTURED TPR ≥ 50 %, FPR ≤ 5 % | n/a | DG-α₀ |
| DG-β | WP-β | Per-scenario CR floor or annotated heuristic | n/a | parallel to DG-α |
| DG-γ | WP-γ | ≥ 20 % MSE reduction on one signal-rich scenario | ≤ 10 % degradation elsewhere | DG-α PASS, DG-α₀ closed |
| DG-δ | WP-δ | ≥ 20 % MSE reduction on one signal-rich scenario | ≤ 10 % degradation elsewhere | DG-α₀ closed |
| DG-ε | WP-ε | Δ_combined > max(Δ_γ, Δ_δ) + 2 SE (paired) | ≤ 10 % degradation vs better-of(γ, δ) | DG-γ PASS *and* DG-δ PASS |

All gates evaluated on MSE per §3 Reporting Clause; Allan-family auxiliaries mandatory per §6; *N* / *k*_eff or Cramér–Rao gap paired on the same line per §3.

---

## 13. Handshakes outstanding

**To Integrator (this freeze).**

- Confirm CL-2026-006 against live Ledger state at v1.0 freeze, or assign next available identifier.
- Confirm Handbook §7 anchor exists at v1.0 freeze, or invoke create-if-absent provision.

**To Architect (after v1.0 freeze).**

- Open WP-α₀ draft against this specification; produce the Handbook §7 page in the same pass.

**To Guardian (continuous).**

- Re-engage at WP-α₀ campaign closure (before WP-α / WP-β open) to ratify any threshold-recalibration outcome.
- Re-engage at WP-γ closure and WP-δ closure (before WP-ε opens) to verify Pareto-locality compliance.
- Re-engage at WP-ε orthogonal-isolation check.

**To Scout (continuous).**

- Horizon scan during WP-α₀ campaign: T2 / T3 escalation likelihood, RNG-governance edge cases, covariance-audit findings on S9.

---

## 14. References (external coastlines, citation only)

1. Adams, R. P. & MacKay, D. J. C. (2007). Bayesian online changepoint detection. arXiv:0710.3742.
2. Allan, D. W. (1966). Statistics of atomic frequency standards. *Proc. IEEE* **54**, 221–230.
3. Anderson, T. W. & Darling, D. A. (1954). A test of goodness of fit. *J. Amer. Statist. Assoc.* **49**, 765–769.
4. Blom, H. A. P. & Bar-Shalom, Y. (1988). The interacting multiple model algorithm. *IEEE Trans. Automat. Contr.* **33**, 780–783.
5. Bothwell, T. et al. (2022). Resolving the gravitational redshift across a millimetre-scale atomic sample. *Nature* **602**, 420–424.
6. Huber, P. J. (1981). *Robust Statistics*. Wiley.
7. IEEE Std 1139-2008 / 1139-2022. Standard Definitions of Physical Quantities for Fundamental Frequency and Time Metrology.
8. Kasdin, N. J. (1995). Discrete simulation of colored noise and stochastic processes and 1/f^α power-law noise generation. *Proc. IEEE* **83**, 802–827.
9. Lilliefors, H. W. (1967). On the Kolmogorov–Smirnov test for normality with mean and variance unknown. *J. Amer. Statist. Assoc.* **62**, 399–402.
10. Lisdat, C. et al. (2016). A clock network for geodesy and fundamental science. *Nat. Commun.* **7**, 12443.
11. Panfilo, G. & Arias, F. (2019). The Coordinated Universal Time (UTC). *Metrologia* **56**, 042001.
12. Sullivan, D. B., Allan, D. W., Howe, D. A. & Walls, F. L. (1990). Characterization of clocks and oscillators. *NIST Technical Note* 1337.
13. Warring, U. (2026). *A Topological Information-Pooling Reference for Local Clock Consensus.* This repository, `docs/manuscript.md`.

---

## Appendix A — Phase-2 archive namespace

| Pattern | Contents |
|---|---|
| `data/p2_continuity_*.npz` | S1–S8 re-runs under Phase 2 (harness-drift sanity) |
| `data/p2_alpha0_*.npz` | WP-α₀ Monte Carlo null distributions per family |
| `data/p2_alpha_*.npz` | WP-α STRUCTURED separability diagnostic |
| `data/p2_beta_*.npz` | WP-β Cramér–Rao floors per (scenario, family) |
| `data/p2_gamma_*.npz` | WP-γ α-rule campaign |
| `data/p2_gamma_lite_*.npz` | WP-γ-lite EXPLORATORY runs (if triggered; tagged) |
| `data/p2_delta_*.npz` | WP-δ λ-rule campaign |
| `data/p2_epsilon_*.npz` | WP-ε combined campaign (only if γ + δ pass) |

Phase-1 archives (`data/wp1_*.npz`, `data/wp2_*.npz`, `data/wp3_*.npz`) are read-only artefacts in Phase 2.

**Harness-drift checksum.** Continuity-archive checksums against `wp2_*` originals are computed and logged on every `p2_continuity_*` run; checksum drift is a parameters-layer / RNG-governance bug, not a Phase-2 result.

---

## Appendix B — Versioning

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-05-06 | Initial draft from Council-3 deliberation closure. |
| v0.2 | 2026-05-06 | External-review + Architect/Guardian parallel-track integration. Frozen wordings: WP-γ-lite EXPLORATORY tag (§8.4.5); Pareto-locality clauses on DG-γ/δ/ε (§§8.4.1, 8.5.1, 8.6.1); paired-seed interaction-noise definition with sign convention and seed-vs-physical-noise distinction (§§§8.6.1–8.6.3). New: §0a plain-language overview; §6.1 τ-anchor regime motivation; §6.2 allantools intent; §7.5 covariance-audit safety-margin clause; §8.1.1 materiality-numbers verbal justification; §8.3.1 CR-floor estimand specification; §10 R = 10⁴ pre-registered, software-stack pins; Appendix A harness-drift checksum; Appendix C governance glossary; new STANDING vetoes on EXPLORATORY citation and narrow-regime overfitting (§4). |

**Minor-edit policy.** Edits between v0.1 and v1.0 not affecting decision-gate wording, scenario specifications, or RNG governance are permitted without re-deliberation. Edits affecting any of those three categories require Council closure before integration. Once v1.0 freezes (with CL-2026-006 assignment and Handbook §7 initialisation), all subsequent edits require an explicit amendment with documented rationale.

Next freeze gate: **v1.0 on Integrator confirmation of CL-2026-006 identifier and Handbook §7 anchor.**

---

## Appendix C — Governance glossary

For external readers unfamiliar with Open-Science Harbour vocabulary. Internal-council usage is unaffected.

- **Coastline.** A versioned, falsifiable framework document with mandatory Endorsement Marker, citing external constraints and declaring novel boundaries. This Projektantrag is a Coastline-shaped document.
- **Sail.** A framing or essay artefact; carries no decision gate. CCUF (Endorsement Marker) is a Sail in Phase 2.
- **Ledger (Claim Analysis Ledger).** A registry that classifies claims as COMPATIBLE / UNDERDETERMINED / INCONSISTENT under stated constraints. Phase 2 contributes one entry: CL-2026-006 (proposed) for WP-α₀ recalibration.
- **Handbook.** Reusable methodological reference. Procedures live here; outcomes do not. The Phase-2 statistical methodology lives at Handbook §7.
- **Endorsement Marker.** Mandatory first section of a Coastline document; declares external endorsements, harbour-internal constraints, framing-only Sails, and novel falsifiable boundaries.
- **Lock vs Key.** A *lock* is a stable concept inherited as a constraint (e.g. the IC observable definition); a *key* is a free interpretation parameter (e.g. the IC threshold value per noise family).
- **DG (Decision Gate).** A pre-registered, MSE-evaluated criterion with explicit pass / fail wording. Phase 2 has six: DG-α₀ through DG-ε.
- **LOCAL_CANDIDATE.** Tag for noise families included for exploratory stress-testing without parity to endorsed metrological models. Excluded from calibration scope.
- **EXPLORATORY.** Tag for WP-γ-lite runs under loosened STRUCTURED labels. Cannot be cited as DG evidence.
- **Paired-headline rule.** Every reported MSE-gain figure pairs with the residual *N* / *k*_eff (or Cramér–Rao) gap on the same line.
- **Chart transition.** A formal acknowledgement that an analytical chart (here: the calibrated estimator family) no longer adequately covers the operating regime. Not project failure; explicit re-charting protocol per Council-3 Constitution v0.4.
- **Pareto-locality clause.** Improvement on one scenario must not come at the cost of >10 % degradation on any other Phase-2 scenario at the same operating point. Prevents narrow-regime overfitting.
- **T1 / T2 / T3.** Three-tier WP-α₀ outcome: T1 location shift only (in-chart recalibration); T2 shape change with stable rank ordering (calibration model changes, estimator survives); T3 ordering instability (chart transition, estimator-family challenge).
- **Standing veto.** A persistent constraint on Phase-2 deliberations and outputs. The §4 inventory tracks active and archived vetoes; citing an archived veto re-opens it.

---

*This Projektantrag is itself a Coastline document under template v2.0. Its Endorsement Marker is binding on every Phase-2 output. Its standing vetoes (§4) are binding on every Phase-2 deliberation. Its Reporting Clause (§3) is binding on every Phase-2 figure.*

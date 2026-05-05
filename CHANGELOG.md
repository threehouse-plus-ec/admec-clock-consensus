# Changelog

All notable changes to this project will be documented in this file.

## [0.8.6] — 2026-05-05

### Atlas-integrity reader pass — second round (code-vs-claim alignment)

A second domain-expert reading focused on whether the manuscript's claims match what the code actually computes. Eight findings, all resolved via prose / equation edits (no new simulations needed). Reader pass recorded as an addendum in [`docs/atlas_integrity_reader_pass.md`](docs/atlas_integrity_reader_pass.md).

### Changed
- **`docs/manuscript.md` § 2.6**: new first row in the scope-and-limitations table: "The classifier is computed from the full same-time ensemble." This is operationally consequential — the local consensus rule consumes globally-computed STABLE / STRUCTURED / UNSTRUCTURED labels, so ADMEC as implemented here is *partially* decentralised, not fully so. A truly local IC redesign (each node computes its own IC over its delay-accessible readings only) is a follow-up redesign — see § 5.6 (iii).
- **`docs/manuscript.md` § 2.6 row on noise taxonomy**: corrected the σ_y(τ) hierarchy. White PM ∝ τ^{−1}; white FM ∝ τ^{−1/2}; flicker FM is **flat** in τ; random-walk FM ∝ τ^{+1/2}. Previous text had τ^{−1} for flicker FM (wrong) and τ^{−1/2} for random-walk FM (wrong sign). Implication updated: it is *common-mode* (cross-clock) correlation that would tighten the pooling argument, not within-clock temporal colour.
- **`docs/manuscript.md` § 2.6 closing paragraph**: now explicitly distinguishes maser-ensemble timescales (NIST AT1 etc.) from optical-clock comparison networks (Lisdat 2016, etc.); flags that the manuscript's findings are closer to the former and not directly applicable to the latter (dead time / flywheels / geopotential corrections / cycle slips / phase-stabilised links).
- **`docs/manuscript.md` § 2.6 closing paragraph**: marks the "FPR > 1 % borderline / > 5 % unacceptable" figures explicitly as engineering rules of thumb rather than derived bounds; deployment-specific tolerable FPR depends on steering-loop bandwidth, ensemble size, and false-exclusion cost.
- **`docs/manuscript.md` § 1 introduction**: reworded "no amount of classifier or constraint tuning crosses that bound" to "no static-memoryless tuning of the ADMEC family crosses this reference line in our scenarios"; explicitly identifies the reference as a heuristic, not a one-sided bound.
- **`docs/manuscript.md` § 4.3 consensus equation**: corrected to `({i} ∪ {j : adj[i, j] ∧ delay-accessible}) ∩ {j : mode == STABLE}` with parenthetical explaining that `adj` has a False diagonal in `src/network.py` and the estimator code adds self separately.
- **`docs/manuscript.md` § 4.5 head**: forward-reference now caveats that the lag ablation tests global-IC vs global-IC-shifted; the lag dependence of *truly local* IC is not characterised here.
- **`docs/manuscript.md` § 5.1.2 / § 5.1.5 / § 5.6 close-out / § 6 conclusion**: bound-vs-reference language homogenised. The *N* / *k*_eff observable is described consistently as a heuristic reference, not a bound; "floor" and "cannot exceed" language replaced with "approximate value under the independent-reading null" / "static-memoryless prediction"; one-sided-bound claim removed.
- **`docs/manuscript.md` abstract**: scope tightened to "*under static-memoryless aggregation*"; explicit acknowledgement that ADMEC's classifier is global while the consensus rule is local; redesign list extended.
- **`docs/manuscript.md` § 5.6 "Reserved follow-up"** extended from two redesigns to three: (i) STRUCTURED with reduced weight + drift estimation; (ii) decayed-staleness weighting with state propagation; (iii) **truly decentralised IC** (each node computes its own IC over its delay-accessible readings). The third item makes the prerequisite for any deployment claim about ADMEC-as-decentralised explicit.

### Status
- Second-pass items did not change any data; all edits are prose / equation. The negative DG verdicts are unchanged; the manuscript no longer overclaims architectural locality, terminological consistency, or noise-taxonomy correctness.
- Suite at 303 / 301 passing.

## [0.8.5] — 2026-05-05

### Atlas-integrity reader pass

A pre-release domain-expert reading from the perspective of operational hydrogen-maser and optical-clock ensemble engineering identified twelve specific concerns about the manuscript's metrology realism. The full review is recorded verbatim in [`docs/atlas_integrity_reader_pass.md`](docs/atlas_integrity_reader_pass.md). Headline finding: "The manuscript is a solid characterisation study with a strong methodological backbone. Its main weakness is that it is too pure-mathematics and not enough metrology."

The manuscript revision below incorporates all HIGH-priority items, all MEDIUM-priority items either as edits or as scope-bounded follow-up commitments, and the LOW-priority items as edits where they require only prose. Items that would require new simulation infrastructure (tuned random-walk-FM Kalman baseline; physically-motivated S8 replacement; Allan-deviation metric on consensus residuals; parameter-sensitivity sweep on `bocpd` / `imm` defaults) are explicitly deferred to the follow-up project's pre-registration.

### Added
- `scripts/wp3_threshold_fpr_check.py`: per-threshold null-FPR check on S4 (15-node ring null) and S5 (50-node random-sparse null), 10 seeds. Output [`data/wp3_threshold_null_fpr_20260505.npz`](data/wp3_threshold_null_fpr_20260505.npz). Result: at the WP1 calibrated threshold (2.976) the empirical null FPR is **1.1–1.2 %**, close to the operational borderline; at threshold 1.5 (the consensus-MSE optimum on S1 / S3 delayed) it is **17.9–18.5 %**, an order of magnitude above the operational redline.
- `docs/atlas_integrity_reader_pass.md`: verbatim record of the reader's findings, with a disposition table mapping each finding to its manuscript response.
- **`docs/manuscript.md` § 2.6 "Scope and limitations vis-à-vis real clock networks"**: a five-row table mapping each of the simulation's key simplifications (white-noise residuals; 3× σ failure mode; Poisson delays; omniscient `freq_global` baseline; MSE-vs-zero figure of merit) to the real-network reality and the implication for the manuscript's claims.
- **`docs/manuscript.md` § 4.4.1 "Operational cost of the low-threshold wins"**: empirical FPR table per threshold, with operational-redline contextualisation. Identifies the threshold-1.5 wins as a *characterisation* of the constraint layer's variance-absorption mechanism, not an operational recommendation.
- **`docs/manuscript.md` § 5.5.1 "Caveats on the recommendations"**: explicit limitations of the operational-recommendation block, noting that real timekeeping uses Allan-deviation / TDEV stability metrics, real failure modes are phase steps and frequency offsets (not σ inflation), and centralised aggregation is itself delay-constrained.

### Changed
- **`docs/manuscript.md` § 5.1**: added a "spatial pooling only" caveat noting that the *N* / *k*_eff reference is the floor for *static memoryless* estimators on the ADMEC update rule; estimators with explicit temporal memory (Kalman with random-walk-FM clock model, AT1-style exponential averaging) may approach or sit below the line. The manuscript's `imm` and `bocpd` baselines carry temporal state but use off-the-shelf default parameters; a tuned random-walk-FM Kalman comparison is reserved for follow-up.
- **`docs/manuscript.md` § 5.5 operational recommendations**: rewritten to (a) bound IC threshold from below by the deployment's tolerable FPR; (b) note that "stale mode" without forward state propagation is a primitive version of NIST AT1-style ensemble-clock practice and a deployment-grade implementation should propagate each neighbour with a clock model; (c) recommend logging the STRUCTURED stream for operator diagnosis even though the consensus rule does not consume it.
- **`docs/manuscript.md` § 5.6 redesign (a)** reframed from "STRUCTURED with reduced weight" to **"STRUCTURED with reduced weight + drift parameter estimated and contributed back into the consensus"** — closer to AT1's per-clock state propagation. The reader's note: "exclude STRUCTURED" is the *opposite* of standard ensemble-clock practice.
- **`docs/manuscript.md` § 5.6 redesign (b)** reframed to "Decayed-staleness weighting *with state propagation*" with explicit pointer to a tuned random-walk-FM Kalman baseline as the appropriate yardstick for the redesign's evaluation.
- **`docs/manuscript.md` § 5.2 retitled** to "Threshold mismatch: null FPR vs consensus MSE — and why this matters operationally".
- **`docs/manuscript.md` references**: Allan 1966 and Lisdat 2016 entries annotated to flag what the manuscript does *not* do (no Allan-deviation primary metric; Poisson delays not representative of optical-fibre links).
- **`docs/manuscript.md` Acknowledgements**: now record the Atlas-integrity reader pass and its scope of influence.

### Outstanding for v1.0 release tag
The Atlas-integrity reader pass is now complete. Remaining items: tag, Zenodo DOI mint, optional final prose polish.

### Status
- Suite at 303 / 301 passing (no source-code changes; only manuscript prose, one new diagnostic script, one new archive, one new docs file).

## [0.8.4] — 2026-05-05

### Changed
- `docs/manuscript.md`: reframed from "draft manuscript scaffold" to **Technical Report v1.0 candidate**. The decision is to keep this work on GitHub Pages as a clean citable technical report rather than push it through journal peer review at this stage; the follow-up project (architectural redesigns from § 5.6 + a Cramér–Rao analysis pre-registered against the new architecture) is the natural home for peer-reviewed publication. Specific edits:
  - Added "Technical Report v1.0 candidate" top-matter directly under the title with explicit framing.
  - Added a preferred-citation block with the intended release tag (`v1.0-tech-report`) and a Zenodo DOI placeholder.
  - Reframed `Type` and `Status` lines away from journal-manuscript language.
  - § 7 now uses the release tag as the canonical anchor; explicit `git tag -a v1.0-tech-report` + push commands; instructions for replacing the DOI placeholders after Zenodo archival.
  - Data-availability and code-availability statements updated to point at the future Zenodo record (DOI placeholders) rather than carrying journal-submission TODOs.
  - Test-suite count updated to 303 / 301 passing (+27 from the user-authored ARP test files).
- `README.md` and `index.md`: project-document tables updated to call the manuscript a "Technical Report v1.0 candidate" with the citable release tag mentioned. Test count row updated to 303 / 301.

### Outstanding for v1.0 release tag
- **Atlas-integrity reader pass.** Council-3 flagged that domain expertise on real clock-network engineering hasn't been invoked. One informed reader's eyes — someone who has touched real maser / optical-clock networks — before tagging.
- **Zenodo DOI mint.** Tag the canonical commit and configure Zenodo's GitHub-release integration to produce a DOI; replace placeholders in manuscript front-matter and statements section.
- **Optional final pass on prose clarity** based on the reader's feedback.

The tag is intentionally not yet created.

### Status
- Project work is complete. The remaining items are pre-release release-management tasks (reader pass, tag, DOI), not new content.
- Suite at 303 / 301 passing.

## [0.8.3] — 2026-05-05

### Changed
- `docs/manuscript.md`: addresses Council-3 review (Guardian + Architect + Integrator stances). The convergent-finding diagnosis — that the central claim was being asserted at three different epistemic strengths in three parts of the document — is the through-line of this revision pass.
  - **Fig. 1 regenerated with `freq_global` as denominator** (Architect A1). The previous figure used `freq_exclude at threshold 2.5` as the "best non-ADMEC baseline"; that denominator silently changed character per scenario (different filter banks won different scenarios) and was inconsistent with the *N* / *k*_eff heuristic's derivation, which is for inverse-variance weighted means of independent readings. `freq_global` is exactly that estimator. New per-seed-paired ratios: S1 baseline 2.28 / combined 0.78; S2 baseline 0.29 / combined 0.29; S3 baseline 18.2 / combined 4.8. Every measurement still sits at or below the *N* / *k*_eff line; the figure is now also consistent with its own derivation.
  - **Algebraic-invisibility argument extended to the projection stage** (Architect A2). § 4.3 now shows that `project_update(state, proposed_update, sigmas, params)` does not read the classifier's mode array — the projection function is mode-blind by signature — so the algebraic invisibility extends through the full ADMEC pipeline, not just the consensus target.
  - **Empty-neighbourhood fallback specified in § 2.2** (Architect A3): a node whose accessible STABLE neighbour set is empty carries the previous estimate forward (or initialises to `Y[0, i]` at *t* = 0; for `admec_full` the centralised inverse-variance weighted mean). Prevalence < 5 % at the WP1 threshold, ≈ 20 % on S3 drop at threshold 1.5.
  - **Pivot statement added to § 1** (Integrator I1): explicit "From pre-registered test to characterised regime" subsection. The pre-registration was for Claim A (does ADMEC pass its gates? — answered NO); the manuscript headlines Claim B (in what regime would the ADMEC family be competitive? — characterised). Both are sourced from the same pre-registered ablation menu; neither rescues the other.
  - **Reader's Map updated** (Integrator I2) to include § 4.3, § 5.3, § 5.4 in the express path; the previously-suppressed novel architectural results are now signposted explicitly.
  - **§ 4.6 re-labelled as post-hoc combined-tuning harness** (Integrator I4) with explicit retraction of the proposal's orthogonality assumption (the data shows non-additive interaction).
  - **§ 3.1 bug-fix paragraph extended** (Integrator I5): explicit statement that all § 4 ablation deltas are computed against the post-fix archive — the negative DG verdicts measure ADMEC against a working baseline, not a buggy one.
  - **§ 4 forward-reference signposts** (Integrator I3): each ablation subsection (§§ 4.2–4.5) now has a one-line italicised forward reference to the discussion section that interprets it.
  - **74 % S3 reduction decomposed** (Architect A4): the headline "74 %" is shown to combine a topological-mode change (drop → stale, *k*_eff 1.30 → 4.00, −38 %) with a parameter change (threshold 2.976 → 1.5, −40 %); the two compose multiplicatively. Headline number now broken into source contributions in a new sub-table in § 4.6.
  - **Stale-mode-below-line mechanism relabelled speculative** (Architect A7): the "temporal pooling" attribution is now replaced with an explicit "bias reduction at the cost of staleness variance" candidate mechanism, marked speculative pending an explicit bias-variance decomposition.
  - **§ 5.3.1 bracketed as "interpretation contingent on follow-up validation"** (Integrator I7).
  - **Acknowledgements added** (Integrator I9) referencing the Council-3 review chart that drove this revision pass.
  - **§ 5.1.4 added — Sign-fixed decomposition (Analytic Reference Pipeline v0.2)**. Bridges the manuscript's informal *N* / *k*_eff observable to the project-internal formal framework at `analysis/docs/analytic_reference.md`, which defines a Jensen gap Δ_J for topology heterogeneity and a sign-fixed deviation Δ_res with explicit interpretation (Δ_res < 0 = "helpful violation", Δ_res > 0 = "unmodelled degradation"). The manuscript adopts ARP's sign-fixed framing for the rest of § 5 as the more careful framing of the speculative mechanism in § 5.1's main text.

- `scripts/figure_topology_ceiling.py`: switched denominator to `freq_global` (per-seed paired with the numerator), updated parity-line label, retitled axes / chart for the new denominator. Backwards-compatibility note: the figure file at `docs/manuscript_files/fig_topology_ceiling.png` is regenerated; numerical claims in older drafts of the manuscript that referenced "best non-ADMEC" denominators are now consistent with the freq_global-denominator framing.

### Status
- Manuscript revised under Council-3 review's HIGH and MEDIUM priorities. The convergent finding (title-vs-body epistemic-strength tension) is resolved across title, abstract, figure, body, reader's map. LOW items mostly addressed; the Cramér–Rao mini-derivation (Architect A8) is reserved for follow-up alongside the redesigns of § 5.6.
- The user-authored Analytic Reference Pipeline (`analysis/`) is staged separately; this commit only references it from the manuscript, leaving the pipeline files for the user to commit themselves.
- Suite unchanged at 276 / 274 passing for the existing test files; new tests under `tests/test_analytic_reference.py` and `tests/test_arp_metrics.py` are part of the user's separate commit.

## [0.8.2] — 2026-05-05

### Changed
- `docs/manuscript.md`: addresses Guardian-stance review (twelve concerns clustered into terminological drift, methodological opacity, and pre-registration hygiene). All HIGH-priority items resolved; MEDIUM and most LOW items also resolved.
  - **Title** "Bound" → "Reference"; subtitle prepended with "An empirical". Title now matches body and §5.1's heuristic framing.
  - **Epistemic-status note** added directly under the title declaring the manuscript a pre-registered characterisation study and the *N* / *k*_eff observable as a heuristic with empirical support, *not* a proven lower bound.
  - **Abstract** scope-restricted: the universal claim "no local-consensus algorithm" is now bounded to the ADMEC family characterised here, with explicit acknowledgement that hierarchical / gossip-with-epoch / asynchronous-clustering schemes are not in our menu.
  - **§ 1 introduction** got a "Pre-registered claims vs post-hoc characterisation" subsection that visually separates the two categories — the pre-registered DG verdicts (§§ 3, 4.3) from the post-hoc characterisation in § 4 ablations and §§ 5.2–5.4 constructive findings.
  - **§ 3.3 DG-2b** now reports per-scenario strict-STRUCTURED TPR. Critical finding now visible: **S8 (fold bifurcation, the scenario the δ_min temporal-statistic gates were calibrated for) has strict-STRUCTURED TPR = 0.0000** across every cell — a result that the prior 0.7 % aggregate masked. Two candidate readings (insufficient horizon vs threshold-mismatch) are listed explicitly.
  - **§ 5.1 expanded** with a new § 5.1.1 "Operational definition of *k*_eff" (one paragraph specifying mean-over-(seed, node) of accessible-neighbour count + 1, with the convention dependence made explicit) and a § 5.1.2 "What the heuristic does and does not claim" that demotes the violated-assumption cancellation to "hypothesised, untested" and notes that a hostile correlation structure could in principle make the heuristic underestimate the gap.
  - **Fig. 1 caption** clarified: the two horizontal positions per scenario reflect the convention change (drop / stale), not measurement noise; combined-tuned points sit modestly *below* their reference (a within-cluster claim) while every cluster sits at or below its reference (an across-cluster claim) — reconciling the previously-ambiguous "at / along / below" language.
  - **§ 5.3.1 substantially rewritten.** Title now "Why tracking STRUCTURED separately *might* still be architecturally important — and why this study cannot tell". The regime-detection reframe is now explicitly a *motivating hypothesis* for § 5.6 redesigns, not a finding — because the only scenario where regime detection should produce a positive signal (S8) produces a zero one. Two pre-conditions for a follow-up STRUCTURED-as-regime-detection criterion are listed.
  - **§ 5.7** opening line softened ("These results admit a reading within the author's broader causal-graph framework (Warring 2026b — currently a self-cited unrefereed preprint)") and "ceiling" → "reference" terminology made consistent with the rest of § 5.
  - **§ 6 conclusion** scope-restricted matching the abstract: claims now apply to the ADMEC family, not all local-consensus algorithm classes.
  - **§ 7 reproducibility** got a "Manuscript-canonical commit" subsection with `git rev-parse HEAD` instructions for pinning the SHA and a Zenodo-DOI to-do.
  - **Statements section added at end**: author contributions, funding, competing interests, data availability, code availability, and an expanded AI-assistance disclosure ("Claude assisted with manuscript scaffolding, prose drafting, and code-template refinement. All simulations, calibrations, numerical results, code commits, scientific decisions, and claims are author-generated and author-verified.").

- `scripts/wp2_classification_check.py`: added per-signal-scenario aggregation so the strict-STRUCTURED TPR can be inspected at S1–S8 granularity. Output adds a "Per-scenario (signal scenarios only)" section after the existing aggregate report. The aggregate numbers are unchanged.

### Status
- Manuscript ready for external submission as a methods/characterisation paper after the listed journal-submission TODOs (Zenodo DOI mint, commit SHA pinning at submission tag).
- Suite unchanged at 276 / 274 passing.

## [0.8.1] — 2026-05-05

### Changed
- `docs/manuscript.md`: substantive reframing pass addressing two external reviews. The manuscript is now framed explicitly as a *pre-registered characterisation study* of the topological boundary on local anomaly-aware consensus, not as a record of a failed gate-rescue attempt.
  - **Title** changed to "A Topological Information-Pooling Bound on Local Clock Consensus" with subtitle "A characterisation study using the ADMEC anomaly-aware scheme". Foregrounds the central claim instead of the project-internal scope.
  - **Abstract** rewritten to lead with the core finding: *delay-constrained local clock consensus is limited primarily by causal-topological access to information, not by estimator sophistication*. The pre-registered decision-gate notation (DG-2/2b/3) is now described in words first; project labels stay in the main text but no longer dominate the abstract.
  - **§ 1 Introduction** now opens with the central claim and treats ADMEC as a vehicle for measuring the boundary, not as the result. A new "Reader's map" subsection tells skim readers which sections to read or skip; the pre-registered design (gates, classifier rule) is now a labelled subsection rather than the main throughline.
  - **§ 5.1 retitled "The topological pooling-limit heuristic"** (was "topological ceiling"). Added an explicit caveat that the *N* / *k*_eff line is a heuristic upper-bound argument, not a proven theorem; identifies the two assumptions (independent readings, no temporal pooling) that the data violates in opposite directions and partially cancel. Figure 1 caption and surrounding prose updated to "reference" rather than "ceiling" in the heuristic-bound context (the figure file itself unchanged).
  - **§ 5.5 Operational recommendations** got a bolded "For deployments where centralised aggregation is feasible" clause head (mirroring the existing bolded recommendation entries) so the deployment-regime guidance is legible on a skim.
  - **§ 5.6 retitled "Reserved follow-up: two architectural redesigns"** (was "Future redesigns"). Adds explicit framing that the redesigns are intentionally reserved for a follow-up study with its own pre-registration rather than added as opportunistic extra sweeps to this manuscript.
  - **§ 6 Conclusion** rewritten to match the characterisation framing: the contribution is a *characterisation of the boundary condition* under which local anomaly-aware consensus competes with centralised pooling, not a claim that ADMEC failed.
  - § 7 reproducibility note slightly softened on "known failures" wording to avoid implying a regression.

### Status
- Manuscript ready for external readers as a characterisation/methods paper. Project documentation and ablation archive are unchanged from v0.8.0; this is a writing-only revision.
- Suite unchanged at 276 / 274 passing.

## [0.8.0] — 2026-05-05

### Added
- `notebooks/wp3_tutorial.ipynb` and `docs/wp3_tutorial.md` (+ figure files): WP3 tutorial — 29 cells walking through the five ablation archives, the integrated combined-tuning archive, and an inline reproduction of the manuscript's topology-ceiling figure. Loads canonical archives rather than re-simulating; runs in ~3 min. Mirrors the WP1/WP2 pattern; cited from `index.md`, `docs/manuscript.md`, and `notebooks/README.md`.

### Changed
- `notebooks/wp1_tutorial.ipynb` (and rendered `docs/wp1_tutorial.md`): added a closing "What happened next" subsection that points to (a) the WP3 finding that the WP1-calibrated 2.976 bit threshold is suboptimal for consensus MSE, and (b) the architectural-impossibility result for three-way > two-way at the consensus stage. No code changes; existing cells re-executed cleanly.
- `notebooks/wp2_tutorial.ipynb` (and rendered `docs/wp2_tutorial.md`): added a closing "What happened next" subsection summarising the five WP3 ablations as a table, the combined-tuning result (S3 0.741 → 0.196), the matched-threshold S1+S2 wins, and pointers to the WP3 tutorial and manuscript.
- `notebooks/README.md`: rewritten to reflect the three-tutorial structure with runtime, scope, and mirrored-markdown links per tutorial.
- `index.md` "Where to start" list now includes all three tutorials.
- `README.md` notebooks row updated to mention all three tutorials.

### Status
- Three matched tutorials covering all three completed work packages, plus a manuscript synthesising the project. Project documentation is complete.
- Suite unchanged at 276 / 274 passing.

## [0.7.5] — 2026-05-05

### Added
- `scripts/wp3_combined_tuning_check.py`: integrated harness running `admec_full` with all three WP3 design recommendations applied simultaneously (`stale` + threshold 1.5 + `var_loose`) on the same RNG-matched seeds as the WP2 campaign. Plus comparator runs of `freq_exclude` at three thresholds and `imm` at default for the matched-threshold and best-of-best comparison framings.
- `data/wp3_combined_tuning_20260505.npz`: integrated-tuning archive.

### Changed
- `docs/manuscript.md`: substantive review fixes addressing all five tier-1 / tier-2 issues raised in two-pass review.
  - Abstract reformatted into paragraphs (so the file is robust to Read truncation) and **gate framing corrected**: the manuscript reports against four pre-registered gates (DG-1 prerequisite, plus DG-2/DG-2b/DG-3 as simulation gates), not two.
  - § 2.1 signal sentence corrected: amplitudes are 5 σ for sinusoidal/step, drift is 0.01 σ/step, fold parameters are ε = 0.005 and r₀ = −1.0; one-line summary replaced with an itemised list that distinguishes signal types.
  - § 3.2 S2 row: bolded `freq_exclude 0.135` (the actual best non-ADMEC baseline on S2) — the prior bolding of `imm 0.147` understated the gap and would have misled readers.
  - § 3.3 DG-2b numbers updated to the corrected `wp2_classification_check.py` output (post-RNG-fix): TPR 0.430 / FPR 0.010 / precision 0.763 (all-scenarios) or 0.831 (signal-only) / F1 0.550 / 0.567 / strict-STRUCTURED TPR 0.007. Prior values shifted by < 0.005 on every metric.
  - § 4.3 "byte-identical" → "numerically identical (max abs delta = 0 to double precision)".
  - § 4.4 low-threshold claim qualified: the preference for low thresholds is real on signal-rich delayed scenarios (S1, S3) but not on the dense low-delay control (S2 drop's optimum is the WP1 calibrated 2.976 bit).
  - § 4.6 reframed and re-measured: the prior "~ 0.24" / "~ 0.19" estimates were composed off individual ablations; replaced with an integrated-harness run (S1 0.252, S2 0.091, S3 0.196). Three comparison framings (DG-2 pre-registered, matched-threshold, best-of-best) tabulated separately so the matched-threshold S1 + S2 wins are not blurred by the best-of-best gap on S3.
- `scripts/wp2_classification_check.py`: RNG order fix — simulate clocks **before** sampling network, matching `wp2_campaign.py`. Without this, the script's seeds produce different (Y, adj, delays) realisations from the canonical archive.
- `logbook/007_2026-05-04_wp2-simulation-harness.md` and `logbook/wp2-summary.md`: updated DG-2b TPR / precision / F1 values to the post-RNG-fix output and added a brief note on the reproducibility-script provenance.
- `index.md`: duplicate ordered-list numbering in "Where to start" fixed (was `1, 2, 3, 4, 5, 4`).
- `README.md`: data row updated to mention the four WP3 ablation archives + integrated combined-tuning archive.

### Status
- WP3 systematic sweep + integrated combined-tuning verification complete. All manuscript numbers reproducible from a checked-in script + canonical .npz pair.
- Suite unchanged at 276 / 274 passing.

## [0.7.4] — 2026-05-05

### Added
- `src/estimators.py:admec_full`: `classification_lag: int = 0` parameter (WP3 ablation 5 — ADMEC-full-lagged). Shifts the classification mode array by `lag` timesteps so reading[t, i] is classified using IC[t − lag, i]. Default `lag = 0` preserves the WP2 baseline.
- `scripts/wp3_ablation_lagged_classification.py`: WP3 ablation 5 harness — 3 scenarios × 10 seeds × 2 delay modes × 2 lag values = 120 runs.
- `data/wp3_ablation_lagged_classification_20260505.npz`: ablation archive.
- `logbook/012_2026-05-05_wp3-ablation-lagged-classification.md`: WP3 ablation 5 entry; closes the systematic sweep.

### Findings
- **No simultaneity bias.** If the same-step IC were artificially inflated by self-reference, lagging the classifier would help. It does not — `lag = 1` hurts admec_full MSE by **+66 %** on S1 drop, **+43 %** on S3 drop, **+28 %** on S1 stale, and is essentially null on S2 and S3 stale.
- Drop-mode S1 / S3 lose structure correlation by **−0.119 / −0.223** under lag = 1 (consensus absorbs more of the signal because anomalous readings flow in for one extra step before exclusion).
- The asymmetry mirrors ablation 1: lag matters when the consensus has few accessible neighbours and no other temporal averaging. Stale mode and dense S2 absorb the lag harmlessly.
- The lagged variant is **strictly dominated** by the default; no scenario × mode where it helps.

### Status
- **WP3 systematic sweep complete (5 of 5 ablations done).** Combined design tuning (stale + var_loose + thr 1.5) takes S3 admec_full from 0.741 to ~0.19 — still 8 × worse than centralised `imm` 0.025. The information-theoretic ceiling on sparse delayed networks holds.
- DG-1 closed (mitigated). DG-2 NOT MET. DG-2b NOT MET. DG-3 NOT MET on three-way > two-way (architecturally impossible). DG-3 constraint clause satisfied.
- 276 / 274 passing (no new tests in this commit; lagged variant validated empirically through the ablation harness).
- Remaining choice: write up as characterisation study, or pursue architectural redesigns (STRUCTURED-with-reduced-weight; decayed-staleness weighting).

## [0.7.3] — 2026-05-05

### Added
- `scripts/wp3_ablation_threshold_sweep.py`: WP3 ablation 2 harness — 7 IC thresholds × 2 delay modes × 3 scenarios × 10 seeds for `admec_full`, plus matched-threshold `freq_exclude` runs and the STABLE-fraction diagnostic grid.
- `data/wp3_ablation_threshold_sweep_20260505.npz`: ablation archive.
- `logbook/011_2026-05-05_wp3-ablation-threshold-sweep.md`: WP3 ablation-2 entry.

### Changed
- `logbook/010_2026-05-04_wp3-ablation-two-vs-three-way.md`: framing strengthened to architectural-impossibility ("three-way *cannot* help under the current architecture, not just *did not* help in this run") per user review of ablation 4.

### Findings
- **The expected "narrow active region" prediction was wrong.** The IC threshold has strong, asymmetric sensitivity: lower thresholds (1.5) substantially improve admec_full MSE on signal-rich delayed scenarios (S1 drop 0.732 → 0.308, −58 %; S3 stale 0.461 → 0.191, −59 %).
- **The WP1-calibrated threshold (2.976, optimised for null FPR) is suboptimal for consensus MSE** in the WP2 problem regime. Different estimators have different optimal thresholds: admec_full prefers low (1.5–2.0); freq_exclude prefers moderate (2.5–3.5).
- **At matched threshold 1.5, admec_full beats freq_exclude on S1 (0.238 vs 0.276) and S2 (0.111 vs 0.276)** — first signal-rich scenarios outside S2 where the architecture beats centralised exclusion. The mechanism: the constraint layer absorbs the per-step variance increase from aggressive exclusion that freq_exclude has no buffer for.
- **Under independent per-estimator threshold tuning** (best-of-best), admec_full adds S2 stale to its win column (0.088 vs imm 0.147). **DG-2 still NOT MET** because the WP2 verdict was pre-registered at the calibrated threshold, and S3's 8× gap to centralised remains.

### Status
- WP3 ablations 1, 2, 3, 4 of 5 complete. Only ablation 5 (`admec-full-lagged`) remains; predicted outcome ≈ null given DG-2b TPR ≈ 0.7 % and entry-010's architectural-impossibility finding.
- Test suite unchanged at 276 / 274 passing (no test additions in this commit).

## [0.7.2] — 2026-05-04

### Added
- `src/classify.py:classify_array` -- `two_way: bool = False` parameter. When True, the temporal-statistic split is bypassed and every flagged reading collapses to UNSTRUCTURED (a single ANOMALOUS class).
- `src/estimators.py` -- `two_way` parameter on `_classify_network_full`, `admec_unconstrained`, `admec_delay`, `admec_full`. Default `False` preserves the WP2 baseline exactly.
- `scripts/wp3_ablation_two_vs_three_way.py`: WP3 ablation 4 harness -- 3 scenarios × 10 seeds × 3 ADMEC estimators × 2 delay modes × 2 classifier variants = 360 cells.
- `data/wp3_ablation_two_vs_three_way_20260504.npz`: ablation archive.
- `logbook/010_2026-05-04_wp3-ablation-two-vs-three-way.md`: WP3 ablation-4 entry.
- `tests/test_classify.py:TestTwoWayClassifier` (5 tests) covering STABLE-region equivalence, STRUCTURED → UNSTRUCTURED collapse, no-STRUCTURED-in-two-way, NaN handling.

### Findings
- **Across 360 (scenario × seed × estimator × delay-mode × classifier) cells, the max absolute MSE delta is 0.0000e+00 and the max absolute structure-correlation delta is 0.0000e+00.** Three-way and two-way produce *byte-identical* consensus output.
- The classification counts differ as expected: three-way has 5–6 STRUCTURED cells per scenario; two-way has 0. But the STABLE count is identical between modes, so the STABLE-only consensus mask is identical, and so are the metrics.
- **DG-3 "three-way > two-way" sub-criterion NOT MET (delta = 0).** A stronger negative result than DG-2 — the gap is exactly zero, not just small. The architectural complexity of the structured/unstructured distinction buys nothing at the level DG-3 measures.
- The corollary insight: the proposal's "tracked and gated" language for STRUCTURED would require an update rule that uses STRUCTURED status (e.g. include with reduced weight) to have any operational effect on the consensus. The current ADMEC architecture excludes both anomaly classes equally.

### Notes
- entry 009 revised to flag `var_loose`'s S1 drop +13.4 % regression explicitly; the recommendation is now scenario-conditional, not a blanket fix.

### Status
- WP3 ablations 1 + 3 + 4 of 5 complete. Combined: DG-2 NOT MET; DG-2b NOT MET; DG-3 NOT MET on the three-way clause. The findings are mutually consistent — STRUCTURED is rare (DG-2b) and operationally inert (this entry).
- 276 / 274 passing (5 new TestTwoWayClassifier tests).
- Next ablation: 2 (threshold sweep) -- quick hygiene check; expected to confirm IC threshold's narrow active region.

## [0.7.1] — 2026-05-04

### Added
- `scripts/wp3_ablation_constraint_sensitivity.py`: WP3 ablation 3 harness — 7 constraint variants (baseline + ±30 % on `max_step_factor`, `energy_factor`, and `var_ratio_min/max`) × 2 delay modes × 3 scenarios × 10 seeds = 420 admec_full runs plus 60 admec_delay comparator runs. RNG ordering matched to `scripts/wp2_campaign.py` so the baseline reproduces the WP2 canonical archive.
- `data/wp3_ablation_constraint_sensitivity_20260504.npz`: ablation archive.
- `logbook/009_2026-05-04_wp3-ablation-constraint-sensitivity.md`: WP3 ablation-3 entry.

### Findings
- **`var_loose` [0.35, 1.65] is the only constraint variant that recovers `admec_full < admec_delay` on S3 stale.** S3 stale admec_full MSE drops from 0.461 → 0.307 (−33 %), beating admec_delay 0.340. Confirms the entry-008 hypothesis that the variance-ratio bound was over-tight under stale-mode noisier proposed updates.
- `energy_tight` (0.7×) also helps materially on S1 drop (−19 %) and S3 stale (−26 %); the energy bound acts as a soft variance regulariser when the proposed update is noisy.
- **The remaining gap to centralised baselines is structural.** Even with `stale` + `var_loose` (the best combination), S3 admec_full = 0.307 is 12× worse than `imm` = 0.025 — consistent with the centralised-vs-local information-theoretic ceiling. **DG-2 stays NOT MET under all 14 (mode × variant) configurations.**
- Constraint sensitivity is heavily scenario-dependent: S2 is essentially insensitive, S1 drop is most sensitive to `energy_tight`, S3 stale is most sensitive to `var_loose`.
- Structure correlation is largely insensitive to constraint tuning (< 0.04 spread across all variants).

### Status
- WP3 ablations 1 + 3 of 5 complete. Together they characterise the WP2 failure: drop convention contributed ~40 % of the gap, variance-ratio bound was the binding constraint under stale, and a 12× residual gap on S3 is information-theoretic. No design tuning can rescue DG-2.
- 271 / 269 passing (no test additions in this commit; harness validation by reproducibility against ablation-1 archive).
- Next ablation: 4 (two-way vs three-way) — the most informative remaining test given DG-2b strict-STRUCTURED TPR ≈ 0.7 %.

## [0.7.0] — 2026-05-04

### Added
- `src/estimators.py`: `delay_mode` parameter on `freq_local`, `admec_delay`, and `admec_full`. `'drop'` (default) preserves the WP2 baseline; `'stale'` (WP3 ablation 1) pulls the delayed reading `Y[t − delays[i, j], j]` for every adjacency neighbour rather than dropping inaccessible ones.
- `scripts/wp3_ablation_delay_convention.py`: WP3 ablation 1 harness — runs S1, S2, S3 × 10 seeds × {drop, stale} on the three local estimators plus centralised baselines for direct comparison. Output: `data/wp3_ablation_delay_convention_YYYYMMDD.npz`. RNG ordering matched to `scripts/wp2_campaign.py` so drop-mode reproduces the WP2 canonical archive exactly.
- `data/wp3_ablation_delay_convention_20260504.npz`: ablation archive.
- `logbook/008_2026-05-04_wp3-ablation-delay-convention.md`: WP3 ablation-1 entry with finding, interpretation, and the unexpected `admec_delay > admec_full` on S3 stale (suggests WP3 ablation 3 — constraint sensitivity — as the next step).
- `tests/test_estimators.py`: 10 new tests under `TestDelayMode` (zero-delay equivalence, unknown-mode rejection, hand-constructed delayed-readings example, finiteness sweep).

### Findings
- Stale convention reduces `admec_full` MSE by **44 %** on S1 (0.732 → 0.413) and **38 %** on S3 (0.741 → 0.461). Structure correlation closes most of the gap to centralised baselines on S3 (0.887 → 0.949 vs `imm` 0.960).
- **DG-2 stays NOT MET under stale**: S1 admec_full 0.413 vs freq_exclude 0.135 (3.1× gap); S3 admec_full 0.461 vs imm 0.025 (18× gap). The WP2 verdict is robust to the delay convention.
- On S2, drop slightly beats stale (0.093 vs 0.104) because adjacency neighbours are already accessible at freshness=1 in dense topology.
- Unexpected: under stale, `admec_delay` beats `admec_full` on S3 MSE (0.340 vs 0.461) — suggests the variance-ratio constraint mis-fires when proposed updates are noisier (multiple stale lags). WP3 ablation 3 will quantify.

### Status
- WP3 ablation 1 of 5 complete. DG-2 robustly NOT MET across delay conventions. Next ablation: constraint sensitivity (#3) or classification threshold (#2).
- 271 tests / 269 passing (10 new `TestDelayMode` tests; 2 known WP1 failures from entry-002 σ-underestimation, mitigated).

## [0.6.1] — 2026-05-04

### Fixed
- `src/constraints.py:is_feasible`: matched the FP guard in `project_update` (`var_before > 1e-20` rather than `> 0`). Previously the two functions disagreed on near-uniform states because `np.var` of a constant array returns ~3e-33: `is_feasible` would mark a small update as infeasible while `project_update` would accept it. Added regression test `test_constant_state_agrees_with_project_update`.
- `logbook/007_2026-05-04_wp2-simulation-harness.md`: corrected the S1 / S3 DG-2 result tables to match the canonical archive — S1 collapse-index `0.622 → 0.644` and structure-correlation `0.899 → 0.897`; S3 collapse-index baseline `freq_exclude → imm`, value `0.820 → 0.808`; S3 structure-correlation baseline `imm 0.952 → 0.960` and admec_full `0.795 → 0.887`. Verdict (NOT MET, S1 = 0/3, S3 = 0/3) is unchanged.
- `logbook/007*.md` and `logbook/wp2-summary.md`: re-derived DG-2b classification metrics with `scripts/wp2_classification_check.py` (now in the repository). Reports both "all 8 scenarios" (TPR 0.432, FPR 0.010, precision 0.767, F1 0.553) and "signal scenarios only" (precision 0.834, F1 0.569). Strict STRUCTURED-only TPR ≈ 0.007. The earlier `0.808 / 0.590` figures were from a separate aggregation that is no longer in the repository; the current values are reproducible from a checked-in script.
- `logbook/007*.md`: structure-correlation table now reports `freq_local` as a mean over the finite-seed subset with explicit seed counts (`0.598 (8/10 seeds)`, etc.) rather than as `NaN`. The collapse-to-zero residual on signal-bearing nodes leaves the Pearson r undefined on a subset of seeds, but the mean over the finite seeds is still informative.

### Added
- `scripts/wp2_classification_check.py`: reproducible DG-2b recomputation. Mirrors the campaign loop and reports `classification_metrics` for both "all scenarios" and "signal scenarios only" denominators, plus the strict STRUCTURED-only TPR.

### Status
- 261 tests / 259 passing (one new regression test for the `is_feasible` FP guard; 2 known WP1 failures from entry-002 σ-underestimation, mitigated).

## [0.6.0] — 2026-05-04

### Added
- `logbook/wp2-summary.md`: WP2 summary document parallel to `wp1-summary.md`. Records the closure of WP2, the negative DG-2 verdict, the structural failure mode (delay-restricted local consensus on sparse networks), and the WP3 ablation framing scoped to *characterise* the failure rather than rescue DG-2.
- `notebooks/wp2_tutorial.ipynb`: WP2 tutorial mirroring the WP1 pattern. Builds a 15-clock ring scenario, computes cross-sectional IC and the three-way classifier output, runs eight estimators, computes the three IC-independent metrics, then loads the canonical campaign archive and reproduces the DG-2 verdict (NOT MET, S1 = 0/3, S3 = 0/3).
- `docs/wp2_tutorial.md`: Rendered markdown twin of the tutorial with figures under `docs/wp2_tutorial_files/`, mirroring `docs/wp1_tutorial.md` so the tutorial is browsable on GitHub Pages without running Python.

### Changed
- `logbook/007_2026-05-04_wp2-simulation-harness.md`: corrected MSE / collapse-index / structure-correlation tables to match the canonical `data/wp2_campaign_20260504_fix.npz`. The earlier draft had carried over a few values from a pre-fix dry run; in particular the claim that `admec_full` "wins on S2, S7, S8" was wrong — only **S2** beats the best non-ADMEC baseline on MSE. The DG-2 verdict (NOT MET, S1 = 0/3, S3 = 0/3) is unchanged. Mitigating-factors section rewritten accordingly.

### Status
- WP2 closed. **DG-2 NOT MET** (negative result, recorded as anticipated by the proposal). DG-2b strict-three-way TPR ≈ 0.7 % (also not met). The constraint layer beats `admec_delay` on every scenario but cannot close the gap to centralised exclusion methods on sparse-with-delay topologies.
- WP3 ablations now scoped to characterise the failure mode (delay convention, classification threshold, constraint sensitivity, two-vs-three-way, ADMEC-full-lagged).
- 261 tests / 259 passing (unchanged; 2 known WP1 failures from entry-002 σ-underestimation, mitigated by worst-case threshold calibration in entry 006).

## [0.5.3] — 2026-05-04

### Added
- `src/metrics.py`: IC-independent performance metrics for WP2 campaign. `mse(estimates, reference=0.0)` — mean squared error vs nominal frequency. `collapse_index(estimates, sigmas)` — time-averaged `std(estimates)/mean(sigma)`; 0 for centralised estimators, >0 for local estimators that preserve per-node diversity. `structure_correlation(Y, estimates, signals, signal_clocks, onset_idx)` — Pearson r between (reading−estimate) and injected signal, averaged over signal clocks post-onset; high = estimator preserved structure rather than absorbing it. `classification_metrics(excluded, true_anomalous)` — TPR/FPR/precision/F1 for DG-2b validation against designer-injected ground truth.
- `scripts/wp2_campaign.py`: Full WP2 simulation harness. Defines all 8 proposal scenarios (S1–S8) with signal parameters chosen in unit scale (sigma_white=1.0): sinusoidal amplitude 5.0, step magnitude 5.0, linear drift rate 0.01/step, fold bifurcation epsilon=0.005/r0=-1.0 (empirically tuned to avoid Euler blow-up). Runs `(scenario, seed, estimator)` triples, computes the three primary metrics, and writes a compressed `.npz`. `--smoke` flag for quick validation (2 scenarios, 2 seeds, T=50).
- `tests/test_metrics.py`: 15 tests covering MSE, collapse-index scale invariance, structure-correlation perfect/zero/constant-residual edge cases, and classification-metric contingency tables.

### Fixed
- `src/estimators.py:admec_full`: t=0 initialization changed from `estimates[0, :] = Y[0, :]` (raw readings) to the centralised inverse-variance weighted mean. The old initialization caused the variance-ratio constraint (`var_after/var_before ∈ [0.5, 1.5]`) to reject *every* update, freezing estimates at the t=0 raw readings. MSE on S2 (fully connected) dropped from **4.85 to 0.13**; on S1 (ring) from **1.50 to 0.64**.

### Status
- **256 tests total**, 254 passing (2 known failures: entry-002 sigma-sensitivity).
- WP2 simulation campaign is ready to launch.

## [0.5.2] — 2026-05-04

### Added
- `src/estimators.py:imm_per_node`: Two-mode IMM filter (Blom & Bar-Shalom 1988). Per-node Kalman bank with shared observation model y = mu + N(0, sigma^2) and two process-noise levels — nominal (`sigma_walk_nominal = 0.01 × mean(sigmas)`) and anomalous (`sigma_walk_anomalous = 0.1 × mean(sigmas)`). Q ratio of 100× sits in the upper end of the 10×–100× sweet spot (smaller ratios collapse both filters; larger ratios let the anomalous mode "explain" any null noise as a true mean shift). Symmetric Markov transition `P(j → k ≠ j) = p_switch = 0.05`; the proposal evaluates `p_switch ∈ {0.01, 0.05, 0.1}`. Returns `(mode_probs (T, 2), estimates (T,))`.
- `src/estimators.py:imm_excluded`: per-step exclusion mask — True when the anomalous-mode posterior exceeds `anomalous_threshold = 0.7`. Empirically chosen: under the Gaussian null with default Q ratio, the anomalous posterior never crosses 0.7 (~0% false-positive rate over 50 random seeds); a clean 5σ step is detected with 1-2 step lag.
- `src/estimators.py:imm`: centralised consensus via IMM-based per-node exclusion — same overall structure as `bocpd`, with the same `t=0` centralised-mean fallback.
- `tests/test_estimators.py`: 12 new IMM tests covering shape and normalisation, low anomalous probability under null, step detection within 5 steps, drift detection, exclusion-mask behaviour (post-step and null), centralised consistency across all nodes, step suppression on a network, parameter validation.

### Changed
- `ESTIMATORS` registry now exposes all 9 of 9 estimators (`imm` added).

### Status
- **WP2 modules complete**: `clocks.py`, `network.py`, `classify.py`, `constraints.py`, `estimators.py` (9/9). The simulation harness can now begin.
- **241 tests total**, 239 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.5.1] — 2026-05-04

### Added
- `src/estimators.py:bocpd_run_length_posterior`: Adams & MacKay 2007 Bayesian online changepoint detection in log-space, with message-passing truncation at `r_max` (default 200) keeping per-step cost O(r_max). Gaussian observations with known per-sample sigma; Gaussian prior on the segment mean (default weakly informative). Constant hazard h(r) = 1/`hazard_lambda`.
- `src/estimators.py:bocpd_excluded`: per-node exclusion mask — True when MAP run-length is below `min_run_keep` (default 10), interpreting the proposal's "post-changepoint nodes excluded" rule.
- `src/estimators.py:bocpd`: centralised consensus estimator using inverse-variance weighted mean over non-excluded nodes. Carries previous estimate forward when all nodes are excluded; uses an all-nodes weighted-mean fallback at t=0 (BOCPD's MAP run-length always starts at 1, so the first step is excluded by construction).
- `tests/test_estimators.py`: 11 new tests for BOCPD covering posterior shape and normalisation, MAP-run-length growth under null, MAP collapse around a step changepoint, exclusion-mask behaviour with one-or-two-step detection lag, centralised-consistency across all nodes, and step suppression on a network with one stepped clock.

### Changed
- `src/estimators.py`: Added documentation comments to `freq_local`, `admec_delay`, and `admec_full` clarifying that delay-inaccessible neighbours are dropped (not pulled from history). Stale-reading variants are deferred to WP3 ablations per user-feedback after batch (a) review.
- `ESTIMATORS` registry now exposes 8 of 9 entries (`bocpd` added).

### Status
- WP2 modules `clocks.py`, `network.py`, `classify.py`, `constraints.py`, and `estimators.py` (8/9). Only IMM remains.
- **229 tests total**, 227 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.5.0] — 2026-05-04

### Added
- `src/estimators.py`: WP2 batch (a) — seven of nine consensus estimators sharing a common `(Y, Sigmas, adj, delays, **kwargs) -> Estimates(T, N)` interface.
  - **FREQ-global**: inverse-variance weighted mean over all nodes per step.
  - **FREQ-local**: per-node weighted mean over delay-accessible neighbours plus self (configurable `freshness` window).
  - **FREQ-exclude**: centralised mean excluding nodes with cross-sectional per-reading IC ≥ `THRESHOLD_95`.
  - **Huber**: IRLS M-estimator with default tuning constant `c = 1.345`; the proposal evaluates `c ∈ {1.0, 1.345, 2.0}` on null scenarios and fixes the best.
  - **ADMEC-unconstrained**: cross-sectional IC + longitudinal temporal stats → three-way classifier; centralised weighted mean over STABLE nodes only (STRUCTURED nodes "tracked and gated", not absorbed; UNSTRUCTURED excluded).
  - **ADMEC-delay**: per-node weighted mean over delay-accessible STABLE neighbours.
  - **ADMEC-full**: ADMEC-delay + sequential constraint projection on the per-node update vector via `src/constraints.py:project_update`.
- Module-level `ESTIMATORS` registry maps method names to callables, ready for the WP2 simulation harness.
- `tests/test_estimators.py`: 27 tests covering shape, dtype, registry membership, finiteness across all seven methods on a clean ring topology, plus per-method correctness checks (variance reduction, outlier exclusion, Huber robustness, full topology equivalence between ADMEC-delay and ADMEC-unconstrained, constraint smoothing under tight variance bounds).

### Status
- WP2 modules `clocks.py`, `network.py`, `classify.py`, `constraints.py`, and `estimators.py` (7/9) implemented. BOCPD and IMM are deferred to the next batch.
- **218 tests total**, 216 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.4.2] — 2026-05-04

### Added
- `src/constraints.py`: Update-size projector for ADMEC-full. `ConstraintParams` dataclass (defaults match proposal spec: max_step_factor=3, energy_factor=1, var_ratio in [0.5, 1.5]); `project_update(state, proposed_update, sigmas)` performs sequential projection (per-node box → energy ball → variance-ratio rejection fallback) and returns (filtered_update, status); `is_feasible` diagnostic helper.
- `tests/test_constraints.py`: 19 tests covering passthrough, box clipping (per-node and per-sigma-vector), energy scaling, variance-ratio rejection (collapsing and inflating), variance-neutral updates, edge cases (scalar sigma, negative sigma, shape mismatch, constant state), `is_feasible` paths, and a sequential-projection feasibility sweep.

### Status
- WP2 modules implemented: `clocks.py`, `network.py`, `classify.py`, `constraints.py`. Only `estimators.py` remains a stub.
- **191 tests total**, 189 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.4.1] — 2026-05-04

### Added
- `src/classify.py`: Three-way classifier wired with calibrated default thresholds (`THRESHOLD_95 = 2.976`, `DELTA_MIN_VAR = 0.2105`, `DELTA_MIN_ACF = 0.8703`) from entries 004 and 006. `Mode` IntEnum (UNDEFINED/STABLE/STRUCTURED/UNSTRUCTURED), `classify_node` (scalar), `classify_array` (vectorised), `classify_series` (single-clock end-to-end), `classify_network` (T×N matrix), `mode_counts` summary helper.
- `tests/test_classify.py`: 23 tests covering default values, all branches of the three-way rule, NaN handling, vectorisation parity, end-to-end behaviour on a Gaussian null and on a heavy-tailed clock, network shape and per-clock independence, and the documented blind spot for linear drift.

### Notes
- Two empirical observations baked into the classifier docstring: (1) linear drift below ~sigma/W classifies as UNSTRUCTURED, since the temporal-structure heuristic is calibrated for critical-slowing-down dynamics; (2) the per-reading IC threshold of 2.976 bit is selective — coherent processes (high-rho AR(1), smooth drifts) broaden the mixture density along with the readings and do not reliably cross it. Crossing typically requires isolated extreme readings. Which scenarios populate STRUCTURED vs UNSTRUCTURED in practice is a WP2 question.

### Status
- WP2 modules implemented: `clocks.py`, `network.py`, `classify.py`. `estimators.py` and `constraints.py` remain stubs.
- **172 tests total**, 170 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.4.0] — 2026-05-04

### Added
- `src/clocks.py`: WP2 clock simulator. `ClockParams` dataclass; `simulate_clock` / `simulate_network_clocks`; signal generators `signal_sinusoidal`, `signal_linear_drift`, `signal_step`, `signal_fold_bifurcation` (S8); `hydrogen_maser` reference preset (Panfilo & Arias 2019); `build_scenario_clocks` composer for the eight WP2 scenarios.
- `src/network.py`: WP2 network topology + delay model. `make_ring`, `make_fully_connected`, `make_random_sparse` (k-regular spanning-tree heuristic, no networkx dependency); `sample_delays` (symmetric Poisson on edges); `make_network` dispatcher.
- `tests/test_clocks.py`: 21 tests covering noise levels, declared sigma, signal additivity for all four generators, heavy-tail behaviour, multi-clock simulation, hydrogen-maser preset, and the scenario builder.
- `tests/test_network.py`: 21 tests covering topology shapes, symmetry, connectivity, degree targets, delay symmetry/integer/edge-only/Poisson-mean behaviour, and the dispatcher.

### Status
- WP2 foundational modules (`clocks.py`, `network.py`) implemented. `classify.py`, `estimators.py`, `constraints.py` remain stubs.
- **149 tests total**, 147 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration).

## [0.3.2] — 2026-05-04

### Added
- `scripts/fig08_per_reading_threshold.py`: Per-reading I_k threshold calibration across the ten null noise models, with worst-case sigma recalibration (-20%)
- `data/006_per_reading_threshold.npz`: Per-reading I_k pools and percentiles for all ten null models, both clean and worst-case sigma regimes
- `tests/test_per_reading_threshold.py`: 19 tests covering the AIPP-vs-per-reading P95 ordering, ×1.5 stability across all ten noise models (clean and worst-case), worst-case inflation under sigma underestimation, and ×1.2 stability across N ∈ {50, 100, 200} for the operational threshold
- `logbook/`: Entry 006 (per-reading threshold recalibration; closes the WP2-prerequisite open item from `wp1-summary.md`)

### Changed
- `logbook/wp1-summary.md`: Open item on AIPP-to-per-reading threshold recalibration is closed; the operational WP2 threshold is 2.976 bit (worst case, heteroscedastic Gaussian), 1.62× the AIPP threshold it replaces
- `src/classify.py`: Stub docstring updated to reference the per-reading 2.976 bit threshold (Entry 006), distinguishing it from the AIPP-derived value of 1.835 bit

### Status
- WP1 → WP2 bridge. Does not modify DG-1 ruling. Resolves the only open item flagged for WP2 entry
- **107 tests total**, 105 passing (2 known failures: systematic -20% sigma-sensitivity, mitigated by worst-case calibration)

## [0.3.1] — 2026-04-01

### Added
- `src/comparison.py`: Comparison figures of merit — `compute_chi2`, `compute_huber`, `compute_allan_deviation`
- `tests/test_comparison.py`: 12 tests for comparison functions and ordering consistency
- `scripts/fig07_comparison_fom.py`: Figure generation for Entry 005
- `scripts/save_wp1_data.py`: Retroactive data export for entries 001–004
- `data/`: Data directory with `.npz` archives for all five logbook entries
- `data/README.md`: Data naming conventions, contents, and regeneration instructions
- `logbook/`: Entry 005 (positioning IC against established figures of merit)

### Status
- **WP1 addendum.** Does not modify DG-1 ruling. Triggered by external review.
- **88 tests total**, 86 passing (2 known failures: systematic −20% σ-sensitivity).

## [0.3.0] — 2026-03-31

### Added
- `src/temporal.py`: Temporal-structure statistics — `compute_temporal_structure`, `calibrate_delta_min`
- `tests/test_temporal.py`: 13 tests for temporal statistics, δ_min calibration, and detectability
- `scripts/fig06_delta_min_calibration.py`: Figure generation script
- `logbook/`: Entry 004 (δ_min calibration)
- `docs/outreach.md`: Non-technical overview

### Changed
- `src/classify.py`: Stub updated to reflect calibrated thresholds (δ_min_var = 0.2105, δ_min_acf = 0.8703) and corrected classifier definition (plain lag-1 acf, not acf trend slope)
- `docs/projektantrag.md`: Classifier rule updated to match WP1 implementation (autocorrelation trend slope → plain lag-1 autocorrelation)
- `README.md`, `index.md`: DG-1 status now consistently reports the σ-sensitivity failure and mitigation

### Status
- **WP1: Complete.** All tasks done (entries 001–004). DG-1 closed with one recorded failure (systematic σ-underestimation, mitigated).
- **76 tests total**, 74 passing (2 known failures: systematic −20% σ-sensitivity).
- Three-way classification rule fully specified.

## [0.2.0] — 2026-03-31

### Added
- `src/ic.py`: IC implementation — `compute_ic`, `compute_aipp`, `compute_ti`, `aipp_gaussian_limit`, `perturb_sigmas`, `verify_sigmas`
- `src/noise.py`: Noise generators — `generate_pareto_symmetric`, `generate_flicker` (Davies-Harte fGn), `generate_random_walk`, `generate_ar1`
- `tests/test_ic.py`: 24 tests for IC computation, convergence, threshold stability, σ-verification
- `tests/test_sensitivity.py`: 17 tests for σ-sensitivity analysis (15 pass, 2 known failures — systematic −20% exceeds 15% bound)
- `tests/test_noise.py`: 15 tests for noise generators
- `tests/test_powerlaw_thresholds.py`: 7 tests for extended threshold stability and finite-N bias
- `scripts/fig04_sigma_sensitivity.py`, `scripts/fig05_powerlaw_thresholds.py`: Figure generation scripts
- `logbook/`: Entries 001–003 with figures (AIPP correction, σ-sensitivity, power-law nulls)
- `index.md`, `_config.yml`: GitHub Pages site (Jekyll, minimal theme)
- `.gitignore`

### Changed
- `docs/projektantrag.md`: Split from combined rebuttal+proposal into proposal-only (v0.5.3). AIPP target corrected from 0.55 to 1.25 bit. All labels switched to English.
- `docs/rebuttal.md`: Standalone rebuttal with proper title. Labels switched to English.
- `README.md`: Updated to reflect WP1 progress, DG-1 closure, test counts, and code status.

### Status
- **DG-1: Closed.** All criteria assessed. All pass except systematic σ-underestimation (−20%), which exceeds the pre-registered 15% bound. Mitigation: worst-case threshold calibration for WP2.
- **63 tests total**, 61 passing.
- Remaining WP1 item: effect-size threshold δ_min.

## [0.0.1] — 2026-03-30

### Added
- Repository structure: `src/`, `tests/`, `notebooks/`, `docs/`
- Stub modules for all six code components (ic, clocks, network, estimators, constraints, classify)
- Project proposal (`docs/projektantrag.md`, v0.5.2 frozen)
- Rebuttal to hostile internal review (`docs/rebuttal.md`)
- README with decision gates, timeline, and honest status reporting
- CITATION.cff
- MIT licence (code), CC BY 4.0 (docs)

### Status
- **No code was implemented.** All modules raised `NotImplementedError`.
- **No results existed.** The repository documented what would be built.

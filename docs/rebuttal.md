# Rebuttal to Internal Review

Response to the hostile review of ADM-EC project proposal v0.4. The review led to the revised proposal v0.5 (see [Project Proposal](projektantrag.md)).

---

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
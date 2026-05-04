# Delay-Constrained Anomaly-Aware Consensus in Heterogeneous Clock Networks

**Status:** WP1 complete. WP2 not started. DG-1 closed with one recorded failure: systematic σ-underestimation exceeds the pre-registered 15% bound (mitigated by worst-case threshold calibration; see logbook entry 002). Three-way classification rule fully specified.

---

## What this is

A research project testing whether distinguishing *structured* from *unstructured* anomalies in a heterogeneous clock network — and responding to each differently under communication-delay and update-size constraints — yields measurable improvement over established robust consensus methods.

The comparison set includes frequentist weighted averaging, Huber M-estimation, Bayesian online changepoint detection (Adams & MacKay 2007), and an interacting multiple model filter (Blom & Bar-Shalom 1988). The proposed scheme classifies nodes into three categories (stable / structured anomaly / unstructured anomaly) using an information-content observable plus temporal-structure criteria, and applies delay-constrained, update-bounded corrections.

The project may produce a positive result (the three-way classification improves consensus) or a negative result (established robust methods are sufficient). Both outcomes are published here.

## What this is not

- Not a framework, architecture, or paradigm. It is a methods study.
- Not an AI project. The clock-network benchmark is inspired by metrology, not machine learning.
- Not a claim about near-critical sensing. One scenario (S8) tests near-critical dynamics; the rest test anomaly detection and change-point handling.

## Project documents

| Document | Description | Status |
|----------|-------------|--------|
| [`docs/projektantrag.md`](docs/projektantrag.md) | Project proposal (DFG Sachbeihilfe structure). Defines objectives, work packages, decision gates, and failure conditions. | v0.5.3 (frozen) |
| [`docs/rebuttal.md`](docs/rebuttal.md) | Point-by-point rebuttal to a hostile internal review. Documents how the project scope was contracted. | v1.0 |

## Code

| Module | Description | Status |
|--------|-------------|--------|
| `src/ic.py` | Information Content: interval-probability definition, analytic Gaussian CDF, σ-perturbation | Implemented (WP1) |
| `src/noise.py` | Noise generators: symmetric Pareto, fractional Gaussian noise (Davies-Harte), random walk, AR(1) | Implemented (WP1) |
| `src/temporal.py` | Temporal-structure statistics (variance slope, lag-1 autocorrelation) and δ_min calibration | Implemented (WP1) |
| `src/comparison.py` | Comparison figures of merit: per-point χ², Huber loss, Allan deviation | Implemented (WP1 addendum) |
| `src/clocks.py` | Clock model with power-law noise (white, flicker, random-walk), four signal generators (sinusoidal, linear, step, fold), heavy-tail and degradation modes, scenario builder | Implemented (WP2) |
| `src/network.py` | Ring / random-sparse / fully-connected topologies with symmetric Poisson delays | Implemented (WP2) |
| `src/estimators.py` | Eight of nine estimators implemented (FREQ-global/local/exclude, Huber, BOCPD, ADMEC-unconstrained/-delay/-full); IMM still pending | Partially implemented (WP2) |
| `src/constraints.py` | Update-size constraint projection: per-node 3σ box, total Nσ² energy ball (sequential projection), variance-ratio fallback rejection | Implemented (WP2) |
| `src/classify.py` | Three-way node classification (stable / structured / unstructured) with calibrated defaults from entries 004 and 006; scalar, vectorised, single-series, and network APIs | Implemented (WP2) |
| `tests/` | Unit tests for IC, noise, σ-sensitivity, threshold stability, temporal structure, comparison, per-reading threshold, clocks, network, classifier, constraints, estimators | 229 tests (227 passing, 2 known failures) |
| `data/` | Numerical output from each logbook entry (.npz archives) | Entries 001–006 |
| `notebooks/` | WP1 calibration, WP2 simulation runs, WP3 ablation | Not yet implemented |

## Decision gates

The project has explicit stop/go gates. Results are published regardless of outcome.

| Gate | Condition | Status | If fail |
|------|-----------|--------|---------|
| **DG-1** | IC calibration: AIPP converges to 1.25 bit (±5% relative); thresholds stable within ×1.5 across noise models including correlated noise; σ-sensitivity bounded | Closed — all criteria pass except systematic σ-underestimation (fails pre-registered 15% bound at +19.3%; mitigated by worst-case threshold calibration, not relaxed; see logbook entries 001–003) | Halt project |
| **DG-2** | ADMEC-full outperforms best non-ADMEC baseline on ≥ 2 IC-independent metrics in S1 and S3; outperforms ADMEC-delay | Not started | Archive as negative result |
| **DG-2b** | Three-way classification TP ≥ 70% (internal consistency check) | Not started | Collapse to two-way classification |
| **DG-3** | Each constraint layer ≥ 10% on ≥ 1 metric; three-way > two-way | Not started | Archive |

## Timeline

| Period | Work package | Gate |
|--------|-------------|------|
| April 2026 | WP1: IC calibration | DG-1 |
| April–May 2026 | WP2: Simulation (8 scenarios × 10 seeds × 9 estimators) | DG-2, DG-2b |
| May 2026 | WP3: Ablation | DG-3 |
| May–June 2026 | WP4: Manuscript | — |

## Motivating context

The project is motivated by the near-critical sensing tradition described in [Amplifiers at the Boundary](https://threehouse-plus-ec.github.io/near-critical-sensing/) (Warring 2026) — an essay on the epistemology of systems that amplify proximity to regime boundaries. The design philosophy (distinguish structured from unstructured anomalies rather than suppressing all anomalies uniformly) comes from that tradition, but the project's evidentiary claims are tested on the clock-network benchmark, not derived from the essay.

## Author

**Ulrich Warring**
Physikalisches Institut, Albert-Ludwigs-Universität Freiburg
Quantum & Atomic Physics group (AG Schätz)

## Licence

Code: MIT. Documentation: CC BY 4.0.

## Acknowledgements

AI tools (Claude, Anthropic) were used for brainstorming, structural editing, and code prototyping during project design. All scientific content, decisions, hypotheses, and claims are the sole responsibility of the author.

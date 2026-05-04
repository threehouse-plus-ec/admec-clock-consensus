---
layout: default
title: Home
---

# ADM-EC Clock Consensus

**Current status:** WP1 complete. WP2 not started. DG-1 closed; IC calibrated across ten null models. One sub-criterion failed: systematic σ-underestimation exceeds 15% bound — this is a procedural workaround (worst-case threshold calibration), not an intrinsic fix; IC remains sensitive to the fidelity of declared uncertainties. Three-way classification rule fully specified (δ_min calibrated).

*IC is stable under tested nulls and finite-N effects. Sensitivity to σ-misestimation indicates dependence on the fidelity of declared uncertainties rather than intrinsic robustness. WP2 will test whether classification-based response compensates for this sensitivity at the system level.*

---

Does distinguishing *structured* from *unstructured* anomalies in a heterogeneous clock network — and responding to each differently under communication-delay and update-size constraints — yield measurable improvement over established robust consensus methods?

This project tests that question on simulated clock networks, comparing the proposed scheme against frequentist averaging, Huber M-estimation, Bayesian online changepoint detection, and an interacting multiple model filter. Both positive and negative results are published.

**Author:** Ulrich Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg

### Where to start

1. **[WP1 Tutorial](docs/wp1_tutorial.md)** — walkthrough of IC definition, calibration, and classification with outputs – run it online: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/threehouse-plus-ec/admec-clock-consensus/main?labpath=notebooks%2Fwp1_tutorial.ipynb)
2. **[Project Proposal](docs/projektantrag.md)** — objectives, work packages, decision gates, failure conditions. Start here for the full picture.
3. **[Latest logbook entry](logbook/006_2026-05-04_per-reading-threshold-recalibration.md)** — what was done most recently and what it means for the gates.
4. **[Source code](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src)** — the implementation.

---

## Project documents

| Document | Description |
|----------|-------------|
| [Project Proposal](docs/projektantrag.md) | Internal project proposal (DFG Sachbeihilfe structure, v0.5.3 frozen). Defines objectives, work packages, scenarios, estimators, decision gates, and failure conditions. |
| [Rebuttal](docs/rebuttal.md) | Point-by-point response to a hostile internal review of proposal v0.4. Documents what was conceded, what was cut, and why. |
| [Outreach](docs/outreach.md) | Non-technical overview: when clocks disagree — noise, signal, and the value of anomalies. |
| [WP1 Summary](logbook/wp1-summary.md) | What was defined, demonstrated, and not solved in WP1. Consolidates entries 001–005. |

## Data

Numerical output from each logbook entry: [`data/`](data/)  
Naming convention: `{entry_number}_{short_name}.npz`. See [`data/README.md`](data/README.md) for contents.

## Logbook

Chronological record of what was done, what was found, and what it means for the decision gates.

| Entry | Date | Summary |
|-------|------|---------|
| [001 — IC Implementation and AIPP Correction](logbook/001_2026-03-31_ic-implementation-and-aipp-correction.md) | 2026-03-31 | IC implemented; AIPP null limit corrected from 0.55 to 1.25 bit; convergence and threshold stability pass DG-1 |
| [002 — σ-Sensitivity Analysis](logbook/002_2026-03-31_sigma-sensitivity-analysis.md) | 2026-03-31 | Systematic −20% σ-underestimation fails pre-registered 15% bound; proceed with worst-case threshold calibration |
| [003 — Power-Law Nulls and Finite-N Bias](logbook/003_2026-03-31_powerlaw-nulls-and-finite-n-bias.md) | 2026-03-31 | All ten null models within ×1.5; finite-N bias < 1% at N ≥ 75; DG-1 closed |
| [004 — δ_min Calibration](logbook/004_2026-03-31_delta-min-calibration.md) | 2026-03-31 | Effect-size thresholds calibrated; classification rule complete; WP1 complete |
| [005 — Positioning IC Against FoM](logbook/005_2026-04-01_positioning-ic-against-fom.md) | 2026-04-01 | IC positioned against χ², Huber loss, Allan deviation; property table; data infrastructure |
| [006 — Per-Reading Threshold Recalibration](logbook/006_2026-05-04_per-reading-threshold-recalibration.md) | 2026-05-04 | AIPP→per-reading threshold recalibrated; operational WP2 threshold 2.976 bit, 1.62× the AIPP value; closes WP2 prerequisite |

## Code

Source: [`src/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src) | Tests: [`tests/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/tests)

| Module | Description | Status |
|--------|-------------|--------|
| [`ic.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/ic.py) | Information Content: interval-probability definition, analytic Gaussian CDF, σ-perturbation | Implemented |
| [`temporal.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/temporal.py) | Temporal-structure statistics and δ_min calibration for three-way classifier | Implemented |
| [`comparison.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/comparison.py) | Comparison figures of merit: per-point χ², Huber loss, Allan deviation | Implemented |
| [`clocks.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/clocks.py) | Clock model with power-law noise, four signal generators, heavy-tail and degradation modes, scenario builder | Implemented (WP2) |
| [`network.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/network.py) | Ring / random-sparse / fully-connected topologies with symmetric Poisson delays | Implemented (WP2) |
| [`estimators.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/estimators.py) | 8/9 estimators (FREQ × 3, Huber, BOCPD, ADMEC × 3); IMM pending | Partially implemented (WP2) |
| [`constraints.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/constraints.py) | Update-size constraint projection (3σ box, Nσ² energy, variance-ratio rejection) | Implemented (WP2) |
| [`classify.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/classify.py) | Three-way node classification with calibrated defaults (entries 004 + 006) | Implemented (WP2) |

## Decision gates

| Gate | Condition | Status |
|------|-----------|--------|
| **DG-1** | IC calibration: AIPP converges to 1.25 bit (±5% relative); thresholds stable within ×1.5; σ-sensitivity bounded | Closed — all criteria pass except systematic σ-underestimation (mitigated; see entry 002) |
| **DG-2** | ADMEC-full outperforms best non-ADMEC baseline on ≥ 2 IC-independent metrics in S1 and S3; outperforms ADMEC-delay | Not started |
| **DG-2b** | Three-way classification TP ≥ 70% (internal consistency check) | Not started |
| **DG-3** | Each constraint layer ≥ 10% on ≥ 1 metric; three-way > two-way | Not started |

## Work packages

| WP | Description | Status |
|----|-------------|--------|
| **WP1** | IC calibration: convergence, threshold stability, σ-sensitivity, δ_min | Complete (logbook entries 001–005; [summary](logbook/wp1-summary.md)) |
| **WP2** | Clock network simulation: 8 scenarios × 10 seeds × 9 estimators | Not started |
| **WP3** | Ablation: 5 configurations × 3 scenarios × 10 seeds | Not started |
| **WP4** | Manuscript | Not started |

## Timeline

| Period | Work package | Gate |
|--------|-------------|------|
| April 2026 | WP1: IC calibration | DG-1 |
| April–May 2026 | WP2: Simulation | DG-2 |
| May 2026 | WP3: Ablation | DG-3 |
| May–June 2026 | WP4: Manuscript | — |

---

Code: MIT. Documentation: CC BY 4.0.

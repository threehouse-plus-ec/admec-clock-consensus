---
layout: default
title: Home
---

# ADM-EC Clock Consensus

**Current status:** WP1 in progress. IC implemented and converges to 1.25 bit. Threshold stability verified across five noise models. σ-sensitivity: systematic underestimation (-20%) fails the pre-registered 15% bound (+19.3% shift); proceeding with worst-case threshold calibration. Power-law nulls and finite-N bias remain.
{: .status-banner}

---

Does distinguishing *structured* from *unstructured* anomalies in a heterogeneous clock network — and responding to each differently under communication-delay and update-size constraints — yield measurable improvement over established robust consensus methods?

This project tests that question on simulated clock networks, comparing the proposed scheme against frequentist averaging, Huber M-estimation, Bayesian online changepoint detection, and an interacting multiple model filter. Both positive and negative results are published.

**Author:** Ulrich Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg

### Where to start

1. **[Projektantrag](docs/projektantrag.md)** — the project proposal: objectives, work packages, decision gates, failure conditions. Start here for the full picture.
2. **[Latest logbook entry](logbook/002_2026-03-31_sigma-sensitivity-analysis.md)** — what was done most recently and what it means for the gates.
3. **[Source code](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src)** — the implementation.

---

## Project documents

| Document | Description |
|----------|-------------|
| [Projektantrag](docs/projektantrag.md) | Internal project proposal (DFG Sachbeihilfe structure, v0.5.3 frozen). Defines objectives, work packages, scenarios, estimators, decision gates, and failure conditions. |
| [Rebuttal](docs/rebuttal.md) | Point-by-point response to a hostile internal review of Projektantrag v0.4. Documents what was conceded, what was cut, and why. |

## Logbook

Chronological record of what was done, what was found, and what it means for the decision gates.

| Entry | Date | Summary |
|-------|------|---------|
| [001 — IC Implementation and AIPP Correction](logbook/001_2026-03-31_ic-implementation-and-aipp-correction.md) | 2026-03-31 | IC implemented; AIPP null limit corrected from 0.55 to 1.25 bit; convergence and threshold stability pass DG-1 |
| [002 — σ-Sensitivity Analysis](logbook/002_2026-03-31_sigma-sensitivity-analysis.md) | 2026-03-31 | Systematic −20% σ-underestimation fails pre-registered 15% bound; proceed with worst-case threshold calibration |

## Code

Source: [`src/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src) | Tests: [`tests/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/tests)

| Module | Description | Status |
|--------|-------------|--------|
| [`ic.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/ic.py) | Information Content: interval-probability definition, analytic Gaussian CDF, σ-perturbation | Implemented |
| [`clocks.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/clocks.py) | Clock model with power-law noise | Not yet implemented |
| [`network.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/network.py) | Network topology and delay model | Not yet implemented |
| [`estimators.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/estimators.py) | All nine estimators | Not yet implemented |
| [`constraints.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/constraints.py) | Update-size constraint projection | Not yet implemented |
| [`classify.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/classify.py) | Three-way node classification | Not yet implemented |

## Decision gates

| Gate | Condition | Status |
|------|-----------|--------|
| **DG-1** | IC calibration: AIPP converges to 1.25 bit (±5% relative); thresholds stable within ×1.5; σ-sensitivity bounded | Partial — convergence and thresholds pass; σ-underestimate fails 15% bound (proceeding with mitigation) |
| **DG-2** | ADMEC-full ≥ 15% MSE reduction vs best non-ADMEC baseline in S1 and S3 | Not started |
| **DG-3** | Each constraint layer ≥ 10% on ≥ 1 metric; three-way > two-way | Not started |

## Timeline

| Period | Work package | Gate |
|--------|-------------|------|
| April 2026 | WP1: IC calibration | DG-1 |
| April–May 2026 | WP2: Simulation | DG-2 |
| May 2026 | WP3: Ablation | DG-3 |
| May–June 2026 | WP4: Manuscript | — |

---

Code: MIT. Documentation: CC BY 4.0.

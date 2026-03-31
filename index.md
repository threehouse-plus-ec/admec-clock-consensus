---
layout: default
title: Home
---

# ADM-EC Clock Consensus

Delay-constrained anomaly-aware consensus in heterogeneous clock networks.

A research project testing whether distinguishing *structured* from *unstructured* anomalies in a heterogeneous clock network — and responding to each differently under communication-delay and update-size constraints — yields measurable improvement over established robust consensus methods.

**Author:** Ulrich Warring, Physikalisches Institut, Albert-Ludwigs-Universitat Freiburg

---

## Project documents

| Document | Description |
|----------|-------------|
| [Projektantrag](docs/projektantrag.md) | Internal project description (DFG Sachbeihilfe structure). Objectives, work packages, decision gates, failure conditions. |
| [Rebuttal](docs/rebuttal.md) | Point-by-point rebuttal to hostile internal review. |

## Logbook

Chronological record of what was done, what was found, and what it means for the decision gates.

| Entry | Date | Summary |
|-------|------|---------|
| [001 — IC Implementation and AIPP Correction](logbook/001_2026-03-31_ic-implementation-and-aipp-correction.md) | 2026-03-31 | IC implementation, AIPP null limit corrected from 0.55 to 1.25 bit |
| [002 — σ-Sensitivity Analysis](logbook/002_2026-03-31_sigma-sensitivity-analysis.md) | 2026-03-31 | σ-sensitivity: systematic −20% fails 15% bound; proceed with worst-case calibration |

## Code

Source code: [`src/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src) — Tests: [`tests/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/tests)

| Module | Description | Status |
|--------|-------------|--------|
| [`ic.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/ic.py) | Information Content: interval-probability definition, analytic Gaussian CDF | Implemented |
| [`clocks.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/clocks.py) | Clock model with power-law noise | Not yet implemented |
| [`network.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/network.py) | Network topology and delay model | Not yet implemented |
| [`estimators.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/estimators.py) | All nine estimators | Not yet implemented |
| [`constraints.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/constraints.py) | Update-size constraint projection | Not yet implemented |
| [`classify.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/classify.py) | Three-way node classification | Not yet implemented |

## Decision gates

| Gate | Condition | Status |
|------|-----------|--------|
| **DG-1** | IC calibration: AIPP converges to 1.25 bit (±5% relative); thresholds stable within ×1.5 | Partial pass |
| **DG-2** | ADMEC-full ≥ 15% MSE reduction vs FREQ-global in S1 and S3 | Not started |
| **DG-3** | Each constraint layer ≥ 10% on ≥ 1 metric | Not started |

## Timeline

| Period | Work package | Gate |
|--------|-------------|------|
| April 2026 | WP1: IC calibration | DG-1 |
| April–May 2026 | WP2: Simulation | DG-2 |
| May 2026 | WP3: Ablation | DG-3 |
| May–June 2026 | WP4: Manuscript | — |

---

Code: MIT. Documentation: CC BY 4.0.

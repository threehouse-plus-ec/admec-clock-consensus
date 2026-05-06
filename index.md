---
layout: default
title: Home
---

# ADM-EC Clock Consensus

**Current status:** WP1 complete, WP2 complete. **DG-2 NOT MET (negative result, recorded as anticipated)**: `admec_full` beats the best non-ADMEC baseline on MSE in one of eight scenarios (S2, fully connected, low delay). The delay-restricted local consensus cannot close the gap to centralised exclusion methods on sparse-with-delay topologies; the constraint layer beats `admec_delay` everywhere but cannot rescue DG-2. WP3 ablations are scoped to characterise this failure mode (delay convention, classification threshold, constraint sensitivity).

*IC is stable under tested nulls and finite-N effects. Sensitivity to σ-misestimation indicates dependence on the fidelity of declared uncertainties rather than intrinsic robustness. WP2 has tested whether classification-based response compensates for this sensitivity at the system level — it does not, on the eight tested scenarios. WP3 ablations characterise which architectural choice drives the failure.*

---

Does distinguishing *structured* from *unstructured* anomalies in a heterogeneous clock network — and responding to each differently under communication-delay and update-size constraints — yield measurable improvement over established robust consensus methods?

This project tests that question on simulated clock networks, comparing the proposed scheme against frequentist averaging, Huber M-estimation, Bayesian online changepoint detection, and an interacting multiple model filter. Both positive and negative results are published.

**Author:** Ulrich Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg

### Where to start

1. **[Technical Report v1.0 candidate](docs/manuscript.md)** — the full WP2 + WP3 characterisation: campaign results, all five ablations, the topology-pooling-limit figure, mechanism, operational recommendations, and follow-up redesign directions. Reads in ~15 min. Citable through release tag `v1.0-tech-report` (pending Atlas-integrity reader pass + Zenodo DOI).
2. **[WP1 Tutorial](docs/wp1_tutorial.md)** — IC definition, calibration, and classification — [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/threehouse-plus-ec/admec-clock-consensus/main?labpath=notebooks%2Fwp1_tutorial.ipynb)
3. **[WP2 Tutorial](docs/wp2_tutorial.md)** — network pipeline + the DG-2 verdict — [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/threehouse-plus-ec/admec-clock-consensus/main?labpath=notebooks%2Fwp2_tutorial.ipynb)
4. **[WP3 Tutorial](docs/wp3_tutorial.md)** — five ablations + integrated combined-tuning + the topology pooling-reference figure — [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/threehouse-plus-ec/admec-clock-consensus/main?labpath=notebooks%2Fwp3_tutorial.ipynb)
5. **[Project Proposal](docs/projektantrag.md)** — pre-registered objectives, work packages, decision gates.
6. **[Latest logbook entry](logbook/012_2026-05-05_wp3-ablation-lagged-classification.md)** — WP3 ablation 5 (lagged classification, closes the systematic sweep).
7. **[Source code](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src)** — the implementation.

---

## Project documents

| Document | Description |
|----------|-------------|
| [Technical Report v1.0 candidate](docs/manuscript.md) | The full WP2 + WP3 characterisation, prepared as a citable technical report rather than a journal manuscript. Self-contained ~15 min read; tables reproducible from the canonical archives. Citable via release tag + Zenodo DOI once the Atlas-integrity reader pass is complete. |
| [Project Proposal](docs/projektantrag.md) | Internal project proposal (DFG Sachbeihilfe structure, v0.5.3 frozen). Defines objectives, work packages, scenarios, estimators, decision gates, and failure conditions. |
| [Rebuttal](docs/rebuttal.md) | Point-by-point response to a hostile internal review of proposal v0.4. Documents what was conceded, what was cut, and why. |
| [Outreach](docs/outreach.md) | Non-technical overview: when clocks disagree — noise, signal, and the value of anomalies. |
| [WP1 Summary](logbook/wp1-summary.md) | What was defined, demonstrated, and not solved in WP1. Consolidates entries 001–005. |
| [WP2 Summary](logbook/wp2-summary.md) | What was implemented, the negative DG-2 verdict, and the WP3 ablation framing. Consolidates entry 007. |

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
| [007 — WP2 Simulation Harness](logbook/007_2026-05-04_wp2-simulation-harness.md) | 2026-05-04 | WP2 campaign harness (8 scenarios × 10 seeds × 9 estimators); metrics module; `admec_full` initialization bug fixed |
| [008 — WP3 Ablation 1: Delay Convention](logbook/008_2026-05-04_wp3-ablation-delay-convention.md) | 2026-05-04 | Stale-reading mode reduces `admec_full` MSE by 38–44 % on S1/S3 but does not close the gap to centralised baselines; DG-2 robustly NOT MET |
| [009 — WP3 Ablation 3: Constraint Sensitivity](logbook/009_2026-05-04_wp3-ablation-constraint-sensitivity.md) | 2026-05-04 | `var_loose` [0.35, 1.65] recovers `admec_full < admec_delay` on S3 stale (−33 % MSE); no variant closes the 12× gap to centralised baselines; DG-2 NOT MET across all 14 (mode × variant) configurations |
| [010 — WP3 Ablation 4: Two-vs-Three-Way](logbook/010_2026-05-04_wp3-ablation-two-vs-three-way.md) | 2026-05-04 | Three-way and two-way classifiers produce byte-identical consensus (max delta = 0 across 360 cells). DG-3 "three-way > two-way" NOT MET — the structured/unstructured split has no operational effect under the WP2 architecture |
| [011 — WP3 Ablation 2: Threshold Sweep](logbook/011_2026-05-05_wp3-ablation-threshold-sweep.md) | 2026-05-05 | IC threshold sensitivity is much larger than predicted; lower thresholds (1.5) halve admec_full MSE on S1/S3. At matched threshold 1.5, admec_full beats freq_exclude on S1 and S2; DG-2 still NOT MET on S3 (8× gap remains) |
| [012 — WP3 Ablation 5: Lagged Classification](logbook/012_2026-05-05_wp3-ablation-lagged-classification.md) | 2026-05-05 | No simultaneity bias detected — `classification_lag=1` HURTS by +28 % to +66 % on drop-mode signal-rich scenarios. WP3 systematic sweep complete (5/5) |

## Code

Source: [`src/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/src) | Tests: [`tests/`](https://github.com/threehouse-plus-ec/admec-clock-consensus/tree/main/tests)

| Module | Description | Status |
|--------|-------------|--------|
| [`ic.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/ic.py) | Information Content: interval-probability definition, analytic Gaussian CDF, σ-perturbation | Implemented |
| [`temporal.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/temporal.py) | Temporal-structure statistics and δ_min calibration for three-way classifier | Implemented |
| [`comparison.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/comparison.py) | Comparison figures of merit: per-point χ², Huber loss, Allan deviation | Implemented |
| [`clocks.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/clocks.py) | Clock model with power-law noise, four signal generators, heavy-tail and degradation modes, scenario builder | Implemented (WP2) |
| [`network.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/network.py) | Ring / random-sparse / fully-connected topologies with symmetric Poisson delays | Implemented (WP2) |
| [`estimators.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/estimators.py) | All 9 estimators (FREQ × 3, Huber, BOCPD, IMM, ADMEC × 3) | Implemented (WP2) |
| [`constraints.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/constraints.py) | Update-size constraint projection (3σ box, Nσ² energy, variance-ratio rejection) | Implemented (WP2) |
| [`classify.py`](https://github.com/threehouse-plus-ec/admec-clock-consensus/blob/main/src/classify.py) | Three-way node classification with calibrated defaults (entries 004 + 006) | Implemented (WP2) |

## Decision gates

| Gate | Condition | Status |
|------|-----------|--------|
| **DG-1** | IC calibration: AIPP converges to 1.25 bit (±5% relative); thresholds stable within ×1.5; σ-sensitivity bounded | Closed — all criteria pass except systematic σ-underestimation (mitigated; see entry 002) |
| **DG-2** | ADMEC-full outperforms best non-ADMEC baseline on ≥ 2 IC-independent metrics in S1 and S3; outperforms ADMEC-delay | **NOT MET** — S1 = 0/3, S3 = 0/3 metrics pass (entry 007); only S2 wins on MSE. `admec_full` does beat `admec_delay` on every scenario |
| **DG-2b** | Three-way classification TP ≥ 70% (internal consistency check) | NOT MET on strict three-way (TPR ≈ 0.7 %); overall anomaly TPR 0.46 |
| **DG-3** | Each constraint layer ≥ 10% on ≥ 1 metric; three-way > two-way | **NOT MET on three-way > two-way** (entry 010): three-way and two-way produce byte-identical consensus across all 360 cells (max delta = 0). Constraint clause satisfied (entry 009) but the three-way clause cannot be satisfied without an architectural redesign |

## Work packages

| WP | Description | Status |
|----|-------------|--------|
| **WP1** | IC calibration: convergence, threshold stability, σ-sensitivity, δ_min | Complete (logbook entries 001–005; [summary](logbook/wp1-summary.md)) |
| **WP2** | Clock network simulation: 8 scenarios × 10 seeds × 9 estimators | Complete (entry 007; [summary](logbook/wp2-summary.md)) — DG-2 NOT MET |
| **WP3** | Ablation: 5 configurations × 3 scenarios × 10 seeds (delay convention, classification threshold, constraint sensitivity, two-vs-three-way, ADMEC-full-lagged) | **Complete** (entries 008–012) |
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

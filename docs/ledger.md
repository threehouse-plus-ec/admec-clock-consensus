---
layout: default
title: Claim Analysis Ledger
---

# Claim Analysis Ledger

> **Boundary sentence (frozen).** *The handbook defines procedures; the Ledger records outcomes and discriminant conditions.* Methodology does not migrate into the Ledger; outcomes do not migrate into the [handbook](handbook.md).

The Ledger is a registry of **claim-shaped outcomes** across phases of the ADM-EC Clock Consensus programme. Each entry classifies one claim as **COMPATIBLE / UNDERDETERMINED / INCONSISTENT** under a stated constraint set, and records the discriminant condition that distinguishes those classes.

**Anti-aggregation discipline.** Not every WP produces a Ledger entry. A WP is Ledger-shaped only if its outcome is itself a *claim* (with stated alternatives, a discriminant, and a feasibility flag). Methodology, harness builds, and per-axis ablations stay in the [logbook](../logbook/) and the Projektantrag's audit trail; the Ledger is reserved for claim-level outcomes.

## Status

- **Created:** 2026-05-06 alongside the [Phase-2 Projektantrag](projektantrag_p2.md), in response to its §11 pre-registration registry pattern.
- **Phase-1 entries:** none. Phase-1 outcomes are recorded in the [manuscript](manuscript.md), the [logbook](../logbook/), and the [WP1](../logbook/wp1-summary.md) / [WP2](../logbook/wp2-summary.md) summaries; they are not currently re-shaped as Ledger claims.
- **Phase-2 entries:** one proposed (CL-2026-006). Identifier assignment is **deferred to the Phase-2 v1.0 freeze** (Integrator handshake — Projektantrag §13).

## Entries

### CL-2026-006 *(proposed; pending Integrator confirmation at Phase-2 v1.0 freeze)*

| Field | Value |
|-------|-------|
| **Identifier** | CL-2026-006 (proposed; assignment deferred to v1.0 freeze) |
| **Title** | WP-α₀ — IC threshold transfers to canonical Phase-2 noise families |
| **Phase** | 2 |
| **Source document** | [Phase-2 Projektantrag §8.1, §11](projektantrag_p2.md#81-wp-α₀--ic-threshold-recalibration) |
| **Claim shape** | The Phase-1 Gaussian-null-calibrated IC threshold either *transfers* (recalibration shifts only the threshold value within the same estimator family) or *does not transfer* (calibration model changes, or estimator-family chart transition required). |
| **Alternatives** | T1 — location shift only (in-chart recalibration); T2 — shape change with stable rank ordering (calibration model changes, estimator survives); T3 — ordering instability (chart transition triggered, estimator-family challenge). |
| **Discriminant condition** | (i) AD-test p-value vs pre-registered α = 0.01; (ii) Kolmogorov Δ_max > 0.05 *or* tail-ratio deviation > 20 % at the 95th-percentile reference; (iii) Spearman-ρ ≥ 0.85 ordering check. Detailed thresholds in [Projektantrag §§8.1.1, 8.1.2](projektantrag_p2.md#811-dual-materiality-threshold-for-t1-vs-t2). |
| **Feasibility flag** | Pre-registered as feasible at R = 10⁴ Monte-Carlo replicates per family (Phase-2 §10). Software-stack pins recorded for bit-identical replay. |
| **Outcome classification** | TBD — pending WP-α₀ campaign closure. |
| **Status** | **PROPOSED.** Identifier *CL-2026-006* is provisional; Integrator confirms against the live Ledger registry state at v1.0 freeze and either ratifies the identifier or assigns the next available one. |

**Anti-aggregation note.** WP-α through WP-ε do **not** create new Ledger entries unless their outcomes are themselves claim-shaped under the discipline above. WP-α₀ qualifies because the recalibration outcome decides the *shape* of all downstream calibration: T1 / T2 keeps the estimator family in chart, T3 forces a chart transition. WP-α / WP-β / WP-γ / WP-δ / WP-ε produce campaign-style outcomes (decision-gate PASS / NOT MET against pre-registered MSE thresholds) that belong in the Projektantrag audit trail, not in the Ledger.

---

## Schema

Every Ledger entry uses the table above's field set. Required fields:

- **Identifier** — `CL-YYYY-NNN`. Assignment by Integrator at the next freeze checkpoint, against live registry state.
- **Title** — short claim name; matches the Projektantrag wording.
- **Phase** — 1, 2, … (one Ledger; phase scopes which Projektantrag governs the entry).
- **Source document** — the Projektantrag clause that defines the claim shape.
- **Claim shape** — one to three sentences stating the claim and its alternatives in falsifiable terms.
- **Alternatives** — explicit enumeration (T1 / T2 / T3 here; PASS / NOT MET / NOT APPLICABLE in other shapes).
- **Discriminant condition** — the procedural test that distinguishes alternatives. Procedure details live in the [handbook](handbook.md), not here.
- **Feasibility flag** — whether the discriminant test is operationally runnable; if not, the entry is recorded as PROPOSED but cannot resolve.
- **Outcome classification** — `COMPATIBLE / UNDERDETERMINED / INCONSISTENT` (or domain-specific labels like T1 / T2 / T3); set after the discriminant test runs. `TBD` until then.
- **Status** — `PROPOSED / OPEN / RESOLVED / WITHDRAWN`.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| v0.1 (stub) | 2026-05-06 | Created alongside Phase-2 Projektantrag draft v0.2. CL-2026-006 staged as PROPOSED. Identifier confirmation deferred to Phase-2 v1.0 freeze. |

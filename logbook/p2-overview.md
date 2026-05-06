# Phase-2 Overview — Pre-Freeze Status

**Status:** Phase-2 Projektantrag in draft v0.2 ([`docs/projektantrag_p2.md`](../docs/projektantrag_p2.md)). **No Phase-2 simulation work has started.** This file is the Phase-2 logbook entry-point; per-WP entries land here once the v1.0 freeze closes and WP-α₀ opens.

---

## Where Phase 2 stands at the time of writing

Phase 1 closed with:

- DG-1 CLOSED (mitigated; logbook entries 002, 006).
- DG-2, DG-2b, DG-3 NOT MET (entries 007, 010, plus the WP3 ablation series 008–012).
- The Technical Report v1.0 candidate ([`docs/manuscript.md`](../docs/manuscript.md)) is the citable Phase-1 deliverable.

Phase 2 is a *redesign campaign* on the topological pooling-limit baseline characterised in Phase 1. The Projektantrag in [`docs/projektantrag_p2.md`](../docs/projektantrag_p2.md) defines:

- Two consensus-rule redesigns to test independently before any combined version: WP-γ (α-rule, STRUCTURED with reduced weight + estimated drift) and WP-δ (λ-rule, decayed-staleness weighting with state propagation).
- A WP-α₀ recalibration pass for the IC threshold under four canonical noise families (white FM, flicker FM, random-walk FM, power-law FM) with three-tier T1 / T2 / T3 escalation logic.
- A WP-α STRUCTURED-channel separability check that gates the WP-γ main path.
- A WP-β Cramér–Rao floor pass that replaces the heuristic *N* / *k*_eff line with a per-(scenario, family) bound.
- Two new metrology-anchored scenarios: S9 (linear fibre chain, 10 nodes) and S10 (hub-and-spoke, 12 nodes).
- A frozen Reporting Clause requiring Allan-family auxiliaries (σ_y(τ), Mod-σ_y(τ), TDEV) on every output, with MSE governing the decision gates and the residual *N* / *k*_eff or Cramér–Rao gap paired on the same line.
- A Pareto-locality clause on every redesign decision gate (≥ 20 % MSE gain on at least one signal-rich scenario *and* ≤ 10 % degradation on every other Phase-2 scenario at the same operating point).

## Pre-freeze blockers (Projektantrag §13 handshakes outstanding)

Phase-2 v1.0 freeze requires:

1. **Integrator confirms CL-2026-006** identifier against the live [Claim Analysis Ledger](../docs/ledger.md), or assigns the next available identifier. The CL-2026-006 entry covers the WP-α₀ recalibration claim shape.
2. **Integrator confirms Handbook §7 anchor** at v1.0 freeze, or invokes the create-if-absent provision (already invoked: [`docs/handbook.md`](../docs/handbook.md) §7 stub initialised 2026-05-06).
3. **Architect handover** (after v1.0 freeze): open WP-α₀ draft against the Projektantrag specification; populate the Handbook §7 stub with full procedure write-ups in the same pass.

## Veto inventory in force during Phase 2

The Projektantrag §4 standing list applies to all Phase-2 deliberations and outputs. In particular:

- Reuse of Phase-1 decision-gate identifiers (DG-2 / DG-2b / DG-3) for Phase-2 gates is vetoed — Phase 2 uses DG-α₀ / DG-α / DG-β / DG-γ / DG-δ / DG-ε.
- Bundling WP-γ and WP-δ before each passes its independent gate is vetoed.
- Citation of EXPLORATORY-tagged results (WP-γ-lite, §8.4.5) as evidence for DG passage, threshold validity, or estimator robustness is vetoed.
- Narrow-regime overfitting (gain on one scenario reported without the Pareto-locality compliance check across S1–S10) is vetoed.

## Archive namespace separation

Phase-2 archives live in the `data/p2_*.npz` namespace, **strictly additive** with respect to Phase-1 archives. No `wp2_*` or `wp3_*` artefact is migrated, regenerated, or overwritten by Phase-2 code. See [`data/README.md`](../data/README.md) for the full namespace table and the harness-drift checksum requirement on every `p2_continuity_*` run.

## Phase-2 logbook entries (planned)

Per-WP entries land in this directory under the `p2_NNN_YYYY-MM-DD_title.md` pattern (mirrors Phase-1 numbering). Numbering is reserved per WP rather than chronologically across WPs:

- `p2_001_*` to `p2_009_*` — WP-α₀ campaign (per-family Monte Carlo nulls, AD tests, ordering checks, T1 / T2 / T3 outcome).
- `p2_010_*` to `p2_019_*` — WP-α STRUCTURED-channel separability diagnostics on S1, S3, S6, S7, S8.
- `p2_020_*` to `p2_029_*` — WP-β per-scenario Cramér–Rao floors.
- `p2_030_*` to `p2_039_*` — WP-γ α-rule campaign (and `p2_030L_*` for any WP-γ-lite EXPLORATORY runs).
- `p2_040_*` to `p2_049_*` — WP-δ λ-rule campaign.
- `p2_050_*` to `p2_059_*` — WP-ε combined α + λ campaign (only opens if DG-γ PASS *and* DG-δ PASS).
- `p2_continuity_*` — Phase-1 S1–S8 re-runs under Phase-2 harness, harness-drift sanity.

This block-numbered scheme matches the Projektantrag's sequential gating: a WP cannot open until its prerequisite gate closes, so numbering blocks reflect the work-package boundaries, not the calendar.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-05-06 | Phase-2 logbook starter created alongside Projektantrag v0.2. No Phase-2 simulation work yet; this file documents the pre-freeze state. |

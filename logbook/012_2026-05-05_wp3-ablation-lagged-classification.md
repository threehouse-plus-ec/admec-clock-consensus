# Logbook Entry 012 — WP3 Ablation 5: ADMEC-Full-Lagged Classification

**Date:** 2026-05-05
**Work package:** WP3 (ablation 5 of 5; closes the systematic sweep)
**Decision gate:** none directly; refines the DG-2 picture

---

## Objective

The proposal lists `ADMEC-full-lagged` as one of five WP3 configurations. Its purpose is to test for **simultaneity bias** in the WP2 architecture: each clock's IC at time t is computed against the cross-sectional ensemble at time t, which includes that clock's own reading. The question is whether this self-reference inflates IC values in a way that biases the classifier — for example by making the per-reading I_k systematically higher because each reading contributes a self-component to its own integrand mixture.

The lagged variant classifies reading[t, i] using IC[t − 1, i] instead of IC[t, i], so the classifier sees only the previous-step ensemble and the direct coupling between IC and the reading being classified is removed. Predicted outcome (entry 008 / 010 prediction list): **approximately null delta**, since consecutive IC values are highly correlated under reasonable temporal coherence.

That prediction was wrong in a direction that turned out to be informative.

## What was done

`src/estimators.py:admec_full` gained a `classification_lag: int = 0` parameter. With `classification_lag = 1`, the classification mode array is shifted by one timestep before being consumed by the consensus rule: row t of `modes` becomes the row that `_classify_network_full` produced for row `t − 1`, with row 0 left at its original value to avoid an out-of-bounds. The IC computation itself is unchanged; only the time index used to look up the classification result is offset. This is the cleanest implementation that matches the proposal's stated semantics ("classification uses IC(t − 1)") without redoing the IC computation.

`scripts/wp3_ablation_lagged_classification.py` runs `admec_full` on the same scenario set as ablations 1–4 (S1, S2, S3 over 10 seeds) at both delay modes (drop, stale) and both lag values (0 = baseline, 1 = lagged). Output: `data/wp3_ablation_lagged_classification_20260505.npz`. RNG order matched to `scripts/wp2_campaign.py`.

## Results

### admec_full mean MSE over 10 seeds

| Scenario | mode | lag = 0 | lag = 1 | absolute Δ | relative |
|----------|------|--------:|--------:|-----------:|---------:|
| S1 | drop | 0.7321 | 1.2185 | +0.4864 | **+66 %** |
| S1 | stale | 0.4132 | 0.5272 | +0.1140 | +28 % |
| S2 | drop | 0.0929 | 0.0927 | −0.0002 | −0.2 % |
| S2 | stale | 0.1043 | 0.1046 | +0.0003 | +0.3 % |
| S3 | drop | 0.7408 | 1.0582 | +0.3175 | **+43 %** |
| S3 | stale | 0.4606 | 0.4652 | +0.0045 | +1.0 % |

### admec_full mean structure correlation over 10 seeds

| Scenario | mode | lag = 0 | lag = 1 | Δ |
|----------|------|--------:|--------:|--:|
| S1 | drop | 0.897 | 0.778 | **−0.119** |
| S1 | stale | 0.924 | 0.912 | −0.012 |
| S2 | drop | 0.958 | 0.957 | −0.001 |
| S2 | stale | 0.957 | 0.957 | +0.001 |
| S3 | drop | 0.887 | 0.664 | **−0.223** |
| S3 | stale | 0.949 | 0.951 | +0.002 |

## Findings

### 1. There is no simultaneity bias

If the same-step IC were inflated by self-reference, lagging the classification would produce *better* MSE — the classifier would see a less biased decision surface. Instead, lagging produces *worse* MSE on every scenario × mode where there is any difference at all, by 28 % to 66 % on the drop-mode signal-rich cases. The same-step IC is genuinely informative; there is no statistical artefact to remove.

This is the cleanest evidence so far that the WP2 IC computation is well-formed. The Gaussian-mixture self-reference (each reading contributes one component of N to its own integrand background) is part of the IC definition, not a bug; the self-component contributes ≈ 1/N of the mixture mass and the integral is well-defined for any N ≥ 2.

### 2. Lag effect is asymmetric across scenarios and delay modes

The pattern in the table above:

- **Drop-mode signal-rich scenarios (S1, S3) suffer most**: lag = 1 raises MSE by 43–66 %, drops structure correlation by 0.12–0.22.
- **Stale-mode S1**: lag = 1 raises MSE by 28 %, but only slightly drops structure correlation (−0.01).
- **S2 (dense, low delay) and S3 stale**: essentially no effect (≤ 1 % MSE, ≤ 0.002 SC).

Two things drive this:

- **Detection latency.** Under drop mode, an anomalous reading is excluded from i's consensus only when i's classifier flags it. A one-step lag means each just-emerged anomaly pollutes consensus for one extra step before exclusion. On a sparse network with few accessible neighbours (S1 ring, S3 random-sparse), there are few clean alternatives to dilute the polluted reading, so the per-step penalty propagates into MSE.
- **Effective absorption capacity.** Under stale mode the consensus already integrates messages from delays of 1–4 steps; an additional 1-step lag in the classifier is absorbed by the existing temporal averaging. On S2 (fully connected at delay 0.3) the abundance of accessible neighbours similarly washes out single-clock pollution.

So lag matters when (a) the consensus has few accessible neighbours and (b) the architecture has no other source of temporal averaging. That is precisely the drop-mode-on-sparse-network regime.

### 3. The lagged variant is strictly dominated under WP2/WP3 architecture

There is no scenario × mode where lag = 1 helps. The proposal's `ADMEC-full-lagged` configuration is operationally inferior to the default same-step classification across the entire ablation menu, and DG-2 is therefore not rescued (or rescuable) by removing simultaneity bias — there was no bias to begin with.

## Combined WP3 final picture

This entry closes the systematic WP3 sweep. Five ablations done:

| # | Ablation | Best admec_full effect | DG-2 rescue? |
|---|----------|------------------------|:------------:|
| 1 | Delay convention (entry 008) | stale: −38–44 % S1/S3 MSE | No |
| 2 | Threshold sweep (entry 011) | thr 1.5: −58 %/−59 % S1 drop / S3 stale | No |
| 3 | Constraint sensitivity (entry 009) | var_loose: −33 % S3 stale | No |
| 4 | Two-vs-three-way (entry 010) | δ = 0 (architectural) | No (formally impossible) |
| 5 | Lagged classification (this entry) | lag=1 hurts; lag=0 already optimal | No (and not needed) |

**Combined design tuning** (stale + var_loose + threshold 1.5 + same-step classification) takes admec_full S3 from 0.741 (WP2) to ~0.19 (WP3 best). Still 8 × worse than centralised `imm` 0.025. The information-theoretic ceiling (50 nodes pooled vs ~3-neighbour local consensus) holds.

## DG-2 / DG-3 final verdict (WP3 sweep complete)

| Gate / sub-criterion | Status | Where addressed |
|----------------------|--------|-----------------|
| DG-1 | Closed (one mitigated failure) | entries 001–003, 006 |
| DG-2 | NOT MET (S2 only; even with WP3 retuning, S3 gap = 8×) | entry 007 + WP3 entries |
| DG-2b | NOT MET (strict-STRUCTURED TPR ≈ 0.7 %) | entry 007 |
| DG-3 constraint clause | satisfied | entries 007, 009 |
| DG-3 three-way > two-way | NOT MET (architecturally impossible; δ = 0) | entry 010 |

The negative gates are robust to all five ablations. The architecture is internally coherent and a cleanly tunable estimator family, but the centralised information-theoretic advantage on sparse delayed networks cannot be closed by classifier or constraint tuning alone.

## What this does and does not show

**It does show:**
- No simultaneity bias in the WP2 IC computation; the same-step IC is the right operating point.
- Detection latency carries a meaningful MSE penalty (28–66 %) on drop-mode signal-rich scenarios with sparse accessible neighbourhoods.
- The penalty vanishes when the architecture already has temporal averaging (stale mode) or abundant accessible neighbours (S2). This complements the ablation-1 finding that drop-mode locality starves consensus.
- DG-2 cannot be rescued by lagging classification.

**It does not show:**
- That all forms of lag would hurt. A *signal-aware* lag (e.g. classify on a smoothed IC trace) might do something different. WP3's pre-registered design is the simplest one (single-step delay); cross-axis exploration is out of scope.

## Files changed

| File | Change |
|------|--------|
| `src/estimators.py` | `admec_full` gains `classification_lag: int = 0` parameter |
| `scripts/wp3_ablation_lagged_classification.py` | New: 3 scenarios × 10 seeds × 2 modes × 2 lags = 120 runs |
| `data/wp3_ablation_lagged_classification_20260505.npz` | New: ablation archive |

## Strategic note for project lead

With the WP3 systematic sweep complete, the residual question is no longer "what to tune?" but "what to redesign?" The ablations show:

- The architecture has a real noise-absorption mechanism (constraint layer) that pays off when paired with aggressive exclusion (entry 011).
- The structural ceiling on sparse delayed networks (~8 × on S3) is information-theoretic, not architectural; it cannot be closed by tuning.
- The three-way / two-way distinction is architecturally invisible to the consensus stage (entry 010).

Two redesign directions could plausibly change DG-2 or DG-3:

1. **STRUCTURED with reduced weight** (rather than excluded): would make the three-way distinction operationally meaningful and could improve structure correlation on the scenarios where STRUCTURED actually fires (currently 5–6 cells per S1/S2 run, 6 per S3 run; rare but non-zero).
2. **Hierarchical or decayed-staleness weighting** (rather than binary drop/stale): would let admec_full use partial information from delayed neighbours rather than a binary cutoff. Could push the local consensus closer to the centralised CRB on S3.

Both are non-trivial code changes, not parameter sweeps. For the present project's writeup, the recommendation is to treat the WP3 sweep as a clean characterisation result — "per-reading thresholds optimised for null detection are suboptimal for consensus, the constraint layer's role is variance absorption, and the structured/unstructured split is invisible at the consensus stage" — and reserve redesigns for a follow-up project.

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for code prototyping and structural editing.*

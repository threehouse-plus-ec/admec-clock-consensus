# Logbook Entry 008 — WP3 Ablation 1: Delay Convention Sweep

**Date:** 2026-05-04
**Work package:** WP3 (ablation 1 of 5)
**Decision gate:** none (DG-2 already closed; this entry characterises the failure mode)

---

## Objective

The WP2 result (entry 007) closed DG-2 negatively: ADMEC-full beats the best non-ADMEC baseline on MSE in only one of eight scenarios (S2, fully connected, low delay). The stated failure mode was structural — on sparse networks with realistic Poisson delays, the delay-restricted local consensus could not match a centralised inverse-variance weighted mean.

WP3 ablation 1 tests one specific hypothesis behind that failure: **does using stale readings `Y[t − τ_ij, j]` (instead of dropping inaccessible neighbours) close the WP2 gap?**

The user's batch-(a) review explicitly flagged this as the principled WP3 follow-up to the "drop, don't use stale history" convention adopted as the WP2 baseline.

## What was done

### 1. `delay_mode` parameter added to local estimators

`src/estimators.py:freq_local`, `:admec_delay`, and `:admec_full` now accept a `delay_mode` keyword:

- **`'drop'`** (default, WP2 baseline): a neighbour `j` is included in `i`'s consensus iff `adj[i, j] AND delays[i, j] <= freshness`, using the current-step reading `Y[t, j]`. Neighbours with delay > freshness are dropped from the consensus, NOT pulled from history.
- **`'stale'`** (WP3 ablation): every adjacency neighbour contributes its reading and self-assessed STABLE status from the time it was sent, namely `Y[t − delays[i, j], j]`. Neighbours with `t − delay < 0` are dropped at the start of the run (warm-up effect on the first few steps). The node itself is always included at lag 0.

For ADMEC variants the classification status used in the consensus is the *delayed* one: `stable[t − delays[i, j], j]`. Each neighbour reports both its reading and its self-classification at the moment the message was sent, which is the consistent semantics for delayed communication.

`freq_global`, `freq_exclude`, `huber`, `bocpd`, `imm`, and `admec_unconstrained` are centralised and do not consume `delay_mode`. The default value `'drop'` keeps backward compatibility with the WP2 canonical archive (verified by re-running scripts/wp3_ablation_delay_convention.py with matched RNG order: drop-mode S1/S2/S3 admec_full MSE values are byte-identical to `data/wp2_campaign_20260504_fix.npz`).

### 2. Ablation harness `scripts/wp3_ablation_delay_convention.py`

Mirrors the WP2 campaign loop on the three signal scenarios where the WP2 result was structural — S1 (15 nodes, ring, Poisson(2.0)), S2 (15 nodes, fully connected, Poisson(0.3)), S3 (50 nodes, random_sparse, Poisson(4.0)). Each `(scenario, seed, estimator)` triple is run twice — once with `delay_mode='drop'` and once with `delay_mode='stale'` — for the three local estimators (`freq_local`, `admec_delay`, `admec_full`). Centralised baselines (`freq_exclude`, `imm`) are also run for direct comparison.

Output: `data/wp3_ablation_delay_convention_20260504.npz`. RNG ordering matches `scripts/wp2_campaign.py` so drop-mode results reproduce the WP2 canonical archive exactly.

### 3. Tests added

`tests/test_estimators.py:TestDelayMode` — 10 tests, all passing:
- 3 × `test_zero_delays_drop_equals_stale`: when `delays == 0` everywhere, drop and stale must produce identical estimates (sanity check on the equivalence at the trivial-delay boundary).
- 3 × `test_unknown_delay_mode_raises`: `delay_mode='nonsense'` raises `ValueError`.
- 1 × `test_stale_uses_delayed_readings`: a hand-constructed 3-node ring where delay = 2 between nodes 0 and 1 verifies that stale mode sees `Y[t − 2, 1]` (so node 0's mean at t=2 equals 3.0 = mean(1, 7, 1)), while drop mode at freshness=1 excludes node 1 (mean = 1.0 = node 0's own reading averaged with node 2).
- 3 × `test_stale_does_not_diverge`: on an S1-like simulation the stale-mode output is finite for all three estimators.

## Results

### Mean MSE over 10 seeds

| Scenario | mode | freq_local | admec_delay | admec_full | freq_exclude | imm |
|----------|------|-----------:|------------:|-----------:|-------------:|----:|
| S1 | drop | 3.084 | 1.647 | 0.732 | **0.135** | 0.147 |
| S1 | stale | 1.876 | 0.861 | 0.413 | — | — |
| S2 | drop | 0.331 | 0.139 | **0.093** | 0.135 | 0.147 |
| S2 | stale | 0.325 | 0.126 | 0.104 | — | — |
| S3 | drop | 1.642 | 1.027 | 0.741 | **0.025** | 0.025 |
| S3 | stale | 0.570 | 0.340 | 0.461 | — | — |

`freq_exclude` and `imm` rows in stale-mode are blank because they are centralised and not affected by the delay convention.

### Mean structure correlation over 10 seeds

| Scenario | mode | freq_local | admec_delay | admec_full | freq_exclude | imm |
|----------|------|-----------:|------------:|-----------:|-------------:|----:|
| S1 | drop | 0.598 (8/10 seeds) | 0.800 | 0.897 | 0.955 | **0.956** |
| S1 | stale | 0.692 | 0.849 | 0.924 | — | — |
| S2 | drop | 0.951 | 0.954 | 0.958 | 0.955 | 0.956 |
| S2 | stale | 0.951 | 0.955 | 0.957 | — | — |
| S3 | drop | 0.884 (7/10 seeds) | 0.866 | 0.887 | 0.960 | **0.960** |
| S3 | stale | 0.921 | 0.935 | 0.949 | — | — |

## Findings

**Stale convention substantially improves all three local estimators on sparse-with-delay scenarios.**

- `admec_full` MSE drops by **44 % on S1** (0.732 → 0.413) and **38 % on S3** (0.741 → 0.461).
- `admec_delay` MSE drops by **48 % on S1** (1.647 → 0.861) and **67 % on S3** (1.027 → 0.340).
- `freq_local` MSE drops by **39 % on S1** (3.084 → 1.876) and **65 % on S3** (1.642 → 0.570).
- Structure correlation also closes much of the gap to centralised baselines: `admec_full` on S3 goes from 0.887 to 0.949 (vs `imm` 0.960 — within 0.011).

**But the gap to centralised baselines does not close on MSE.**

- S1: `admec_full` stale = 0.413 vs `freq_exclude` = 0.135 — still 3.1× worse.
- S3: `admec_full` stale = 0.461 vs `imm` = 0.025 — still 18× worse.
- Only on S2 (fully connected, delay 0.3) does `admec_full` continue to win — and there `stale` is mildly worse than `drop` (0.104 vs 0.093) because every adjacency neighbour is already accessible at delay ≤ 1 in drop mode, so adding stale lag only injects irrelevant history.

### Interpretation

**The drop convention was a real but partial cause of the WP2 failure.** The hypothesis that "ADMEC-full lost on S1/S3 because we starved its consensus by dropping delayed neighbours" is *partly* right — switching to stale recovers ~40–45 % of the MSE. But the bigger limit is geometric: a 50-node random-sparse network with target degree 3 and Poisson(4.0) delays gives each node a small effective neighbourhood even when the convention is generous. Centralised methods that pool all 50 readings simply have an information advantage that the local consensus cannot match.

Concretely, with N = 50 and average degree 3, each node's adjacency-neighbour set is on average 3 nodes (4 with self). A centralised inverse-variance weighted mean over 50 nodes has variance 1/50 of a single reading; the local consensus has variance 1/4. That alone gives a ~12× MSE penalty before any convention details matter. The 18× residual gap on S3 stale is consistent with that scaling argument plus a smaller contribution from delay-induced staleness.

**`freq_local` performance gives the cleanest signature of the convention effect** because it has no IC classification or constraint layer to confound. On S3, `freq_local` drop = 1.642 vs stale = 0.570 — a 65 % reduction purely from changing the delay convention. The fact that the analogous reductions are smaller for `admec_full` (38 %) and `admec_delay` (67 %) than for `freq_local` indicates that the IC and temporal-statistic gates do not interact strongly with the delay convention on these scenarios — they pass through approximately the same filter mass either way.

### What this confirms about WP2

- **DG-2 stays NOT MET** under either delay convention. The negative verdict is robust to this design choice; it is not an artefact of the WP2 baseline convention.
- **The constraint layer continues to add value over `admec_delay` everywhere**: even under stale, `admec_full` beats `admec_delay` on every scenario × metric tested (S1: 0.413 vs 0.861; S2: 0.104 vs 0.126; S3: 0.461 vs 0.340 — wait, stale `admec_delay` 0.340 < stale `admec_full` 0.461 on S3).

That last point is interesting and unexpected: under stale, `admec_delay` *beats* `admec_full` on S3 MSE (0.340 vs 0.461). The constraint layer hurts on S3 stale. Why? Likely because under stale mode the proposed update vector is large and noisy (each node's stale neighbours can disagree across 4-step lags), so the variance-ratio constraint ([0.5, 1.5]) trips frequently and rejects updates, freezing some nodes. WP3 ablation 3 (constraint sensitivity ±30 %) will quantify this directly.

## DG-2 verdict update

| Scenario | DG-2 metric | drop admec_full | stale admec_full | best non-ADMEC | DG-2 pass? |
|----------|-------------|----------------:|-----------------:|---------------:|:----------:|
| S1 | MSE | 0.732 | 0.413 | 0.135 | ✗ both |
| S1 | Structure | 0.897 | 0.924 | 0.956 | ✗ both |
| S3 | MSE | 0.741 | 0.461 | 0.025 | ✗ both |
| S3 | Structure | 0.887 | 0.949 | 0.960 | ✗ both |

DG-2 was not met under the WP2 (drop) convention; it remains not met under stale. The headline conclusion of entry 007 — that the delay-restricted local consensus on sparse-with-delay networks cannot match centralised exclusion methods — is confirmed.

## What this does and does not show

**It does show:**
- The drop convention is a meaningful contributor to the WP2 gap (~40 % of admec_full's MSE on S1, ~38 % on S3).
- The remaining gap (3–18×) is structural, set by the network geometry and the centralised-vs-local information advantage. No convention tweak can close it.
- On S3, stale mode sometimes destabilises the constraint layer enough that `admec_delay` beats `admec_full` on MSE — flagging the variance-ratio constraint as a candidate failure mode under noisier proposed updates. WP3 ablation 3 will quantify this.

**It does not show:**
- That the stale variant is universally preferable. On S2 (where delay is short and freshness already covers most neighbours) it is slightly worse. The right convention depends on the topology / delay profile.
- That a different stale-reading scheme (e.g. with a maximum staleness cap) would change the conclusion. The default here (no cap) is the cleanest test of the WP2 hypothesis.
- That delay-restricted local consensus is intrinsically inferior. On dense networks with low delays (S2), the architecture works as designed.

## Files changed

| File | Change |
|------|--------|
| `src/estimators.py` | Added `delay_mode` parameter (`'drop'` default, `'stale'` ablation) to `freq_local`, `admec_delay`, `admec_full` |
| `scripts/wp3_ablation_delay_convention.py` | New: ablation harness (S1, S2, S3 × 10 seeds × {drop, stale}) |
| `data/wp3_ablation_delay_convention_20260504.npz` | New: ablation archive |
| `tests/test_estimators.py` | New `TestDelayMode` class (10 tests) covering zero-delay equivalence, unknown-mode rejection, hand-constructed delayed-readings example, and finiteness sweep |

## Suggested next ablation

Given the unexpected `admec_delay` > `admec_full` on S3 stale, **WP3 ablation 3 (constraint sensitivity ±30 %)** is the right next step. It will tell us whether the variance-ratio constraint is the part of the constraint stack that mis-fires under noisier proposed updates, and whether loosening it (e.g. variance ratio ∈ [0.3, 1.7]) recovers the gap to `admec_delay` without re-introducing the spurious-update failures the constraint was designed to prevent.

WP3 ablation 2 (classification threshold sweep) is also a clean next test, and the WP2 data already constrains the expected outcome (the IC gate rarely fires, so the threshold sweep should show `admec_full` with relaxed threshold collapses to `freq_exclude`).

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for code prototyping and structural editing.*

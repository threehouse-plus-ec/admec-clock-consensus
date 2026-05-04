# Logbook Entry 009 — WP3 Ablation 3: Update-Size Constraint Sensitivity (±30 %)

**Date:** 2026-05-04
**Work package:** WP3 (ablation 3 of 5)
**Decision gate:** none (DG-2 already closed; this entry characterises the failure mode)

---

## Objective

Ablation 1 (entry 008) found an unexpected ordering on S3 stale: `admec_delay` (mean MSE 0.340) beats `admec_full` (0.461). Under drop mode the ordering is conventional (`admec_full` 0.732 < `admec_delay` 1.647); only under stale, where the proposed update vector picks up extra variance from multi-step lags across neighbours, does the constraint layer hurt rather than help.

The hypothesis raised in entry 008 was that the variance-ratio bound `[0.5, 1.5]` is over-tight when proposed updates are noisier — the post-update ratio `var(state + Δ) / var(state)` lands outside the bound more often, so the constraint rejects updates that would have been beneficial. Ablation 3 tests this directly by sweeping the three constraint axes at ±30 % per the proposal's pre-registered design.

## What was done

`scripts/wp3_ablation_constraint_sensitivity.py` runs `admec_full` on the same three scenarios from ablation 1 (S1, S2, S3) over 10 seeds (RNG order matched to `scripts/wp2_campaign.py`), under both delay modes, with seven `ConstraintParams` variants:

| variant | `max_step_factor` | `energy_factor` | `var_ratio_min` | `var_ratio_max` |
|--------:|------------------:|----------------:|----------------:|----------------:|
| `baseline` | 3.0 | 1.0 | 0.5 | 1.5 |
| `step_loose` | 3.9 | 1.0 | 0.5 | 1.5 |
| `step_tight` | 2.1 | 1.0 | 0.5 | 1.5 |
| `energy_loose` | 3.0 | 1.3 | 0.5 | 1.5 |
| `energy_tight` | 3.0 | 0.7 | 0.5 | 1.5 |
| `var_loose` | 3.0 | 1.0 | 0.35 | 1.65 |
| `var_tight` | 3.0 | 1.0 | 0.65 | 1.35 |

Each scenario × mode × variant cell averages 10 seeds. The harness also runs `admec_delay` once per (scenario, seed, mode) as the comparator (no constraint params consumed). Output: `data/wp3_ablation_constraint_sensitivity_20260504.npz`.

## Results

### `admec_full` mean MSE over 10 seeds

| Scenario | mode | baseline | step_loose | step_tight | energy_loose | energy_tight | var_loose | var_tight | `admec_delay` |
|----------|------|---------:|-----------:|-----------:|-------------:|-------------:|----------:|----------:|--------------:|
| S1 | drop | 0.732 | 0.765 | 0.731 | 0.691 | 0.594 | 0.830 | 0.659 | 1.647 |
| S1 | stale | 0.413 | 0.393 | 0.374 | 0.440 | 0.384 | 0.408 | 0.521 | 0.861 |
| S2 | drop | 0.093 | 0.093 | 0.093 | 0.092 | 0.094 | 0.095 | 0.134 | 0.139 |
| S2 | stale | 0.104 | 0.104 | 0.104 | 0.104 | 0.102 | 0.103 | 0.118 | 0.126 |
| S3 | drop | 0.741 | 0.739 | 0.746 | 0.847 | 0.593 | 0.757 | 0.721 | 1.027 |
| **S3** | **stale** | **0.461** | 0.460 | 0.453 | 0.495 | **0.343** | **0.307** | 0.586 | **0.340** |

`admec_full` mean structure correlation over 10 seeds:

| Scenario | mode | baseline | step_loose | step_tight | energy_loose | energy_tight | var_loose | var_tight | `admec_delay` |
|----------|------|---------:|-----------:|-----------:|-------------:|-------------:|----------:|----------:|--------------:|
| S1 | drop | 0.897 | 0.890 | 0.897 | 0.905 | 0.912 | 0.883 | 0.908 | 0.800 |
| S1 | stale | 0.924 | 0.926 | 0.929 | 0.921 | 0.925 | 0.923 | 0.913 | 0.849 |
| S2 | drop | 0.958 | 0.958 | 0.958 | 0.958 | 0.958 | 0.958 | 0.957 | 0.954 |
| S2 | stale | 0.957 | 0.957 | 0.957 | 0.957 | 0.956 | 0.957 | 0.956 | 0.955 |
| S3 | drop | 0.887 | 0.887 | 0.886 | 0.882 | 0.894 | 0.887 | 0.889 | 0.866 |
| S3 | stale | 0.949 | 0.949 | 0.949 | 0.949 | 0.945 | 0.942 | 0.953 | 0.935 |

## Findings

### 1. Variance-ratio bound was the binding constraint on S3 stale

**`var_loose` [0.35, 1.65] reduces S3 stale MSE from 0.461 to 0.307 (−33 %), recovering the conventional ordering `admec_full < admec_delay`** (0.307 vs 0.340). This is direct confirmation of the entry-008 hypothesis: the variance-ratio constraint was rejecting too many updates when the proposed update vector picked up extra variance from multi-step lags across stale neighbours. Loosening the bound by 30 % at each end was sufficient to restore the constraint's intended role (smoothing without over-rejecting).

**`var_tight` [0.65, 1.35] worsens S3 stale MSE to 0.586** (+27 % vs baseline). The direction is consistent: tightening the variance-ratio bound makes the over-rejection problem worse.

The three other axes have only modest effects on S3 stale: `step_*` and `energy_loose` move MSE by a few percent or worsen it; only `energy_tight` materially helps (0.461 → 0.343, −26 %). The latter is interesting and a touch counterintuitive: tightening the *energy* ceiling on a noisy proposed update vector forces uniform shrinkage onto the energy ball, which acts like a soft variance regulariser. It does not, however, fully recover the `var_loose` improvement.

### 2. The fix does not close the gap to centralised baselines

The S3 best-baseline target on MSE is `imm` = 0.025 (or `freq_exclude` 0.025; both are essentially the centralised inverse-variance weighted mean). Even `var_loose` admec_full at 0.307 is **12 × worse** than this floor. The ratio is consistent with the information-theoretic argument in entry 008: a centralised mean over 50 nodes has variance 1/50 of a single reading; a local consensus over ~3 adjacency neighbours plus self has variance 1/4. The ~12 × gap between these is set by network geometry, not by any constraint tuning.

The same picture holds on S1: even the best variant (`step_tight` stale 0.374, `energy_tight` drop 0.594) leaves the gap to `freq_exclude` 0.135 wide open (~3 × on S1 stale).

**DG-2 stays NOT MET across all 14 (delay mode × constraint variant) admec_full configurations on S1 and S3.** The negative verdict is robust to both dimensions of design choice that the proposal's pre-registered ablation menu identified as candidates for rescue.

### 3. The constraint axes affect the three scenarios differently

S2 (fully connected, low delay) is essentially insensitive to the step and energy axes: every drop-mode admec_full from 0.092 to 0.094 is within Monte-Carlo noise of the baseline 0.093. The only S2 variant that meaningfully changes things is `var_tight`, which raises drop-mode MSE from 0.093 to 0.134 — close to the WP2 baseline `freq_exclude` 0.135. So even the small S2 win can be wiped out by an over-tight variance-ratio bound, but the default value is not the binding constraint there.

S1 drop responds most strongly to `energy_tight` (0.732 → 0.594, −19 %), suggesting the energy bound is a soft regulariser that helps on noisy ring topologies even without stale-reading.

S3 drop responds to `energy_tight` (0.741 → 0.593, −20 %) but not to `var_loose` (0.741 → 0.757, +2 %). Under drop the variance-ratio constraint isn't binding on S3; only when stale lags inject extra noise into the proposed update does the constraint start to over-reject. This is the cleanest evidence that the binding constraint depends on the noise structure of the proposed update, which the delay convention modulates.

### 4. Structure correlation is largely insensitive to constraint tuning

On all six (scenario, mode) cells, structure correlation varies by < 0.04 across the seven variants. The only nontrivial change is `var_tight` on S3 stale (+0.004 vs baseline) — a positive result that suggests tighter bounds slightly improve signal preservation on the residual at the cost of higher MSE. This is the conventional trade-off between absorption and rejection in robust consensus, but the magnitude is small.

## Interpretation

Combined with entry 008, ablations 1 and 3 jointly characterise the WP2 failure mode:

- **The "drop" convention contributed roughly 40 % of the WP2 admec_full MSE on S1 and S3** (entry 008): switching to "stale" reduces MSE by 38–44 %.
- **Among constraint axes, the variance-ratio bound is the only one that drives a qualitative change** on S3 stale: `var_loose` (and `energy_tight` to a lesser extent) recover the conventional `admec_full < admec_delay` ordering and improve absolute MSE by another 33 %.
- **Both effects combined** (`stale` mode + `var_loose` constraint variant) bring S3 admec_full to 0.307 — a 58 % reduction from the WP2 baseline (0.741) and within reach of `admec_delay` (0.340) but still 12 × worse than centralised `imm` (0.025).

The remaining 12 × gap is structural and unrescuable by design tuning. It is set by the centralised-vs-local information advantage in a 50-node network with ~3-degree adjacency, exactly as the simple Cramér-Rao argument predicts.

**This closes the WP3 design-tuning question.** Tuning the delay convention or the constraint thresholds can take admec_full from "ridiculous" (S3 drop 0.741) to "reasonable" (S3 stale + var_loose 0.307), but it cannot close the gap to centralised baselines on sparse networks with delays. Ablation 2 (classification threshold sweep), 4 (two-vs-three-way), and 5 (admec-full-lagged) remain in the WP3 menu, but none of them addresses the geometric ceiling identified above; they will refine the picture but cannot rescue DG-2.

## DG-2 verdict update

| Scenario | metric | best admec_full (mode + variant) | best non-ADMEC | DG-2 pass? |
|----------|--------|---------------------------------:|---------------:|:----------:|
| S1 | MSE | 0.374 (stale, step_tight) | freq_exclude 0.135 | ✗ (still 2.8 ×) |
| S1 | structure | 0.929 (stale, step_tight) | imm 0.956 | ✗ |
| S3 | MSE | 0.307 (stale, var_loose) | imm 0.025 | ✗ (still 12 ×) |
| S3 | structure | 0.953 (stale, var_tight) | imm 0.960 | ✗ (within 0.007) |

The S3 structure-correlation gap is now within Monte-Carlo noise (0.953 vs 0.960, 10 seeds). MSE remains the binding metric and confirms DG-2 NOT MET.

## What this does and does not show

**It does show:**
- The variance-ratio bound was the binding constraint under stale-mode noisier proposed updates, exactly as ablation 1 predicted. Loosening to [0.35, 1.65] recovers the conventional ordering `admec_full < admec_delay` on S3 stale.
- The constraint architecture is internally repairable: a single hyper-parameter shift restores the constraint layer's intended role.
- The remaining gap to centralised baselines on S3 (12 ×) is structural — no constraint tuning closes it.
- Constraint sensitivity is heavily scenario-dependent: S2 is almost insensitive, S1 drop is most sensitive to `energy_tight`, S3 stale is most sensitive to `var_loose`.

**It does not show:**
- **That the WP3-recommended `var_loose` setting is universally preferable.** Cross-scenario MSE deltas vs baseline:

  | scenario × mode | baseline | var_loose | delta |
  |-----------------|---------:|----------:|------:|
  | S3 stale | 0.461 | 0.307 | **−33.5 %** |
  | S2 stale | 0.104 | 0.103 | −1.6 % |
  | S1 stale | 0.413 | 0.408 | −1.3 % |
  | S2 drop | 0.093 | 0.095 | +2.2 % |
  | S3 drop | 0.741 | 0.757 | +2.2 % |
  | **S1 drop** | **0.732** | **0.830** | **+13.4 %** |

  `var_loose` is **scenario-specific, not a blanket recommendation**: it is a clear win on S3 stale, roughly neutral on five of six (scenario, mode) cells, and a meaningful regression on S1 drop where the +13.4 % hurt arises because under the WP2 baseline (drop) the variance-ratio bound was *helping* on the noisy ring topology. Adopting `var_loose` globally would trade a 33 % S3-stale gain for a 13 % S1-drop loss.

  The operational recommendation is conditional: use `var_loose` *only when* the proposed update vector inherits extra variance from multi-step lags (i.e. when paired with stale-reading mode on a sparse high-delay topology). The right cross-scenario default would set `var_ratio_min/max` adaptively from the per-step proposed-update statistics — not a tuning question this entry resolves.
- That constraint tuning is irrelevant. It moves admec_full from "embarrassing" to "respectable" on S3, even if it cannot close the gap to centralised methods. For applications where local consensus is required by design (decentralised networks without a global aggregator), the WP3 tuning is operationally important.
- That further multi-axis exploration (e.g. `var_loose × energy_tight`) might find a deeper optimum. The pre-registered ±30 % single-axis design is what the proposal called for; cross-axis sweeps are out of scope here.

## Files changed

| File | Change |
|------|--------|
| `scripts/wp3_ablation_constraint_sensitivity.py` | New: 7-variant × 2-mode × 3-scenario × 10-seed harness |
| `data/wp3_ablation_constraint_sensitivity_20260504.npz` | New: ablation archive |

## Suggested next ablation

Ablation 4 (two-way vs three-way) — the WP2 strict-STRUCTURED TPR was 0.7 % (entry 007), which already suggests the structured/unstructured distinction adds little. WP3 ablation 4 closes that question and addresses DG-3's "three-way > two-way" sub-criterion directly. Ablation 2 (classification threshold sweep) remains a hygiene check; given the per-reading 2.976-bit threshold's selectivity (entry 006) and the freq_exclude ≡ admec_unconstrained equivalence in WP2, the expected outcome is a flat curve.

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for code prototyping and structural editing.*

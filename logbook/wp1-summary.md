# WP1 Summary — Calibration and Positioning of Information Content

**Status:** Work Package 1 complete. DG-1 closed. No outstanding criteria.

---

## Objective

WP1 defined and calibrated a pointwise observable — information content (IC) — for quantifying distributional inconsistency in clock data, established its behaviour under controlled null conditions, and positioned it relative to established figures of merit. IC is model-free at the signal level but calibrated under specific null noise assumptions.

## What was defined

**Information content (IC).** For an ensemble of N observations x₁, …, x_N with declared per-point uncertainties σ₁, …, σ_N, define the Gaussian-mixture background density:

> P(y) = (1/N) Σᵢ 𝒩(y; xᵢ, σᵢ)

The interval probability for point k is the probability mass assigned by P(y) to the interval [x_k − σ_k, x_k + σ_k]:

> p_k = ∫ from x_k − σ_k to x_k + σ_k of P(y) dy

evaluated analytically via the Gaussian CDF. The information content is:

> I_k = −log₂(p_k)   [bits]

High IC indicates that point k is unlikely given the ensemble's self-declared noise — the interval around x_k captures little probability mass under the mixture background. The interval width is set by σ_k, so IC depends both on the mixture background (which determines the density being integrated) and on the declared local uncertainty scale (which determines the integration window). This dual dependence is the structural reason for the σ-sensitivity results reported below. IC requires no parametric model for the anomaly itself; the Gaussian-mixture structure enters only through the null calibration.

**AIPP (average information per point).** The ensemble-level aggregate:

> AIPP = (1/N) Σ_k I_k

Under the Gaussian null with σ_data = σ_declared = 1, as N → ∞ the mixture P(y) converges to 𝒩(0, σ = √2) — the convolution of the data distribution with the Gaussian kernel — giving AIPP → 1.25 bit. The earlier estimate of 0.55 bit (based on the self-contribution alone) was incorrect; see logbook Entry 001 for the derivation and correction.

**δ_min (effect-size thresholds).** Minimum temporal-structure effect sizes that separate structured from unstructured anomalies, computed over a trailing window of W = 20 time steps. Two statistics:

- *Trailing variance slope:* linear regression of log(running variance) over sub-windows of size W/4 within the trailing window. δ_min = 0.2105, calibrated as 3 × median(|slope|) under the hardest null (Student-t with ν = 3 — heavy tails create sporadic variance spikes in sub-windows).
- *Trailing lag-1 autocorrelation:* sample autocorrelation at lag 1 over the trailing window. δ_min = 0.8703, calibrated as the 95th percentile of |autocorrelation| under the hardest null (random walk — inherently non-stationary, with strong serial dependence).

The two statistics use different calibration methods because the variance slope is unbounded (so a multiplier-based threshold is natural), while autocorrelation is bounded to [−1, 1] (so a percentile-based threshold avoids exceeding the domain). All calibrations were performed at N = 50 with T = 200 time steps and 300 realisations per noise model.

## What was demonstrated

**Calibration under nulls.** AIPP converges to the theoretical limit within 5% at N ≥ 100 and within 1% at N ≥ 200. The 95th-percentile anomaly-detection threshold is stable within a factor of 1.24× across all ten tested null models: Gaussian i.i.d., heteroscedastic Gaussian, Student-t (ν = 3, 5), AR(1) (ρ = 0.7, 0.9), symmetric Pareto (α = 2.5, 3.0), fractional Gaussian noise (H = 0.9, via Davies-Harte circulant embedding), and random walk (cumulative sum of i.i.d. Gaussian increments). The pre-registered ×1.5 stability criterion is satisfied with margin. Finite-N bias follows AIPP(N) ≈ 1.248 − 0.913/N + 1.02/N² and is below 1% for N ≥ 75; for smaller samples, the correction −0.9/N bit is available.

**Sensitivity analysis.** IC is robust under random ±20% perturbation of declared uncertainties (AIPP shift +1.2%) and under systematic overestimation (+20% → AIPP shift −12.7%). Systematic underestimation (−20%) produces a 19.3% AIPP shift, exceeding the pre-registered 15% bound. This is the single identified failure in WP1. IC is not invariant under rescaling or misestimation of declared uncertainties; it inherits any systematic bias present in σ. The asymmetry is expected: underestimating σ narrows the integration interval, capturing less probability mass from the mixture background, so AIPP rises. The mitigation adopted for WP2 is worst-case threshold calibration — procedural, not intrinsic.

**Temporal-structure thresholds.** The δ_min values were calibrated from null distributions of variance slope and lag-1 autocorrelation across all ten noise models. Sanity checks confirm that realistic injected signals — sinusoidal drift (amplitude 2σ, period 50 steps) and linearly growing variance (σ(t) = 1 + 0.03t) — exceed their respective δ_min values. The three-way classification rule is fully specified.

**Positioning against established figures of merit.** A controlled comparison (20 clocks, T = 200 steps, one clock with linear drift 0.02/step, seed 2026) showed that the per-point squared normalised residual (χ²) amplifies deviations quadratically, Huber loss (Huber 1981; c = 1.345) bounds their influence linearly beyond its threshold, and IC compresses them logarithmically through the probability transform.

| Property | χ² / residuals | Huber loss | Allan deviation | IC / AIPP |
|----------|---------------|------------|-----------------|-----------|
| Scale behaviour | quadratic | linear beyond threshold | N/A (variance scaling) | logarithmic (via probability) |
| Dependence on σ | explicit, quadratic | explicit | implicit (via noise model) | explicit, nonlinear |
| Additivity | yes (sum of squares) | yes | no (windowed statistic) | yes (information units) |
| Tail sensitivity | very high | bounded | not designed for outliers | distribution-dependent |
| Temporal structure | none | none | scaling only | none (pointwise) |

IC does not replace these measures. It provides a complementary quantity: a scale-normalised, additive measure of self-consistency with respect to declared uncertainties. Unlike χ², it is directly interpretable in probabilistic terms; unlike robust losses, it does not encode a decision policy; and unlike Allan deviation, it does not rely on specific noise-scaling assumptions. Allan deviation (Allan 1966) characterises temporal frequency stability — it is not a pointwise diagnostic and is not directly comparable to IC, χ², or Huber on a per-sample basis. IC's primary role is to separate the detection of inconsistency from its subsequent interpretation.

## What was not solved

WP1 does not demonstrate that IC improves timekeeping or enables better consensus performance. It does not provide a complete taxonomy of anomaly types beyond the binary structured/unstructured distinction defined by δ_min. It does not resolve whether the separation of detection and interpretation — the architectural choice being tested — yields measurable advantage at the network level. These are WP2 questions.

IC remains a pointwise observable. It does not distinguish between random and structured deviations — that distinction requires the temporal-structure layer (variance slope, lag-1 autocorrelation) calibrated via δ_min. Alone, IC can flag that a clock is anomalous but cannot say whether the anomaly is a one-off outlier or a persistent drift.

## Resulting classification rule

```
STABLE:               IC < threshold_95
STRUCTURED ANOMALY:   IC ≥ threshold_95  AND  (|var_slope| > 0.2105  OR  |autocorr| > 0.8703)
UNSTRUCTURED ANOMALY: IC ≥ threshold_95  AND  |var_slope| ≤ 0.2105  AND  |autocorr| ≤ 0.8703
```

where threshold_95 is the 95th-percentile AIPP value from the null calibration (Entry 001), recalibrated under worst-case σ conditions (systematic −20% underestimation, Entry 002). The variance slope and autocorrelation are computed over a trailing window of W = 20 time steps.

## Decision gate outcome

DG-1 closed with one identified limitation: systematic σ-underestimation exceeds the pre-registered 15% sensitivity bound (actual: 19.3%). The 15% criterion was not relaxed post hoc. The failure is recorded, and the mitigation (worst-case threshold calibration) is adopted for WP2. All other DG-1 sub-criteria pass.

## Transition to WP2

WP2 will evaluate whether the separation of inconsistency detection (IC) and temporal-structure classification (δ_min) enables improved handling of anomalous clocks at the network level. The comparison set includes frequentist weighted averaging, Huber M-estimation (Huber 1981), Bayesian online changepoint detection (Adams & MacKay 2007), and an interacting multiple model filter (Blom & Bar-Shalom 1988). Clock noise parameters are drawn from published hydrogen maser characterisations (Panfilo & Arias 2019). Both positive and negative results will be published.

## References

1. Allan, D. W. Statistics of atomic frequency standards. *Proc. IEEE* **54**, 221–230 (1966).
2. Huber, P. J. *Robust Statistics* (Wiley, 1981).
3. Blom, H. A. P. & Bar-Shalom, Y. The interacting multiple model algorithm. *IEEE Trans. Automat. Contr.* **33**, 780–783 (1988).
4. Adams, R. P. & MacKay, D. J. C. Bayesian online changepoint detection. Preprint arXiv:0710.3742 (2007).
5. Scheffer, M. et al. Early-warning signals for critical transitions. *Nature* **461**, 53–59 (2009).
6. Dakos, V. et al. Methods for detecting early warnings of critical transitions. *PLoS ONE* **7**, e41010 (2012).
7. Lisdat, C. et al. A clock network for geodesy and fundamental science. *Nat. Commun.* **7**, 12443 (2016).
8. Panfilo, G. & Arias, F. The Coordinated Universal Time (UTC). *Metrologia* **56**, 042001 (2019).
9. Bothwell, T. et al. Resolving the gravitational redshift across a millimetre-scale atomic sample. *Nature* **602**, 420–424 (2022).

## Artefacts

| Artefact | Location |
|----------|----------|
| Logbook Entries 001–005 | `logbook/` |
| IC implementation | `src/ic.py` |
| Noise generators | `src/noise.py` |
| Temporal-structure statistics | `src/temporal.py` |
| Comparison functions | `src/comparison.py` |
| Test suite (88 tests, 86 passing) | `tests/` |
| Archived data (entries 001–005) | `data/` |
| Outreach document | `docs/outreach.md` |

---

*Author: U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*
*AI tools (Claude, Anthropic) were used for structural editing and code prototyping. All scientific content, decisions, and claims are the sole responsibility of the author.*

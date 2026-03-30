"""
Information Content (IC) — interval-probability definition.

IC measures distributional inconsistency: how improbable is each observation
under the ensemble's own background distribution?

    P(y) = (1/N) Σ_i  N(y; x_i, σ_i)

    p_k = ∫_{x_k - σ_k}^{x_k + σ_k} P(y) dy

    I_k = -log₂(p_k)

IC requires no parametric signal model but is calibrated under specific
null noise assumptions. The term "model-free" refers to the absence of a
parametric signal model, not to the absence of distributional assumptions
in calibration.

Status: STUB. Implementation is WP1.
"""

# TODO (WP1):
# 1. Implement compute_ic(values, sigmas) using analytic Gaussian CDF
# 2. Verify AIPP → 0.55 bit for Gaussian i.i.d. null
# 3. Null-model calibration: Gaussian, heteroscedastic, Student-t, power-law, AR(1), 1/f
# 4. Finite-N bias quantification
# 5. σ-sensitivity analysis (±20%)
# 6. Percentile thresholds (95th, 99th)
#
# Decision gate DG-1:
#   PASS: AIPP ≈ 0.55 (±5%), thresholds stable ×1.5, σ-robust
#   FAIL: halt project

raise NotImplementedError("WP1 not yet started. This module is a stub.")

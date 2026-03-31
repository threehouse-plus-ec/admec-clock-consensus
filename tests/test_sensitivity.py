"""
Tests for σ-sensitivity analysis — WP1/DG-1.

DG-1 σ-sensitivity criterion (chosen BEFORE running the test):
    AIPP shift < 15% relative under ±20% σ perturbation.
    i.e. AIPP stays within [1.25 × 0.85, 1.25 × 1.15] ≈ [1.06, 1.44] bit
    for all three perturbation conditions (random, systematic+, systematic-).

Additionally: 95th-percentile threshold shift < 20% relative under
perturbation (anomaly-detection operating point stability).
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, aipp_gaussian_limit, perturb_sigmas


# --- Pass criterion, defined before any results ---
AIPP_RELATIVE_SHIFT_LIMIT = 0.15  # 15% relative
THRESHOLD_RELATIVE_SHIFT_LIMIT = 0.20  # 20% relative
PERTURBATION_MAGNITUDE = 0.2  # ±20%


class TestPerturbSigmas:
    """Unit tests for the perturbation function itself."""

    def test_random_range(self):
        """Random perturbations stay within ±magnitude."""
        rng = np.random.default_rng(42)
        sigmas = np.ones(1000)
        perturbed = perturb_sigmas(sigmas, mode='random', magnitude=0.2, rng=rng)
        ratios = perturbed / sigmas
        assert np.all(ratios >= 0.8 - 1e-10)
        assert np.all(ratios <= 1.2 + 1e-10)

    def test_random_distribution(self):
        """Random perturbations are approximately uniform."""
        rng = np.random.default_rng(42)
        sigmas = np.ones(10_000)
        perturbed = perturb_sigmas(sigmas, mode='random', magnitude=0.2, rng=rng)
        ratios = perturbed / sigmas
        # Mean should be ≈ 1.0 (uniform on [0.8, 1.2])
        assert abs(np.mean(ratios) - 1.0) < 0.01
        # Std should be ≈ 0.4/√12 ≈ 0.1155
        assert abs(np.std(ratios) - 0.4 / np.sqrt(12)) < 0.01

    def test_systematic_positive(self):
        """Systematic+ gives exactly σ × 1.2."""
        sigmas = np.array([1.0, 2.0, 0.5])
        perturbed = perturb_sigmas(sigmas, mode='systematic+', magnitude=0.2)
        np.testing.assert_allclose(perturbed, sigmas * 1.2)

    def test_systematic_negative(self):
        """Systematic- gives exactly σ × 0.8."""
        sigmas = np.array([1.0, 2.0, 0.5])
        perturbed = perturb_sigmas(sigmas, mode='systematic-', magnitude=0.2)
        np.testing.assert_allclose(perturbed, sigmas * 0.8)

    def test_positivity_guaranteed(self):
        """Even large perturbations cannot produce σ ≤ 0."""
        sigmas = np.array([0.01, 0.001])
        perturbed = perturb_sigmas(sigmas, mode='systematic-', magnitude=0.99)
        assert np.all(perturbed > 0)

    def test_zero_perturbation_is_identity(self):
        """Zero magnitude returns original sigmas."""
        sigmas = np.array([1.0, 2.0, 3.0])
        perturbed = perturb_sigmas(sigmas, mode='random', magnitude=0.0,
                                   rng=np.random.default_rng(42))
        np.testing.assert_allclose(perturbed, sigmas)

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            perturb_sigmas(np.ones(5), mode='bogus')

    def test_baseline_match(self):
        """AIPP under zero perturbation matches unperturbed baseline."""
        rng = np.random.default_rng(99)
        values = rng.normal(0, 1, 200)
        sigmas = np.ones(200)
        ic_base = compute_ic(values, sigmas)
        ic_pert = compute_ic(values, perturb_sigmas(sigmas, mode='random',
                                                     magnitude=0.0, rng=rng))
        np.testing.assert_allclose(compute_aipp(ic_base), compute_aipp(ic_pert))


class TestSigmaSensitivityAIPP:
    """
    DG-1 σ-sensitivity test: AIPP shift < 15% relative under ±20% perturbation.

    Criterion defined BEFORE running:
        |AIPP_perturbed - AIPP_baseline| / AIPP_baseline < 0.15

    Tested at N = 50 and N = 200 (to check finite-size interaction).
    """

    def _run_sensitivity(self, n, n_realisations, mode, rng):
        """Run AIPP computation under given perturbation mode."""
        aipps_base = []
        aipps_pert = []
        for _ in range(n_realisations):
            values = rng.normal(0, 1, n)
            sigmas_true = np.ones(n)
            sigmas_pert = perturb_sigmas(sigmas_true, mode=mode,
                                         magnitude=PERTURBATION_MAGNITUDE, rng=rng)
            ic_base = compute_ic(values, sigmas_true)
            ic_pert = compute_ic(values, sigmas_pert)
            aipps_base.append(compute_aipp(ic_base))
            aipps_pert.append(compute_aipp(ic_pert))
        return np.array(aipps_base), np.array(aipps_pert)

    @pytest.mark.parametrize("n", [50, 200])
    @pytest.mark.parametrize("mode", ['random', 'systematic+', 'systematic-'])
    def test_aipp_shift_bounded(self, n, mode):
        """AIPP shift under σ-perturbation stays within 15% relative."""
        rng = np.random.default_rng(2026)
        aipps_base, aipps_pert = self._run_sensitivity(n, 300, mode, rng)

        mean_base = np.mean(aipps_base)
        mean_pert = np.mean(aipps_pert)
        relative_shift = abs(mean_pert - mean_base) / mean_base

        assert relative_shift < AIPP_RELATIVE_SHIFT_LIMIT, (
            f"N={n}, mode={mode}: AIPP shifted {relative_shift:.3f} "
            f"(base={mean_base:.4f}, pert={mean_pert:.4f}), "
            f"limit is {AIPP_RELATIVE_SHIFT_LIMIT}"
        )


class TestSigmaSensitivityThreshold:
    """
    Threshold stability under σ-perturbation.

    The 95th-percentile AIPP threshold should not shift more than 20%
    relative under perturbation — otherwise the anomaly-detection
    operating point is fragile even if the mean AIPP is robust.
    """

    @pytest.mark.parametrize("mode", ['random', 'systematic+', 'systematic-'])
    def test_threshold_shift_bounded(self, mode):
        """95th-percentile threshold shift < 20% relative."""
        rng = np.random.default_rng(2026)
        n = 50
        n_real = 300

        aipps_base = []
        aipps_pert = []
        for _ in range(n_real):
            values = rng.normal(0, 1, n)
            sigmas_true = np.ones(n)
            sigmas_pert = perturb_sigmas(sigmas_true, mode=mode,
                                         magnitude=PERTURBATION_MAGNITUDE, rng=rng)
            ic_base = compute_ic(values, sigmas_true)
            ic_pert = compute_ic(values, sigmas_pert)
            aipps_base.append(compute_aipp(ic_base))
            aipps_pert.append(compute_aipp(ic_pert))

        p95_base = np.percentile(aipps_base, 95)
        p95_pert = np.percentile(aipps_pert, 95)
        relative_shift = abs(p95_pert - p95_base) / p95_base

        assert relative_shift < THRESHOLD_RELATIVE_SHIFT_LIMIT, (
            f"mode={mode}: 95th percentile shifted {relative_shift:.3f} "
            f"(base={p95_base:.4f}, pert={p95_pert:.4f}), "
            f"limit is {THRESHOLD_RELATIVE_SHIFT_LIMIT}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

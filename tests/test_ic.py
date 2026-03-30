"""
Tests for IC module — WP1 validation.

These tests constitute the first part of DG-1:
    - AIPP converges to ~0.55 bit for Gaussian i.i.d.
    - IC handles edge cases correctly
    - σ-verification flags discrepancies
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, compute_ti, aipp_gaussian_limit, verify_sigmas
from scipy.special import erf


class TestComputeIC:
    """Core IC computation tests."""

    def test_single_point(self):
        """Single point: IC = -log2(erf(1/√2)) (self-contribution only)."""
        ic = compute_ic(np.array([0.0]), np.array([1.0]))
        expected = -np.log2(erf(1.0 / np.sqrt(2.0)))  # ≈ 0.5507
        assert len(ic) == 1
        assert abs(ic[0] - expected) < 1e-10

    def test_empty(self):
        """Empty input returns empty."""
        ic = compute_ic(np.array([]), np.array([]))
        assert len(ic) == 0

    def test_shape_mismatch(self):
        """Mismatched shapes raise ValueError."""
        with pytest.raises(ValueError, match="same shape"):
            compute_ic(np.array([1.0, 2.0]), np.array([1.0]))

    def test_negative_sigma(self):
        """Negative σ raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            compute_ic(np.array([1.0, 2.0]), np.array([1.0, -0.5]))

    def test_zero_sigma(self):
        """Zero σ raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            compute_ic(np.array([1.0, 2.0]), np.array([1.0, 0.0]))

    def test_2d_input_rejected(self):
        """2-D input raises ValueError."""
        with pytest.raises(ValueError, match="1-D"):
            compute_ic(np.ones((3, 2)), np.ones((3, 2)))

    def test_ic_nonnegative(self):
        """IC is always ≥ 0 (probability ≤ 1)."""
        rng = np.random.default_rng(42)
        values = rng.normal(0, 1, 50)
        sigmas = np.ones(50)
        ic = compute_ic(values, sigmas)
        assert np.all(ic >= 0)

    def test_outlier_has_higher_ic(self):
        """An outlier should have higher IC than an inlier."""
        values = np.array([0.0, 0.1, -0.1, 0.05, -0.05, 10.0])
        sigmas = np.ones(6)
        ic = compute_ic(values, sigmas)
        # The outlier (10.0) should have the highest IC
        assert np.argmax(ic) == 5

    def test_identical_points(self):
        """All identical points: each has IC from self-contribution only."""
        values = np.ones(20)
        sigmas = np.ones(20)
        ic = compute_ic(values, sigmas)
        # All points are at the same location. The mixture P(y) is
        # N(y; 1, 1) (all components identical), so p = erf(1/√2) ≈ 0.683.
        # IC ≈ 0.55 bit (self-contribution limit).
        expected = -np.log2(erf(1.0 / np.sqrt(2.0)))
        assert np.allclose(ic, expected, atol=1e-6)

    def test_heteroscedastic(self):
        """Works with heterogeneous σ values."""
        rng = np.random.default_rng(123)
        values = rng.normal(0, 1, 30)
        sigmas = rng.uniform(0.5, 2.0, 30)
        ic = compute_ic(values, sigmas)
        assert ic.shape == (30,)
        assert np.all(np.isfinite(ic))


class TestAIPPGaussianConvergence:
    """
    DG-1 core test: does AIPP converge to the theoretical limit?

    For Gaussian i.i.d. with σ_data = σ_declared = 1:
        AIPP → ~1.25 bit as N → ∞

    The large-N limit arises because the mixture P(y) converges to
    N(0, √2) (convolution of data distribution with kernel), not to
    the self-contribution alone.
    """

    @pytest.fixture
    def theoretical_limit(self):
        return aipp_gaussian_limit(sigma_data=1.0, sigma_declared=1.0)

    @pytest.mark.parametrize("n", [10, 20, 50, 100, 200, 500, 1000])
    def test_convergence(self, n, theoretical_limit):
        """AIPP approaches theoretical limit with increasing N."""
        rng = np.random.default_rng(2026)
        n_realisations = 200
        aipps = []
        for _ in range(n_realisations):
            values = rng.normal(0, 1, n)
            sigmas = np.ones(n)
            ic = compute_ic(values, sigmas)
            aipps.append(compute_aipp(ic))

        mean_aipp = np.mean(aipps)
        std_aipp = np.std(aipps)

        # At N ≥ 100, mean AIPP should be within 5% of limit (DG-1 criterion)
        if n >= 100:
            relative_error = abs(mean_aipp - theoretical_limit) / theoretical_limit
            assert relative_error < 0.05, (
                f"N={n}: AIPP={mean_aipp:.4f} ± {std_aipp:.4f}, "
                f"expected {theoretical_limit:.4f}, "
                f"relative error {relative_error:.3f} > 0.05"
            )

    def test_finite_n_bias_direction(self, theoretical_limit):
        """At small N, AIPP variance is higher but mean is close to limit."""
        rng = np.random.default_rng(2026)
        n_realisations = 500
        aipps_small = []
        for _ in range(n_realisations):
            values = rng.normal(0, 1, 10)
            sigmas = np.ones(10)
            ic = compute_ic(values, sigmas)
            aipps_small.append(compute_aipp(ic))

        mean_small = np.mean(aipps_small)
        std_small = np.std(aipps_small)

        # At N=10, AIPP should still be in the right ballpark (within 20%)
        # but with much higher variance than at large N
        relative_error = abs(mean_small - theoretical_limit) / theoretical_limit
        assert relative_error < 0.20, (
            f"AIPP(N=10) = {mean_small:.4f} ± {std_small:.4f}, "
            f"expected ~{theoretical_limit:.4f}, "
            f"relative error {relative_error:.2f} > 0.20"
        )
        # Variance at N=10 should be substantially higher than at N=1000
        aipps_large = []
        for _ in range(200):
            values = rng.normal(0, 1, 1000)
            sigmas = np.ones(1000)
            ic = compute_ic(values, sigmas)
            aipps_large.append(compute_aipp(ic))
        assert std_small > 2 * np.std(aipps_large), (
            f"Expected higher variance at N=10 ({std_small:.4f}) "
            f"than at N=1000 ({np.std(aipps_large):.4f})"
        )


class TestAIPPThresholdStability:
    """
    DG-1 test: are percentile thresholds stable across noise models?

    Criterion: 95th percentile thresholds stable within ×1.5.
    """

    def _compute_null_aipp_distribution(self, noise_model, n, n_realisations, rng):
        """Compute AIPP distribution under a null noise model."""
        aipps = []
        for _ in range(n_realisations):
            if noise_model == "gaussian":
                values = rng.normal(0, 1, n)
                sigmas = np.ones(n)
            elif noise_model == "heteroscedastic":
                log_sigmas = rng.normal(0, 0.5, n)
                sigmas = np.exp(log_sigmas)
                values = rng.normal(0, sigmas)
            elif noise_model == "student_t_3":
                values = rng.standard_t(3, n)
                sigmas = np.ones(n) * np.sqrt(3)  # theoretical std of t(3) = √(ν/(ν-2))
            elif noise_model == "student_t_5":
                values = rng.standard_t(5, n)
                sigmas = np.ones(n) * np.sqrt(5 / 3)
            elif noise_model == "ar1_07":
                # AR(1) with ρ = 0.7
                values = np.zeros(n)
                values[0] = rng.normal()
                for i in range(1, n):
                    values[i] = 0.7 * values[i - 1] + rng.normal() * np.sqrt(1 - 0.7**2)
                sigmas = np.ones(n)
            else:
                raise ValueError(f"Unknown noise model: {noise_model}")

            ic = compute_ic(values, sigmas)
            aipps.append(compute_aipp(ic))

        return np.array(aipps)

    def test_threshold_stability(self):
        """95th percentile AIPP thresholds within ×1.5 across noise models."""
        rng = np.random.default_rng(2026)
        n = 50
        n_real = 300

        models = ["gaussian", "heteroscedastic", "student_t_3", "student_t_5", "ar1_07"]
        thresholds = {}

        for model in models:
            aipps = self._compute_null_aipp_distribution(model, n, n_real, rng)
            thresholds[model] = np.percentile(aipps, 95)

        # Check pairwise ratios within ×1.5
        thresh_values = list(thresholds.values())
        for i in range(len(thresh_values)):
            for j in range(i + 1, len(thresh_values)):
                ratio = max(thresh_values[i], thresh_values[j]) / min(thresh_values[i], thresh_values[j])
                assert ratio < 1.5, (
                    f"Threshold ratio {ratio:.2f} between "
                    f"{models[i]} ({thresh_values[i]:.3f}) and "
                    f"{models[j]} ({thresh_values[j]:.3f}) exceeds ×1.5"
                )


class TestSigmaVerification:
    """Tests for the σ-verification protocol."""

    def test_consistent_sigmas_no_flags(self):
        """Consistent σ values produce no flags."""
        rng = np.random.default_rng(42)
        t = 100
        sigma = 1.0
        values = rng.normal(0, sigma, t)
        sigmas = np.ones(t) * sigma
        flags = verify_sigmas(values, sigmas, window=20)
        # Most points should not be flagged
        flag_rate = np.mean(flags[20:])
        assert flag_rate < 0.2, f"Flag rate {flag_rate:.2f} too high for consistent σ"

    def test_misspecified_sigma_flagged(self):
        """Grossly misspecified σ produces flags."""
        rng = np.random.default_rng(42)
        t = 100
        values = rng.normal(0, 5.0, t)  # actual σ = 5
        sigmas = np.ones(t) * 1.0  # declared σ = 1 (5× too small)
        flags = verify_sigmas(values, sigmas, window=20)
        # Most points after window should be flagged
        flag_rate = np.mean(flags[20:])
        assert flag_rate > 0.8, f"Flag rate {flag_rate:.2f} too low for misspecified σ"


class TestAggregates:
    """Tests for AIPP and TI."""

    def test_aipp_of_zeros(self):
        assert compute_aipp(np.array([])) == 0.0

    def test_ti(self):
        ic = np.array([1.0, 2.0, 3.0])
        assert compute_ti(ic) == 6.0

    def test_aipp(self):
        ic = np.array([1.0, 2.0, 3.0])
        assert abs(compute_aipp(ic) - 2.0) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

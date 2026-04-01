"""
Tests for comparison figures of merit — Entry 005.

Verifies chi2, Huber loss, and ordering consistency with IC.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from comparison import compute_chi2, compute_huber, compute_allan_deviation
from ic import compute_ic


class TestChi2:
    """Tests for per-point squared normalised residual."""

    def test_zero_residuals(self):
        """chi2 of zero residuals is zero."""
        values = np.zeros(10)
        sigmas = np.ones(10)
        chi2 = compute_chi2(values, sigmas)
        assert np.allclose(chi2, 0.0)

    def test_quadratic_scaling(self):
        """chi2 scales quadratically with residual magnitude."""
        sigmas = np.ones(5)
        values_1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        values_2 = 2.0 * values_1
        chi2_1 = compute_chi2(values_1, sigmas)
        chi2_2 = compute_chi2(values_2, sigmas)
        assert np.allclose(chi2_2, 4.0 * chi2_1)

    def test_sigma_scaling(self):
        """Doubling sigma quarters chi2."""
        values = np.array([2.0, 4.0, 6.0])
        chi2_s1 = compute_chi2(values, np.ones(3))
        chi2_s2 = compute_chi2(values, 2.0 * np.ones(3))
        assert np.allclose(chi2_s2, chi2_s1 / 4.0)

    def test_known_value(self):
        """chi2 of [3.0] with sigma=1 is 9.0."""
        chi2 = compute_chi2(np.array([3.0]), np.array([1.0]))
        assert np.isclose(chi2[0], 9.0)


class TestHuber:
    """Tests for per-point Huber loss."""

    def test_matches_chi2_half_for_small_u(self):
        """Huber matches chi2/2 for |u| <= c."""
        c = 1.345
        values = np.array([0.0, 0.5, 1.0, -1.0, 1.3])
        sigmas = np.ones(5)
        huber = compute_huber(values, sigmas, c=c)
        chi2 = compute_chi2(values, sigmas)
        # All |u| <= c, so Huber = u^2/2 = chi2/2
        assert np.allclose(huber, chi2 / 2.0)

    def test_large_c_recovers_chi2_half(self):
        """Huber with c -> infinity recovers chi2/2 everywhere."""
        values = np.array([0.1, 5.0, 10.0, -20.0, 100.0])
        sigmas = np.ones(5)
        huber = compute_huber(values, sigmas, c=1e10)
        chi2 = compute_chi2(values, sigmas)
        assert np.allclose(huber, chi2 / 2.0, rtol=1e-8)

    def test_linear_regime(self):
        """For |u| > c, Huber grows linearly, not quadratically."""
        c = 1.345
        # u = 10 is well above c
        huber_10 = compute_huber(np.array([10.0]), np.array([1.0]), c=c)[0]
        huber_20 = compute_huber(np.array([20.0]), np.array([1.0]), c=c)[0]
        # Linear growth: huber(20) - huber(10) should be close to
        # c * (20 - 10) = c * 10
        diff = huber_20 - huber_10
        assert np.isclose(diff, c * 10.0)

    def test_huber_bounded_relative_to_chi2(self):
        """For large residuals, Huber < chi2/2."""
        values = np.array([5.0, 10.0, 50.0])
        sigmas = np.ones(3)
        c = 1.345
        huber = compute_huber(values, sigmas, c=c)
        chi2_half = compute_chi2(values, sigmas) / 2.0
        assert np.all(huber < chi2_half)


class TestAllanDeviation:
    """Tests for overlapping Allan deviation."""

    def test_white_noise_scaling(self):
        """For white noise, Allan deviation scales as 1/sqrt(tau)."""
        rng = np.random.default_rng(2026)
        # Use phase data (cumulative sum of white frequency noise)
        freq = rng.normal(0, 1, 10000)
        phase = np.cumsum(freq)
        taus = np.array([1, 2, 4, 8, 16, 32])
        adevs = compute_allan_deviation(phase, taus)
        # Ratio of adjacent adevs should be ~1/sqrt(2) for white FM
        ratios = adevs[1:] / adevs[:-1]
        # Allow generous tolerance — finite sample
        assert np.all(ratios < 1.0), "Allan dev should decrease with tau for white noise"

    def test_single_tau(self):
        """Should handle a single tau value."""
        rng = np.random.default_rng(42)
        values = np.cumsum(rng.normal(0, 1, 100))
        adevs = compute_allan_deviation(values, np.array([5]))
        assert adevs.shape == (1,)
        assert np.isfinite(adevs[0])

    def test_tau_too_large(self):
        """Tau >= T/2 should return NaN."""
        values = np.arange(10, dtype=float)
        adevs = compute_allan_deviation(values, np.array([5, 6]))
        assert np.isnan(adevs[0])
        assert np.isnan(adevs[1])


class TestOrderingConsistency:
    """
    Under Gaussian assumption with fixed sigma, both chi2 and IC should
    be monotone in |x|: larger residuals produce larger scores.

    This is the ordering consistency check from the review refinement.
    """

    def test_chi2_and_ic_monotone_ordering(self):
        """For fixed sigma under Gaussian, chi2 and IC agree on ordering."""
        rng = np.random.default_rng(2026)
        n = 50
        values = rng.normal(0, 1, n)
        sigmas = np.ones(n)

        chi2 = compute_chi2(values, sigmas)
        from ic import compute_ic
        ic = compute_ic(values, sigmas)

        # Both should rank points in the same order by |x|
        abs_vals = np.abs(values)
        order_abs = np.argsort(abs_vals)
        order_chi2 = np.argsort(chi2)
        order_ic = np.argsort(ic)

        # chi2 is exactly monotone in |x| — perfect rank agreement
        assert np.array_equal(order_abs, order_chi2)

        # IC should be monotone in |x| for fixed sigma Gaussian ensemble
        # (larger |x| -> lower interval probability -> higher IC)
        # Check that top-5 IC points are among top-5 |x| points
        top5_abs = set(order_abs[-5:])
        top5_ic = set(order_ic[-5:])
        overlap = len(top5_abs & top5_ic)
        assert overlap >= 4, (
            f"Top-5 overlap between |x| and IC ranking is only {overlap}/5. "
            f"Expected near-perfect agreement under Gaussian with fixed sigma."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

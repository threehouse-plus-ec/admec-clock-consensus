"""
Tests for noise generators — WP1 null-model calibration.

Verifies statistical properties (tail behaviour, spectral slope,
non-stationarity) and that generators produce the expected distributions.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)


class TestParetoSymmetric:
    """Tests for symmetric Pareto generator."""

    def test_shape(self):
        rng = np.random.default_rng(42)
        values = generate_pareto_symmetric(100, alpha=2.5, rng=rng)
        assert values.shape == (100,)

    def test_centred(self):
        """Mean should be approximately zero."""
        rng = np.random.default_rng(42)
        values = generate_pareto_symmetric(10_000, alpha=3.0, rng=rng)
        assert abs(np.mean(values)) < 0.1

    def test_symmetric(self):
        """Distribution should be approximately symmetric."""
        rng = np.random.default_rng(42)
        values = generate_pareto_symmetric(10_000, alpha=3.0, rng=rng)
        # Fraction of negative values should be close to 0.5
        frac_neg = np.mean(values < 0)
        assert 0.4 < frac_neg < 0.6

    def test_heavy_tails(self):
        """Kurtosis should exceed Gaussian (3.0) for α = 2.5."""
        rng = np.random.default_rng(42)
        values = generate_pareto_symmetric(50_000, alpha=2.5, rng=rng)
        from scipy.stats import kurtosis
        k = kurtosis(values, fisher=False)  # excess=False gives raw kurtosis
        assert k > 4.0, f"Kurtosis {k:.2f} not heavy-tailed enough"

    def test_finite_variance_alpha3(self):
        """For α = 3.0, variance should be finite and reasonable."""
        rng = np.random.default_rng(42)
        values = generate_pareto_symmetric(50_000, alpha=3.0, rng=rng)
        assert np.isfinite(np.var(values))


class TestFlicker:
    """Tests for fractional Gaussian noise (fGn) generator."""

    def test_shape(self):
        rng = np.random.default_rng(42)
        values = generate_flicker(100, H=0.9, rng=rng)
        assert values.shape == (100,)

    def test_white_noise_h05(self):
        """H = 0.5 should give approximately uncorrelated noise."""
        rng = np.random.default_rng(42)
        values = generate_flicker(5000, H=0.5, rng=rng)
        # Lag-1 autocorrelation should be near zero
        r1 = np.corrcoef(values[:-1], values[1:])[0, 1]
        assert abs(r1) < 0.05, f"Lag-1 autocorrelation {r1:.3f} too high for H=0.5"

    def test_long_memory_h09(self):
        """H = 0.9 should give positive lag-1 autocorrelation."""
        rng = np.random.default_rng(42)
        values = generate_flicker(5000, H=0.9, rng=rng)
        r1 = np.corrcoef(values[:-1], values[1:])[0, 1]
        assert r1 > 0.3, f"Lag-1 autocorrelation {r1:.3f} too low for H=0.9"

    def test_finite_values(self):
        rng = np.random.default_rng(42)
        values = generate_flicker(200, H=0.9, rng=rng)
        assert np.all(np.isfinite(values))


class TestRandomWalk:
    """Tests for random-walk frequency noise."""

    def test_shape(self):
        rng = np.random.default_rng(42)
        values = generate_random_walk(100, rng=rng)
        assert values.shape == (100,)

    def test_growing_variance(self):
        """Variance of the random walk should grow with N."""
        rng = np.random.default_rng(42)
        # Generate many realisations and check variance at different points
        n_real = 500
        final_50 = []
        final_200 = []
        for _ in range(n_real):
            rw = generate_random_walk(200, rng=rng)
            final_50.append(rw[49])
            final_200.append(rw[199])
        # Var(RW at step k) = k, so var at 200 should be ~4× var at 50
        var_50 = np.var(final_50)
        var_200 = np.var(final_200)
        ratio = var_200 / var_50
        assert 2.5 < ratio < 6.0, f"Variance ratio {ratio:.2f} unexpected"

    def test_increments_are_normal(self):
        """Differences should be approximately N(0,1)."""
        rng = np.random.default_rng(42)
        rw = generate_random_walk(10_000, rng=rng)
        diffs = np.diff(rw)
        assert abs(np.mean(diffs)) < 0.05
        assert abs(np.std(diffs) - 1.0) < 0.05


class TestAR1:
    """Tests for AR(1) generator."""

    def test_shape(self):
        rng = np.random.default_rng(42)
        values = generate_ar1(100, rho=0.7, rng=rng)
        assert values.shape == (100,)

    def test_marginal_variance(self):
        """Stationary marginal variance should be ≈ 1."""
        rng = np.random.default_rng(42)
        values = generate_ar1(50_000, rho=0.9, rng=rng)
        assert abs(np.var(values) - 1.0) < 0.1

    def test_autocorrelation(self):
        """Lag-1 autocorrelation should be ≈ ρ."""
        rng = np.random.default_rng(42)
        values = generate_ar1(50_000, rho=0.9, rng=rng)
        r1 = np.corrcoef(values[:-1], values[1:])[0, 1]
        assert abs(r1 - 0.9) < 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

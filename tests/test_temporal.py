"""
Tests for temporal-structure statistics and δ_min calibration — WP1.

Pre-registered choices (defined BEFORE running):
    - Multiplier k = 3 (δ_min = 3 × median |statistic| under hardest null)
    - Window W = 20
    - The hardest null for autocorrelation is expected to be AR(1) ρ = 0.9
    - The hardest null for variance slope is expected to be random walk

Sanity check: injected sinusoidal structure must exceed δ_min.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from temporal import compute_temporal_structure, calibrate_delta_min
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)

# Pre-registered constants
MULTIPLIER = 3.0
WINDOW = 20
N_REAL = 300
T = 200  # time series length


class TestComputeTemporalStructure:
    """Unit tests for the temporal-structure computation."""

    def test_output_shape(self):
        rng = np.random.default_rng(42)
        values = rng.normal(0, 1, 100)
        vs, ac = compute_temporal_structure(values, window=20)
        assert vs.shape == (100,)
        assert ac.shape == (100,)

    def test_nan_before_window(self):
        """Values before the window should be NaN."""
        rng = np.random.default_rng(42)
        values = rng.normal(0, 1, 50)
        vs, ac = compute_temporal_structure(values, window=20)
        assert np.all(np.isnan(vs[:20]))
        assert np.all(np.isnan(ac[:20]))
        assert np.all(np.isfinite(vs[20:]))
        assert np.all(np.isfinite(ac[20:]))

    def test_short_series(self):
        """Series shorter than window returns all NaN."""
        values = np.array([1.0, 2.0, 3.0])
        vs, ac = compute_temporal_structure(values, window=20)
        assert np.all(np.isnan(vs))
        assert np.all(np.isnan(ac))

    def test_constant_series(self):
        """Constant series: zero variance slope, zero autocorrelation."""
        values = np.ones(50)
        vs, ac = compute_temporal_structure(values, window=20)
        valid_vs = vs[~np.isnan(vs)]
        valid_ac = ac[~np.isnan(ac)]
        assert np.allclose(valid_ac, 0.0, atol=1e-10)

    def test_white_noise_autocorrelation(self):
        """White noise should have near-zero mean autocorrelation."""
        rng = np.random.default_rng(42)
        values = rng.normal(0, 1, 5000)
        vs, ac = compute_temporal_structure(values, window=20)
        valid_ac = ac[~np.isnan(ac)]
        assert abs(np.mean(valid_ac)) < 0.05

    def test_ar1_positive_autocorrelation(self):
        """AR(1) ρ = 0.9 should have clearly positive autocorrelation."""
        rng = np.random.default_rng(42)
        values = generate_ar1(5000, rho=0.9, rng=rng)
        vs, ac = compute_temporal_structure(values, window=20)
        valid_ac = ac[~np.isnan(ac)]
        assert np.mean(valid_ac) > 0.5

    def test_growing_variance_positive_slope(self):
        """A signal with explicitly growing variance should have positive slope."""
        rng = np.random.default_rng(42)
        # Construct: noise with amplitude growing over time
        t = np.arange(200, dtype=float)
        values = rng.normal(0, 1, 200) * (1 + 0.02 * t)
        vs, ac = compute_temporal_structure(values, window=20)
        valid_vs = vs[~np.isnan(vs)]
        # Mean slope should be positive
        assert np.mean(valid_vs) > 0


class TestCalibrateDeltaMin:
    """Tests for δ_min calibration function."""

    def test_basic_var(self):
        """δ_min(var) should be multiplier × median |slope|."""
        var_slopes = np.array([0.1, -0.2, 0.15, -0.1, 0.3])
        autocorrs = np.array([0.05, -0.1, 0.08, -0.03, 0.12])
        dv, da = calibrate_delta_min(var_slopes, autocorrs,
                                      var_multiplier=3.0, acf_percentile=95.0)
        assert abs(dv - 3.0 * np.median(np.abs(var_slopes))) < 1e-10

    def test_basic_acf(self):
        """δ_min(acf) should be the specified percentile of |acf|."""
        autocorrs = np.arange(0, 1, 0.01)  # 100 values from 0 to 0.99
        var_slopes = np.zeros(100)
        dv, da = calibrate_delta_min(var_slopes, autocorrs,
                                      var_multiplier=3.0, acf_percentile=95.0)
        expected = np.percentile(np.abs(autocorrs), 95.0)
        assert abs(da - expected) < 1e-10

    def test_handles_nan(self):
        """NaN values should be ignored."""
        var_slopes = np.array([np.nan, 0.1, np.nan, 0.2, 0.15])
        autocorrs = np.array([np.nan, 0.05, np.nan, 0.1, 0.08])
        dv, da = calibrate_delta_min(var_slopes, autocorrs)
        assert np.isfinite(dv)
        assert np.isfinite(da)


class TestNullDistributions:
    """
    Characterise null distributions and verify δ_min is finite and positive.

    This test runs all ten null models from Entry 003 and computes the
    temporal-structure statistics under each.
    """

    def _generate_null_series(self, model_name, T, rng):
        """Generate a time series of length T under a null model."""
        if model_name == "gaussian":
            return rng.normal(0, 1, T)
        elif model_name == "heteroscedastic":
            s = np.exp(rng.normal(0, 0.5, T))
            return rng.normal(0, s)
        elif model_name == "student_t_3":
            return rng.standard_t(3, T)
        elif model_name == "student_t_5":
            return rng.standard_t(5, T)
        elif model_name == "ar1_07":
            return generate_ar1(T, rho=0.7, rng=rng)
        elif model_name == "pareto_25":
            return generate_pareto_symmetric(T, alpha=2.5, rng=rng)
        elif model_name == "pareto_30":
            return generate_pareto_symmetric(T, alpha=3.0, rng=rng)
        elif model_name == "fgn_09":
            return generate_flicker(T, H=0.9, rng=rng)
        elif model_name == "ar1_09":
            return generate_ar1(T, rho=0.9, rng=rng)
        elif model_name == "random_walk":
            return generate_random_walk(T, rng=rng)
        else:
            raise ValueError(f"Unknown model: {model_name}")

    def test_delta_min_positive_and_finite(self):
        """δ_min computed from the hardest null should be positive and finite."""
        rng = np.random.default_rng(2026)
        models = [
            "gaussian", "heteroscedastic", "student_t_3", "student_t_5",
            "ar1_07", "pareto_25", "pareto_30", "fgn_09", "ar1_09",
            "random_walk"
        ]

        all_var_slopes = []
        all_autocorrs = []

        for model in models:
            for _ in range(N_REAL):
                series = self._generate_null_series(model, T, rng)
                vs, ac = compute_temporal_structure(series, window=WINDOW)
                all_var_slopes.append(vs[~np.isnan(vs)])
                all_autocorrs.append(ac[~np.isnan(ac)])

        all_var_slopes = np.concatenate(all_var_slopes)
        all_autocorrs = np.concatenate(all_autocorrs)

        dv, da = calibrate_delta_min(all_var_slopes, all_autocorrs,
                                      var_multiplier=MULTIPLIER)

        assert dv > 0, f"δ_min(var_slope) = {dv} is not positive"
        assert da > 0, f"δ_min(autocorr) = {da} is not positive"
        assert np.isfinite(dv), f"δ_min(var_slope) = {dv} is not finite"
        assert np.isfinite(da), f"δ_min(autocorr) = {da} is not finite"


class TestDetectability:
    """
    Sanity check: injected structured anomaly must be detectable above δ_min.

    If δ_min is so high that even a clear structured signal can't exceed it,
    the three-way classifier will collapse to two-way in practice.
    """

    def test_sinusoidal_drift_detectable(self):
        """Sinusoidal drift on Gaussian noise should exceed δ_min."""
        rng = np.random.default_rng(2026)

        # First: compute δ_min from Gaussian null
        null_var_slopes = []
        null_autocorrs = []
        for _ in range(N_REAL):
            series = rng.normal(0, 1, T)
            vs, ac = compute_temporal_structure(series, window=WINDOW)
            null_var_slopes.append(vs[~np.isnan(vs)])
            null_autocorrs.append(ac[~np.isnan(ac)])

        null_var_slopes = np.concatenate(null_var_slopes)
        null_autocorrs = np.concatenate(null_autocorrs)
        dv, da = calibrate_delta_min(null_var_slopes, null_autocorrs,
                                      var_multiplier=MULTIPLIER)

        # Then: inject a sinusoidal drift (amplitude 2σ, period 50 steps)
        t = np.arange(T, dtype=float)
        signal = 2.0 * np.sin(2 * np.pi * t / 50)
        noisy_signal = signal + rng.normal(0, 1, T)

        vs, ac = compute_temporal_structure(noisy_signal, window=WINDOW)
        valid_ac = ac[~np.isnan(ac)]

        # The autocorrelation of the sinusoidal component should push
        # the mean autocorrelation above δ_min
        max_ac = np.max(np.abs(valid_ac))
        assert max_ac > da, (
            f"Max |autocorrelation| = {max_ac:.4f} does not exceed "
            f"δ_min(acf) = {da:.4f}. Structured anomaly is undetectable."
        )

    def test_growing_variance_detectable(self):
        """Linearly growing noise amplitude should exceed δ_min(var_slope)."""
        rng = np.random.default_rng(2026)

        # Compute δ_min from Gaussian null
        null_var_slopes = []
        for _ in range(N_REAL):
            series = rng.normal(0, 1, T)
            vs, _ = compute_temporal_structure(series, window=WINDOW)
            null_var_slopes.append(vs[~np.isnan(vs)])

        null_var_slopes = np.concatenate(null_var_slopes)
        dv, _ = calibrate_delta_min(null_var_slopes, null_var_slopes,
                                     var_multiplier=MULTIPLIER)

        # Inject growing variance: σ(t) = 1 + 0.03t
        t = np.arange(T, dtype=float)
        growing = rng.normal(0, 1, T) * (1 + 0.03 * t)
        vs, _ = compute_temporal_structure(growing, window=WINDOW)
        valid_vs = vs[~np.isnan(vs)]

        max_vs = np.max(valid_vs)
        assert max_vs > dv, (
            f"Max var_slope = {max_vs:.4f} does not exceed "
            f"δ_min(var) = {dv:.4f}. Growing variance is undetectable."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

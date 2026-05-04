"""
Tests for the WP2 clock model (src/clocks.py).

Verifies that the discrete-time clock simulator:
  - Reproduces the requested per-component noise levels (white,
    flicker, random walk).
  - Adds drift, signal, degradation, and heavy-tail effects in the
    expected directions.
  - Handles the four signal generators (sinusoidal, linear drift,
    step, fold bifurcation) without divergence.
  - Reports declared sigmas consistent with sigma_white *
    sigma_declared_factor * degradation_factor.

Tolerances are deliberately loose: these tests check the model's
qualitative shape, not its exact numerical values, which depend on
the noise generators upstream.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from clocks import (ClockParams, simulate_clock, simulate_network_clocks,
                    signal_sinusoidal, signal_linear_drift, signal_step,
                    signal_fold_bifurcation, hydrogen_maser,
                    build_scenario_clocks,
                    HYDROGEN_MASER_SIGMA_WHITE, HYDROGEN_MASER_SIGMA_FLICKER)


T = 2000


class TestNoiseLevels:
    """Per-component noise levels match the requested sigmas."""

    def test_white_only(self):
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=2.5)
        y, _ = simulate_clock(p, T, rng=rng)
        assert abs(np.std(y) - 2.5) / 2.5 < 0.1, (
            f"white-only std {np.std(y):.3f} too far from 2.5")

    def test_flicker_only(self):
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=0.0, sigma_flicker=1.5)
        y, _ = simulate_clock(p, T, rng=rng)
        # fGn rescaled to target std
        assert abs(np.std(y) - 1.5) / 1.5 < 0.05

    def test_random_walk_grows(self):
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=0.0, sigma_rw=0.1)
        y, _ = simulate_clock(p, T, rng=rng)
        assert np.std(y[-200:]) > np.std(y[:200]), (
            "random-walk std should grow over time")


class TestSigmaDeclared:
    """Declared sigma reflects sigma_white * factors."""

    def test_default_factor_one(self):
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=2.0)
        _, s = simulate_clock(p, 100, rng=rng)
        assert np.allclose(s, 2.0)

    def test_underestimation_factor(self):
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=2.0, sigma_declared_factor=0.8)
        _, s = simulate_clock(p, 100, rng=rng)
        assert np.allclose(s, 1.6)

    def test_degradation_scales_white_and_declared(self):
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=1.0, degradation_factor=3.0)
        y, s = simulate_clock(p, T, rng=rng)
        assert np.allclose(s, 3.0)
        assert abs(np.std(y) - 3.0) / 3.0 < 0.1


class TestSignalAdditivity:
    """Injected signals are added on top of noise."""

    def test_linear_drift_adds_trend(self):
        rng = np.random.default_rng(0)
        # No noise, just drift
        p = ClockParams(sigma_white=0.0, drift=0.5)
        y, _ = simulate_clock(p, 10, dt=1.0, rng=rng)
        np.testing.assert_allclose(y, np.arange(10) * 0.5)

    def test_sinusoidal_signal_amplitude(self):
        rng = np.random.default_rng(0)
        sig = signal_sinusoidal(amplitude=3.0, period=100.0)
        p = ClockParams(sigma_white=0.0, signal=sig)
        y, _ = simulate_clock(p, T, rng=rng)
        # Amplitude check via max
        assert np.max(y) > 2.7 and np.min(y) < -2.7

    def test_signal_onset_zero_before(self):
        rng = np.random.default_rng(0)
        sig = signal_linear_drift(rate=1.0, onset=50)
        p = ClockParams(sigma_white=0.0, signal=sig)
        y, _ = simulate_clock(p, 100, dt=1.0, rng=rng)
        assert np.all(y[:50] == 0)
        np.testing.assert_allclose(y[50:], np.arange(50) * 1.0)

    def test_step_signal(self):
        rng = np.random.default_rng(0)
        sig = signal_step(magnitude=2.0, onset=50)
        p = ClockParams(sigma_white=0.0, signal=sig)
        y, _ = simulate_clock(p, 100, dt=1.0, rng=rng)
        assert np.all(y[:50] == 0)
        assert np.all(y[50:] == 2.0)

    def test_fold_bifurcation_diverges(self):
        rng = np.random.default_rng(0)
        # Choose epsilon so r crosses zero before T
        sig = signal_fold_bifurcation(epsilon=0.005, r0=-1.0, x0=-0.9)
        p = ClockParams(sigma_white=0.0, signal=sig)
        y, _ = simulate_clock(p, 500, dt=1.0, rng=rng)
        # Initial residual stays small (pre-fold), post-fold either
        # diverges to NaN or produces a large value.
        assert np.nanmax(np.abs(y)) > 10 or np.any(np.isnan(y)), (
            "fold-bifurcation signal should escape after r crosses 0")
        # And the early part should remain bounded
        assert np.all(np.abs(y[:50]) < 5)


class TestHeavyTail:
    """Heavy-tailed clock produces more extreme readings than Gaussian."""

    def test_heavy_tail_more_extreme(self):
        rng_g = np.random.default_rng(42)
        rng_t = np.random.default_rng(42)
        gauss = ClockParams(sigma_white=1.0)
        heavy = ClockParams(sigma_white=1.0, heavy_tail_nu=3.0)
        y_g, _ = simulate_clock(gauss, T, rng=rng_g)
        y_t, _ = simulate_clock(heavy, T, rng=rng_t)
        # Heavy-tail has heavier extremes (larger 99th percentile of |y|)
        q99_g = np.percentile(np.abs(y_g), 99)
        q99_t = np.percentile(np.abs(y_t), 99)
        assert q99_t > q99_g, (
            f"Student-t(3) should produce heavier tails than Gaussian: "
            f"q99 t={q99_t:.3f} vs g={q99_g:.3f}")

    def test_heavy_tail_variance_matches(self):
        """Despite the tails, variance is still ~ sigma_white^2."""
        rng = np.random.default_rng(0)
        p = ClockParams(sigma_white=2.0, heavy_tail_nu=4.0)
        y, _ = simulate_clock(p, 5000, rng=rng)
        assert abs(np.std(y) - 2.0) / 2.0 < 0.15

    def test_heavy_tail_requires_nu_above_2(self):
        with pytest.raises(ValueError, match="heavy_tail_nu"):
            simulate_clock(ClockParams(heavy_tail_nu=2.0), 100,
                           rng=np.random.default_rng(0))


class TestNetworkSimulation:
    """simulate_network_clocks broadcasts per-clock simulation."""

    def test_shape_and_independence(self):
        rng = np.random.default_rng(0)
        params = [ClockParams(sigma_white=1.0) for _ in range(5)]
        Y, S = simulate_network_clocks(params, 200, rng=rng)
        assert Y.shape == (200, 5)
        assert S.shape == (200, 5)
        # No two columns should be identical (independent draws)
        for i in range(5):
            for j in range(i + 1, 5):
                assert not np.array_equal(Y[:, i], Y[:, j])

    def test_per_clock_signal(self):
        rng = np.random.default_rng(0)
        params = [
            ClockParams(sigma_white=0.0, signal=signal_step(1.0, 50)),
            ClockParams(sigma_white=0.0),
        ]
        Y, _ = simulate_network_clocks(params, 100, rng=rng)
        assert np.all(Y[:50, 0] == 0)
        assert np.all(Y[50:, 0] == 1.0)
        assert np.all(Y[:, 1] == 0)


class TestHydrogenMaserPreset:

    def test_default_levels(self):
        rng = np.random.default_rng(0)
        p = hydrogen_maser()
        assert p.sigma_white == HYDROGEN_MASER_SIGMA_WHITE
        assert p.sigma_flicker == HYDROGEN_MASER_SIGMA_FLICKER
        y, s = simulate_clock(p, 1000, rng=rng)
        assert np.all(s > 0)
        # Total empirical std bounded by sum-in-quadrature of components,
        # roughly sqrt(sigma_white^2 + sigma_flicker^2)
        expected = np.sqrt(p.sigma_white ** 2 + p.sigma_flicker ** 2)
        assert 0.5 * expected < np.std(y) < 2.0 * expected

    def test_degraded_3x(self):
        p = hydrogen_maser(degradation_factor=3.0)
        rng = np.random.default_rng(0)
        y, s = simulate_clock(p, 2000, rng=rng)
        assert np.allclose(s, 3 * HYDROGEN_MASER_SIGMA_WHITE)


class TestScenarioBuilder:
    """build_scenario_clocks composes per-clock settings correctly."""

    def test_signal_only_first_n(self):
        params = build_scenario_clocks(
            n=10, n_signal=3,
            signal_factory=lambda i: signal_step(1.0, 10),
            n_degraded=0,
        )
        assert sum(p.signal is not None for p in params) == 3
        assert all(p.signal is None for p in params[3:])

    def test_degraded_at_end(self):
        params = build_scenario_clocks(n=10, n_degraded=2, n_signal=0)
        assert all(p.degradation_factor == 1.0 for p in params[:8])
        assert all(p.degradation_factor == 3.0 for p in params[8:])

    def test_heavy_tail_index(self):
        params = build_scenario_clocks(n=5, n_signal=0, n_degraded=0,
                                        heavy_tail_index=2,
                                        heavy_tail_nu=3.0)
        assert params[2].heavy_tail_nu == 3.0
        for i in (0, 1, 3, 4):
            assert params[i].heavy_tail_nu is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for the update-size constraint projector (src/constraints.py).

Verifies that project_update implements the proposal's three
constraints in sequence and uses the rejection fallback for
variance-ratio violations.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from constraints import ConstraintParams, project_update, is_feasible


N = 10


def state_and_sigmas(seed=0):
    rng = np.random.default_rng(seed)
    state = rng.normal(0, 1, N)
    sigmas = np.ones(N)
    return state, sigmas


class TestPassthrough:
    """A tiny update inside all constraints passes through unchanged."""

    def test_zero_update_passes(self):
        state, sigmas = state_and_sigmas()
        upd = np.zeros(N)
        out, st = project_update(state, upd, sigmas)
        np.testing.assert_array_equal(out, np.zeros(N))
        assert not st['box_clipped']
        assert not st['energy_scaled']
        assert not st['rejected']

    def test_small_update_passes(self):
        state, sigmas = state_and_sigmas()
        rng = np.random.default_rng(1)
        upd = rng.normal(0, 0.05, N)  # tiny
        out, st = project_update(state, upd, sigmas)
        np.testing.assert_allclose(out, upd)
        assert not st['box_clipped']
        assert not st['energy_scaled']
        assert not st['rejected']


class TestBoxClipping:
    """Per-node step constraint: |delta_i| <= 3 * sigma_i."""

    def test_clips_large_per_node(self):
        # High-variance state so a 3-sigma bump on one node doesn't
        # trigger the variance-ratio fallback; we want to test the box
        # step in isolation.
        state = np.array([-3.0, 3.0] * 5)
        sigmas = np.ones(N)
        upd = np.zeros(N)
        upd[3] = 10.0  # 10x sigma -- well above 3-sigma bound
        out, st = project_update(state, upd, sigmas)
        assert st['box_clipped']
        assert not st['rejected']
        assert out[3] == pytest.approx(3.0)
        # Other entries untouched (energy budget is 10; energy = 9, fits)
        for i in range(N):
            if i != 3:
                assert out[i] == pytest.approx(0.0)

    def test_respects_per_node_sigma(self):
        state, _ = state_and_sigmas()
        sigmas = np.array([1.0] * 5 + [0.5] * 5)
        upd = np.full(N, 2.0)  # 2.0 < 3*1.0 OK on left, > 3*0.5 right
        out, st = project_update(state, upd, sigmas)
        assert st['box_clipped']
        # Left half: 2 is below 3*1, so unchanged
        assert np.all(out[:5] == 2.0) or st['energy_scaled']
        # Right half: 2 clipped to 3*0.5 = 1.5
        assert np.all(out[5:] <= 1.5 + 1e-9)


class TestEnergyScaling:
    """Total energy bound: sum(delta^2) <= N * mean(sigma^2)."""

    def test_scales_when_energy_too_large(self):
        state, sigmas = state_and_sigmas()
        # Each component 1.0, total energy = 10, energy_max = N*1 = 10
        upd = np.full(N, 1.001)  # just above
        out, st = project_update(state, upd, sigmas)
        # Should be scaled down to fit the ball
        assert st['energy_scaled']
        assert np.sum(out ** 2) <= N + 1e-6

    def test_no_scaling_within_budget(self):
        state, sigmas = state_and_sigmas()
        upd = np.full(N, 0.5)  # energy 2.5 << 10
        out, st = project_update(state, upd, sigmas)
        assert not st['energy_scaled']
        np.testing.assert_allclose(out, upd)

    def test_energy_ratio_reported(self):
        state, sigmas = state_and_sigmas()
        upd = np.full(N, 1.0)  # energy_ratio = 10 / 10 = 1.0
        _, st = project_update(state, upd, sigmas)
        assert st['energy_ratio'] == pytest.approx(1.0)


class TestVarianceRatio:
    """Variance-ratio constraint: var(state+upd)/var(state) in [0.5, 1.5]."""

    def test_collapsing_update_rejected(self):
        # Update that drives state to all-zeros should crush variance
        state = np.array([1.0, -1.0] * 5)  # var = 1
        sigmas = np.ones(N)
        upd = -state  # state + upd = 0, var ratio = 0
        out, st = project_update(state, upd, sigmas)
        # Either rejected (zeros) or sequentially clipped+rejected
        assert st['rejected']
        np.testing.assert_array_equal(out, np.zeros(N))

    def test_inflating_update_rejected(self):
        # Update doubles the deviation -> var ratio = 4 > 1.5
        state = np.array([0.5, -0.5] * 5)
        sigmas = np.ones(N)
        upd = state.copy()  # state + upd = 2*state -> var ratio = 4
        out, st = project_update(state, upd, sigmas)
        assert st['rejected']
        np.testing.assert_array_equal(out, np.zeros(N))

    def test_variance_neutral_update_passes(self):
        # Adding the same constant to every node leaves variance unchanged
        state, sigmas = state_and_sigmas()
        upd = np.full(N, 0.3)
        out, st = project_update(state, upd, sigmas)
        assert not st['rejected']
        np.testing.assert_allclose(out, upd)
        assert st['var_ratio'] == pytest.approx(1.0)


class TestEdgeCases:

    def test_scalar_sigma_broadcasts(self):
        state, _ = state_and_sigmas()
        upd = np.zeros(N)
        out, st = project_update(state, upd, sigmas=1.0)
        assert out.shape == state.shape

    def test_negative_sigma_raises(self):
        state, _ = state_and_sigmas()
        with pytest.raises(ValueError, match="sigmas must be positive"):
            project_update(state, np.zeros(N), -np.ones(N))

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError, match="must all match"):
            project_update(np.zeros(5), np.zeros(7), np.ones(5))

    def test_constant_state_passes(self):
        # Variance ratio undefined; the projector should not crash
        state = np.full(N, 2.5)
        sigmas = np.ones(N)
        upd = np.zeros(N)
        out, st = project_update(state, upd, sigmas)
        assert not st['rejected']


class TestIsFeasible:

    def test_feasible_small_update(self):
        state, sigmas = state_and_sigmas()
        upd = np.zeros(N)
        assert is_feasible(state, upd, sigmas)

    def test_infeasible_box(self):
        state, sigmas = state_and_sigmas()
        upd = np.zeros(N)
        upd[0] = 5.0  # > 3 sigma
        assert not is_feasible(state, upd, sigmas)

    def test_infeasible_energy(self):
        state, sigmas = state_and_sigmas()
        upd = np.full(N, 1.5)  # 2-sigma per node, energy 22.5 > 10
        assert not is_feasible(state, upd, sigmas)

    def test_infeasible_variance(self):
        state = np.array([1.0, -1.0] * 5)
        sigmas = np.ones(N)
        upd = -state
        assert not is_feasible(state, upd, sigmas)


class TestProjectionOrdering:
    """Sequential projection is approximate; verify it produces a feasible
    result whenever rejection is not triggered."""

    def test_post_projection_satisfies_box_and_energy(self):
        rng = np.random.default_rng(42)
        for trial in range(20):
            state = rng.normal(0, 1, N)
            sigmas = np.full(N, 1.0)
            upd = rng.normal(0, 5, N)  # likely violates box and energy
            out, st = project_update(state, upd, sigmas)
            if st['rejected']:
                continue  # not the case under test
            # Box
            assert np.all(np.abs(out) <= 3.0 + 1e-6), (
                f"trial {trial}: box violated post-projection")
            # Energy
            assert np.sum(out ** 2) <= N + 1e-6, (
                f"trial {trial}: energy violated post-projection")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

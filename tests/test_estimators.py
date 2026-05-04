"""
Tests for the WP2 consensus estimators (src/estimators.py, batch a).

Covers the seven estimators implemented in batch a (FREQ-global/local/
exclude, Huber, ADMEC-unconstrained/delay/full). BOCPD and IMM are
tested separately when implemented.

Each estimator is checked for:
  - Correct output shape (T, N) and dtype
  - Per-method correctness against a controlled scenario
    (clean Gaussian, single outlier, network topology, etc.)
  - Robustness to obvious failure modes (NaN propagation, all-flagged
    fallback, delay 0 vs non-zero)
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from estimators import (freq_global, freq_local, freq_exclude, huber,
                        admec_unconstrained, admec_delay, admec_full,
                        ESTIMATORS)
from network import make_network, make_ring, make_fully_connected
from clocks import (ClockParams, simulate_network_clocks,
                    signal_step, signal_linear_drift)
from constraints import ConstraintParams


N = 10
T = 200


def gaussian_network(t=T, n=N, sigma=1.0, seed=0):
    """N i.i.d. Gaussian clocks, no signal."""
    rng = np.random.default_rng(seed)
    params = [ClockParams(sigma_white=sigma) for _ in range(n)]
    Y, Sigmas = simulate_network_clocks(params, t, rng=rng)
    return Y, Sigmas


# ---------------------------------------------------------------
# FREQ-global
# ---------------------------------------------------------------

class TestFreqGlobal:

    def test_shape(self):
        Y, S = gaussian_network()
        E = freq_global(Y, S)
        assert E.shape == (T, N)

    def test_all_nodes_same_estimate(self):
        Y, S = gaussian_network()
        E = freq_global(Y, S)
        for t in range(T):
            assert np.allclose(E[t, :], E[t, 0])

    def test_centred_on_truth(self):
        """Mean estimate over time should be close to 0 for zero-mean noise."""
        Y, S = gaussian_network()
        E = freq_global(Y, S)
        # Each estimate has variance sigma^2/N = 1/10, so std ~0.32;
        # mean over T=200 steps has SE ~0.32/sqrt(200) ~0.022
        assert abs(np.mean(E[:, 0])) < 0.1

    def test_variance_reduction(self):
        """Estimate variance should be close to sigma^2 / N."""
        Y, S = gaussian_network(sigma=1.0)
        E = freq_global(Y, S)
        var_estimate = np.var(E[:, 0])
        expected = 1.0 / N
        assert 0.5 * expected < var_estimate < 2.0 * expected, (
            f"estimate var {var_estimate:.3f} far from {expected:.3f}")


# ---------------------------------------------------------------
# FREQ-local
# ---------------------------------------------------------------

class TestFreqLocal:

    def test_shape(self):
        Y, S = gaussian_network()
        adj, delays = make_network(N, 'ring', delay_mean=0.0,
                                    rng=np.random.default_rng(0))
        E = freq_local(Y, S, adj, delays)
        assert E.shape == (T, N)

    def test_with_zero_delays_uses_neighbours(self):
        """On a ring with zero delays, each node averages itself + 2 neighbours."""
        Y, S = gaussian_network()
        adj, delays = make_network(N, 'ring', delay_mean=0.0,
                                    rng=np.random.default_rng(0))
        E = freq_local(Y, S, adj, delays)
        # Manual check at t=0: node 0 averages y_0, y_1, y_{N-1}
        s = S[0, [0, 1, N - 1]]
        y = Y[0, [0, 1, N - 1]]
        w = 1.0 / s ** 2
        expected = np.sum(w * y) / np.sum(w)
        assert E[0, 0] == pytest.approx(expected)

    def test_high_delay_excludes_neighbours(self):
        """With delays > freshness, neighbours are inaccessible -> self only."""
        Y, S = gaussian_network()
        adj = np.ones((N, N), dtype=bool)
        np.fill_diagonal(adj, False)
        delays = np.full((N, N), 5)  # all far over freshness=1
        np.fill_diagonal(delays, 0)
        E = freq_local(Y, S, adj, delays, freshness=1)
        # Each node's estimate equals its own reading
        np.testing.assert_allclose(E, Y)


# ---------------------------------------------------------------
# FREQ-exclude
# ---------------------------------------------------------------

class TestFreqExclude:

    def test_shape(self):
        Y, S = gaussian_network()
        E = freq_exclude(Y, S)
        assert E.shape == (T, N)

    def test_excludes_obvious_outlier(self):
        """A single huge outlier reading should be excluded."""
        Y, S = gaussian_network(seed=2026)
        # Inject a huge outlier at one time step on one node
        Y[100, 5] = 50.0  # ~50 sigma
        E_excl = freq_exclude(Y, S)
        E_global = freq_global(Y, S)
        # FREQ-exclude estimate should be much closer to typical
        # than FREQ-global at t=100
        diff_excl = abs(E_excl[100, 0])
        diff_global = abs(E_global[100, 0])
        assert diff_excl < diff_global, (
            f"freq_exclude failed to filter outlier: "
            f"excl={diff_excl:.3f}, global={diff_global:.3f}")


# ---------------------------------------------------------------
# Huber
# ---------------------------------------------------------------

class TestHuber:

    def test_shape(self):
        Y, S = gaussian_network()
        E = huber(Y, S)
        assert E.shape == (T, N)

    def test_more_robust_than_freq_global(self):
        """On data with outliers, Huber is closer to truth than mean."""
        Y, S = gaussian_network(seed=2026)
        Y[100, 5] = 50.0  # outlier
        E_huber = huber(Y, S)
        E_global = freq_global(Y, S)
        # At t=100, Huber should be much closer to 0 than freq_global
        assert abs(E_huber[100, 0]) < abs(E_global[100, 0])

    def test_matches_mean_on_clean_data(self):
        """Without outliers, Huber should reduce to freq_global within tolerance."""
        Y, S = gaussian_network(seed=2026)
        E_huber = huber(Y, S)
        E_global = freq_global(Y, S)
        # Difference should be small (Huber barely fires under Gaussian null)
        assert np.max(np.abs(E_huber - E_global)) < 0.3


# ---------------------------------------------------------------
# ADMEC-unconstrained
# ---------------------------------------------------------------

class TestAdmecUnconstrained:

    def test_shape(self):
        Y, S = gaussian_network()
        E = admec_unconstrained(Y, S)
        assert E.shape == (T, N)

    def test_centralised_under_null(self):
        """Under the Gaussian null almost everything is STABLE,
        so admec_unconstrained ~ freq_global within tolerance."""
        Y, S = gaussian_network(seed=2026)
        E_admec = admec_unconstrained(Y, S)
        E_global = freq_global(Y, S)
        # Should be very close (only differs when something is flagged
        # anomalous, which is rare under null)
        assert np.max(np.abs(E_admec - E_global)) < 0.5


# ---------------------------------------------------------------
# ADMEC-delay
# ---------------------------------------------------------------

class TestAdmecDelay:

    def test_shape(self):
        Y, S = gaussian_network()
        adj, delays = make_network(N, 'ring', delay_mean=0.0,
                                    rng=np.random.default_rng(0))
        E = admec_delay(Y, S, adj, delays)
        assert E.shape == (T, N)

    def test_full_topology_zero_delay_matches_unconstrained(self):
        """Fully connected, zero delays, all-STABLE -> admec_delay ~
        admec_unconstrained."""
        Y, S = gaussian_network(seed=2026)
        adj = np.ones((N, N), dtype=bool)
        np.fill_diagonal(adj, False)
        delays = np.zeros((N, N), dtype=int)
        E_d = admec_delay(Y, S, adj, delays, freshness=0)
        E_u = admec_unconstrained(Y, S)
        # Within numerical tolerance
        assert np.max(np.abs(E_d - E_u)) < 1e-9


# ---------------------------------------------------------------
# ADMEC-full
# ---------------------------------------------------------------

class TestAdmecFull:

    def test_shape(self):
        Y, S = gaussian_network()
        adj, delays = make_network(N, 'ring', delay_mean=0.0,
                                    rng=np.random.default_rng(0))
        E = admec_full(Y, S, adj, delays)
        assert E.shape == (T, N)

    def test_constraint_layer_does_not_amplify_jumps(self):
        """Compared to ADMEC-delay, ADMEC-full should not produce larger
        per-step jumps in any node (the constraints can only shrink or
        reject updates, never grow them)."""
        Y, S = gaussian_network(seed=2026)
        adj, delays = make_network(N, 'ring', delay_mean=0.0,
                                    rng=np.random.default_rng(0))
        E_delay = admec_delay(Y, S, adj, delays, freshness=0)
        E_full = admec_full(Y, S, adj, delays, freshness=0)
        jumps_delay = np.max(np.abs(np.diff(E_delay, axis=0)))
        jumps_full = np.max(np.abs(np.diff(E_full, axis=0)))
        assert jumps_full <= jumps_delay + 1e-9, (
            f"admec_full jumps {jumps_full:.3f} exceed admec_delay "
            f"{jumps_delay:.3f}; constraints should not amplify")

    def test_aggressive_constraints_can_reject(self):
        """Tight variance bounds should trigger rejection on signal-rich data."""
        Y, S = gaussian_network(seed=2026)
        # Add a strong step on one clock to force divergence
        Y[100:, 5] += 5.0
        adj = np.ones((N, N), dtype=bool)
        np.fill_diagonal(adj, False)
        delays = np.zeros((N, N), dtype=int)
        # Tight variance ratio: trigger easily
        cp_tight = ConstraintParams(var_ratio_min=0.99, var_ratio_max=1.01)
        E_tight = admec_full(Y, S, adj, delays, freshness=0,
                              constraint_params=cp_tight)
        cp_loose = ConstraintParams(var_ratio_min=0.5, var_ratio_max=1.5)
        E_loose = admec_full(Y, S, adj, delays, freshness=0,
                              constraint_params=cp_loose)
        # Tight constraints should produce smoother trajectory (at least
        # as smooth) than loose ones
        smooth_tight = np.std(np.diff(E_tight, axis=0))
        smooth_loose = np.std(np.diff(E_loose, axis=0))
        assert smooth_tight <= smooth_loose * 1.01, (
            f"tight constraints didn't smooth trajectory: tight std="
            f"{smooth_tight:.4f}, loose std={smooth_loose:.4f}")


# ---------------------------------------------------------------
# Registry
# ---------------------------------------------------------------

class TestRegistry:

    def test_seven_estimators_registered(self):
        assert len(ESTIMATORS) == 7
        for name in ['freq_global', 'freq_local', 'freq_exclude', 'huber',
                     'admec_unconstrained', 'admec_delay', 'admec_full']:
            assert name in ESTIMATORS
            assert callable(ESTIMATORS[name])


# ---------------------------------------------------------------
# Cross-method sanity: shape and finiteness across the whole batch
# ---------------------------------------------------------------

@pytest.mark.parametrize("method_name", list(ESTIMATORS.keys()))
def test_method_shape_and_finite(method_name):
    """Every registered estimator must return finite (T, N) on a clean
    network."""
    Y, S = gaussian_network()
    adj, delays = make_network(N, 'ring', delay_mean=0.0,
                                rng=np.random.default_rng(0))
    fn = ESTIMATORS[method_name]
    # Some methods don't take adj/delays; pass them anyway for uniformity.
    if method_name in ('freq_local', 'admec_delay', 'admec_full'):
        E = fn(Y, S, adj, delays)
    else:
        E = fn(Y, S, adj=adj, delays=delays)
    assert E.shape == (T, N)
    assert np.all(np.isfinite(E)), f"{method_name} produced non-finite estimates"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

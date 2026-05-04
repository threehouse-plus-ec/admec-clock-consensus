"""
Tests for the WP2 network model (src/network.py).

Verifies:
  - Topology constructors produce the expected adjacency shape
    (degrees, symmetry, no self-loops, connectivity).
  - Delay sampling is symmetric, integer, zero off-edges, and has
    Poisson-mean behaviour at large n.
  - The make_network dispatcher returns matching adjacency/delay
    matrices for each topology.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from network import (make_ring, make_fully_connected, make_random_sparse,
                     sample_delays, make_network)


def is_symmetric(M):
    return np.array_equal(M, M.T)


def has_no_self_loops(M):
    return not np.any(np.diag(M))


def is_connected(adj):
    """Simple BFS connectivity check."""
    n = adj.shape[0]
    visited = {0}
    frontier = [0]
    while frontier:
        nxt = []
        for v in frontier:
            for w in np.where(adj[v])[0]:
                if w not in visited:
                    visited.add(w)
                    nxt.append(w)
        frontier = nxt
    return len(visited) == n


class TestRing:

    @pytest.mark.parametrize("n", [3, 5, 10, 50])
    def test_ring_degree_two(self, n):
        adj = make_ring(n)
        assert adj.shape == (n, n)
        assert is_symmetric(adj)
        assert has_no_self_loops(adj)
        degrees = adj.sum(axis=1)
        assert np.all(degrees == 2)
        assert is_connected(adj)

    def test_ring_too_small(self):
        with pytest.raises(ValueError, match="ring requires"):
            make_ring(2)


class TestFullyConnected:

    @pytest.mark.parametrize("n", [2, 5, 10])
    def test_complete_degree(self, n):
        adj = make_fully_connected(n)
        assert adj.shape == (n, n)
        assert is_symmetric(adj)
        assert has_no_self_loops(adj)
        degrees = adj.sum(axis=1)
        assert np.all(degrees == n - 1)
        assert is_connected(adj)


class TestRandomSparse:

    def test_basic_properties(self):
        rng = np.random.default_rng(0)
        adj = make_random_sparse(n=20, k=3, rng=rng)
        assert adj.shape == (20, 20)
        assert is_symmetric(adj)
        assert has_no_self_loops(adj)
        assert is_connected(adj)

    def test_average_degree_matches_target(self):
        rng = np.random.default_rng(0)
        adj = make_random_sparse(n=50, k=3, rng=rng)
        avg = adj.sum() / 50.0
        # Target degree 3, allow some slack from integer-edge rounding
        assert 2.5 < avg < 3.5

    def test_k_too_small(self):
        with pytest.raises(ValueError, match="k must be >= 2"):
            make_random_sparse(n=10, k=1, rng=np.random.default_rng(0))

    def test_k_too_large(self):
        with pytest.raises(ValueError, match="not feasible"):
            make_random_sparse(n=4, k=4, rng=np.random.default_rng(0))

    def test_reproducible(self):
        adj_a = make_random_sparse(n=20, k=3,
                                    rng=np.random.default_rng(123))
        adj_b = make_random_sparse(n=20, k=3,
                                    rng=np.random.default_rng(123))
        np.testing.assert_array_equal(adj_a, adj_b)


class TestDelays:

    def test_zero_mean_delays(self):
        adj = make_ring(10)
        rng = np.random.default_rng(0)
        delays = sample_delays(adj, delay_mean=0.0, rng=rng)
        assert delays.dtype.kind == 'i'
        assert np.all(delays == 0)

    def test_delays_symmetric(self):
        adj = make_random_sparse(n=20, k=3,
                                  rng=np.random.default_rng(0))
        delays = sample_delays(adj, delay_mean=2.0,
                               rng=np.random.default_rng(0))
        assert is_symmetric(delays)
        assert has_no_self_loops(delays)

    def test_delays_only_on_edges(self):
        adj = make_random_sparse(n=20, k=3,
                                  rng=np.random.default_rng(0))
        delays = sample_delays(adj, delay_mean=5.0,
                               rng=np.random.default_rng(0))
        assert np.all(delays[~adj] == 0)

    def test_delay_mean_at_scale(self):
        """Empirical mean of edge delays is close to the requested mean."""
        adj = make_fully_connected(40)
        rng = np.random.default_rng(0)
        delays = sample_delays(adj, delay_mean=4.0, rng=rng)
        edge_delays = delays[adj]
        # ~ 1560 edges, Poisson(4) -> sample mean within a few percent
        assert abs(np.mean(edge_delays) - 4.0) < 0.3


class TestMakeNetwork:

    @pytest.mark.parametrize("topology,expected_degree",
                              [("ring", 2), ("fully_connected", 9)])
    def test_dispatch(self, topology, expected_degree):
        rng = np.random.default_rng(0)
        adj, delays = make_network(n=10, topology=topology,
                                    delay_mean=1.0, rng=rng)
        assert adj.shape == delays.shape == (10, 10)
        if topology == "ring":
            assert np.all(adj.sum(axis=1) == 2)
        elif topology == "fully_connected":
            assert np.all(adj.sum(axis=1) == 9)
        assert is_symmetric(adj)
        assert is_symmetric(delays)
        assert np.all(delays[~adj] == 0)

    def test_random_sparse_via_dispatch(self):
        rng = np.random.default_rng(0)
        adj, delays = make_network(n=30, topology="random_sparse",
                                    delay_mean=2.0, k=3, rng=rng)
        avg = adj.sum() / 30.0
        assert 2.5 < avg < 3.5

    def test_unknown_topology(self):
        with pytest.raises(ValueError, match="Unknown topology"):
            make_network(n=10, topology="mesh",
                         rng=np.random.default_rng(0))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

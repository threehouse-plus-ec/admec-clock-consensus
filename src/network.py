"""
Network topology and communication-delay model for WP2.

Topologies:
    ring              - each node connected to 2 neighbours
    random_sparse     - random graph with target degree k (default 3)
    fully_connected   - complete graph (degree N-1)

Delays: Poisson-distributed with specified mean per topology, sampled
once at network construction. Delays are symmetric (tau_ij = tau_ji),
modelling a shared communication channel. Delays of zero correspond to
instantaneous communication. Self-loops are excluded from the
adjacency matrix and have delay zero in the delay matrix.

Poisson delays are a convenience model, not a claim about real link
statistics; they provide controllable heterogeneity in information
accessibility (per proposal sec. WP2).
"""

from typing import Optional, Tuple

import numpy as np


def make_ring(n: int) -> np.ndarray:
    """Adjacency matrix for an undirected ring on n nodes (degree 2)."""
    if n < 3:
        raise ValueError(f"ring requires n >= 3, got n={n}")
    adj = np.zeros((n, n), dtype=bool)
    for i in range(n):
        adj[i, (i + 1) % n] = True
        adj[(i + 1) % n, i] = True
    return adj


def make_fully_connected(n: int) -> np.ndarray:
    """Adjacency matrix for a complete graph on n nodes (no self-loops)."""
    if n < 2:
        raise ValueError(f"fully_connected requires n >= 2, got n={n}")
    adj = np.ones((n, n), dtype=bool)
    np.fill_diagonal(adj, False)
    return adj


def make_random_sparse(n: int,
                       k: int = 3,
                       rng: Optional[np.random.Generator] = None,
                       max_attempts: int = 50
                       ) -> np.ndarray:
    """Random graph on n nodes with target degree k.

    Constructed by taking a random spanning tree (guarantees
    connectivity), then adding random edges until the average degree
    reaches k. The realised degree of individual nodes will vary
    around k. If the spanning-tree heuristic happens to produce
    duplicate edges during the attempt phase, it retries.
    """
    if rng is None:
        rng = np.random.default_rng()
    if n < 2:
        raise ValueError(f"random_sparse requires n >= 2, got n={n}")
    if k < 2:
        raise ValueError(f"k must be >= 2 for a connected graph, got k={k}")
    if k >= n:
        raise ValueError(
            f"k={k} not feasible for n={n}; reduce k or use fully_connected.")

    target_edges = (n * k) // 2

    for _ in range(max_attempts):
        adj = np.zeros((n, n), dtype=bool)

        # Random spanning tree by random-permutation Prim
        order = rng.permutation(n)
        for i in range(1, n):
            parent = order[rng.integers(0, i)]
            child = order[i]
            adj[parent, child] = True
            adj[child, parent] = True

        n_edges = (n - 1)
        attempts = 0
        max_local = target_edges * 10
        while n_edges < target_edges and attempts < max_local:
            i, j = rng.integers(0, n, size=2)
            if i != j and not adj[i, j]:
                adj[i, j] = True
                adj[j, i] = True
                n_edges += 1
            attempts += 1
        if n_edges >= target_edges:
            return adj

    raise RuntimeError(
        f"random_sparse failed to reach target {target_edges} edges "
        f"after {max_attempts} attempts; consider increasing max_attempts.")


def sample_delays(adj: np.ndarray,
                  delay_mean: float,
                  rng: Optional[np.random.Generator] = None
                  ) -> np.ndarray:
    """Sample symmetric Poisson delays on the edges of `adj`.

    Returns
    -------
    delays : int array of shape (n, n)
        delays[i, j] = delays[j, i] = number of timesteps from i to j;
        zero on non-edges and on the diagonal.
    """
    if rng is None:
        rng = np.random.default_rng()
    n = adj.shape[0]
    delays = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j]:
                d = int(rng.poisson(delay_mean))
                delays[i, j] = d
                delays[j, i] = d
    return delays


def make_network(n: int,
                 topology: str,
                 delay_mean: float = 0.0,
                 k: int = 3,
                 rng: Optional[np.random.Generator] = None
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """Build adjacency and delay matrices for a WP2 network.

    Parameters
    ----------
    n : int
        Number of nodes.
    topology : str
        One of 'ring', 'random_sparse', 'fully_connected'.
    delay_mean : float
        Poisson mean for sampled communication delays. delay_mean=0
        gives all-zero delays (instantaneous communication).
    k : int
        Target degree for 'random_sparse' (ignored for ring or
        fully connected).
    rng : numpy Generator, optional
        Used for random_sparse construction and for delay sampling.

    Returns
    -------
    adj : bool array of shape (n, n)
        Symmetric adjacency matrix; diagonal is False.
    delays : int array of shape (n, n)
        Symmetric Poisson-sampled delays on edges; zero elsewhere.
    """
    if rng is None:
        rng = np.random.default_rng()

    if topology == 'ring':
        adj = make_ring(n)
    elif topology == 'random_sparse':
        adj = make_random_sparse(n, k=k, rng=rng)
    elif topology == 'fully_connected':
        adj = make_fully_connected(n)
    else:
        raise ValueError(
            f"Unknown topology: {topology!r}. "
            f"Use 'ring', 'random_sparse', or 'fully_connected'.")

    delays = sample_delays(adj, delay_mean, rng=rng)
    return adj, delays

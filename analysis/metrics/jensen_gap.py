"""Jensen-gap metric for topology heterogeneity."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .k_eff import mean_accessible_set_size, total_accessible_count


@dataclass(frozen=True)
class JensenGapResult:
    """Components of the topology Jensen gap."""

    expected_ratio: float
    ratio_at_k_bar: float
    gap: float
    k_bar: float


def jensen_gap(
    N: int,
    neighbor_count: np.ndarray | float,
    *,
    include_self: bool = True,
) -> float:
    """Return ``E[N/k_i] - N/k_bar``.

    The gap is non-negative for positive heterogeneous ``k_i`` by convexity,
    modulo floating-point roundoff.
    """

    return jensen_gap_components(
        N,
        neighbor_count,
        include_self=include_self,
    ).gap


def jensen_gap_components(
    N: int,
    neighbor_count: np.ndarray | float,
    *,
    include_self: bool = True,
) -> JensenGapResult:
    """Return Jensen-gap components for reporting and plotting."""

    n_nodes = _validate_n_nodes(N)
    k_total = np.asarray(
        total_accessible_count(neighbor_count, include_self=include_self),
        dtype=float,
    )
    if np.any(k_total > n_nodes):
        raise ValueError("accessible counts cannot exceed N")

    bar = mean_accessible_set_size(neighbor_count, include_self=include_self)
    expected_ratio = float(np.mean(n_nodes / k_total))
    ratio_at_bar = float(n_nodes / bar)
    return JensenGapResult(
        expected_ratio=expected_ratio,
        ratio_at_k_bar=ratio_at_bar,
        gap=expected_ratio - ratio_at_bar,
        k_bar=bar,
    )


def _validate_n_nodes(N: int) -> int:
    n_nodes = int(N)
    if n_nodes <= 0:
        raise ValueError("N must be positive")
    return n_nodes

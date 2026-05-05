"""Effective neighbourhood size metrics for exported ARP data."""

from __future__ import annotations

import numpy as np


def total_accessible_count(
    neighbor_count: np.ndarray | float,
    *,
    include_self: bool = True,
) -> np.ndarray | float:
    """Return accessible-set counts.

    By default exported ``neighbor_count`` values are interpreted as excluding
    the node itself, so one self-reading is added. Set ``include_self=False`` if
    the export already contains total accessible-set sizes.
    """

    counts = _as_nonnegative_array(neighbor_count, name="neighbor_count")
    total = counts + 1.0 if include_self else counts
    if np.any(total <= 0.0):
        raise ValueError("accessible counts must be positive")
    return _maybe_scalar(total)


def mean_accessible_set_size(
    neighbor_count: np.ndarray | float,
    *,
    include_self: bool = True,
) -> float:
    """Return ``k_bar = E[k_i(t)] + 1`` for exported neighbour counts.

    This is the *arithmetic* mean of accessible-set sizes, not a harmonic
    effective-k.  It is the appropriate average for the homogeneous reference
    ratio ``N / k_bar`` used in the Jensen-gap decomposition.
    """

    total = np.asarray(
        total_accessible_count(neighbor_count, include_self=include_self),
        dtype=float,
    )
    return float(np.mean(total))


def k_bar(
    neighbor_count: np.ndarray | float,
    *,
    include_self: bool = True,
) -> float:
    """Alias for :func:`mean_accessible_set_size`."""

    return mean_accessible_set_size(neighbor_count, include_self=include_self)


def _as_nonnegative_array(values: np.ndarray | float, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        raise ValueError(f"{name} cannot be empty")
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    if np.any(array < 0.0):
        raise ValueError(f"{name} cannot be negative")
    return array


def _maybe_scalar(values: np.ndarray) -> np.ndarray | float:
    if np.ndim(values) == 0:
        return float(values)
    return values

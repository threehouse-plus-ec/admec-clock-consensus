"""Analytic reference model for exported ADMEC campaign data.

This module is intentionally independent of the simulation package. It defines
the controlled null reference used to interpret campaign outputs:

    Var(x_cent) = 1 / sum_j sigma_j^-2
    Var(x_i)    = 1 / sum_{j in A_i} sigma_j^-2

The homogeneous reduction is the reference ratio N / k, where k is the
accessible set size including the node itself.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


ENDORSEMENT_MARKER = (
    "Local candidate framework (no parity implied with externally validated "
    "laws). The analytic reference model is an architectural lens, not a "
    "physical law. External constraints (e.g. Cramer-Rao bounds) are referenced "
    "as established coastlines, not replicated."
)


@dataclass(frozen=True)
class ReferenceAssumptions:
    """Assumptions attached to ARP reference-model outputs."""

    signal_model: str = "null model: s_j(t)=0"
    pooling_model: str = "inverse-variance weighted mean"
    noise_model: str = "independent Gaussian readings with known positive sigma"
    interpretation: str = "controlled reference, not a universal bound"
    endorsement_marker: str = ENDORSEMENT_MARKER


DEFAULT_ASSUMPTIONS = ReferenceAssumptions()


def central_variance(sigmas: np.ndarray) -> np.ndarray | float:
    """Return inverse-variance central reference variance.

    Parameters
    ----------
    sigmas:
        Positive standard deviations with shape ``(N,)`` or ``(..., N)``.
        The last axis is treated as the pooled clock axis.
    """

    sigma = _as_positive_float_array(sigmas, name="sigmas")
    information = np.sum(_inverse_variance(sigma), axis=-1)
    variance = _safe_inverse_information(information)
    return _maybe_scalar(variance)


def local_variance(
    sigmas: np.ndarray,
    accessible: np.ndarray,
    *,
    include_self: bool = False,
) -> np.ndarray:
    """Return local reference variance for each node.

    ``accessible`` is a boolean adjacency/accessibility mask where row ``i``
    marks the readings available to node ``i``. A static ``(N, N)`` mask can be
    used with either static ``(N,)`` or time-varying ``(T, N)`` sigmas. A
    time-varying ``(T, N, N)`` mask requires ``(T, N)`` sigmas.

    Set ``include_self=True`` when the exported mask contains only neighbours
    and the analytic accessible set should include each node's own reading.
    """

    sigma = _as_positive_float_array(sigmas, name="sigmas")
    mask = _as_boolean_array(accessible, name="accessible")

    if sigma.ndim == 1:
        return _local_variance_static(sigma, mask, include_self=include_self)
    if sigma.ndim == 2:
        return _local_variance_time_series(sigma, mask, include_self=include_self)

    raise ValueError("sigmas must have shape (N,) or (T, N)")


def homogeneous_mse_ratio(N: int, k_total: np.ndarray | float) -> np.ndarray | float:
    """Return the homogeneous local/central reference ratio ``N / k``.

    ``k_total`` is the accessible set size including self. Use
    :func:`homogeneous_mse_ratio_from_neighbor_count` for exported neighbour
    counts that exclude self.
    """

    n_nodes = _validate_n_nodes(N)
    k = _as_positive_float_array(k_total, name="k_total")
    if np.any(k > n_nodes):
        raise ValueError("k_total cannot exceed N")
    return _maybe_scalar(n_nodes / k)


def homogeneous_mse_ratio_from_neighbor_count(
    N: int,
    neighbor_count: np.ndarray | float,
) -> np.ndarray | float:
    """Return ``N / (neighbor_count + 1)`` for counts that exclude self."""

    counts = _as_nonnegative_float_array(neighbor_count, name="neighbor_count")
    return homogeneous_mse_ratio(N, counts + 1.0)


def _local_variance_static(
    sigma: np.ndarray,
    mask: np.ndarray,
    *,
    include_self: bool,
) -> np.ndarray:
    if mask.shape != (sigma.size, sigma.size):
        raise ValueError("static accessible mask must have shape (N, N)")

    weighted_mask = _with_self(mask, include_self=include_self)
    information = weighted_mask @ _inverse_variance(sigma)
    return _safe_inverse_information(information)


def _local_variance_time_series(
    sigma: np.ndarray,
    mask: np.ndarray,
    *,
    include_self: bool,
) -> np.ndarray:
    T, N = sigma.shape
    if mask.ndim == 2:
        if mask.shape != (N, N):
            raise ValueError("static accessible mask must have shape (N, N)")
        weighted_mask = _with_self(mask, include_self=include_self)
        information = np.einsum("ij,tj->ti", weighted_mask, _inverse_variance(sigma))
        return _safe_inverse_information(information)

    if mask.ndim == 3:
        if mask.shape != (T, N, N):
            raise ValueError("time-varying accessible mask must have shape (T, N, N)")
        weighted_mask = _with_self(mask, include_self=include_self)
        information = np.einsum("tij,tj->ti", weighted_mask, _inverse_variance(sigma))
        return _safe_inverse_information(information)

    raise ValueError("accessible mask must have shape (N, N) or (T, N, N)")


def _inverse_variance(sigmas: np.ndarray) -> np.ndarray:
    return 1.0 / np.square(sigmas)


def _safe_inverse_information(information: np.ndarray) -> np.ndarray:
    if np.any(information <= 0.0):
        raise ValueError("each accessible set must contain positive information")
    return 1.0 / information


def _with_self(mask: np.ndarray, *, include_self: bool) -> np.ndarray:
    result = np.array(mask, dtype=bool, copy=True)
    if not include_self:
        return result

    if result.ndim == 2:
        np.fill_diagonal(result, True)
        return result

    if result.ndim == 3:
        idx = np.arange(result.shape[1])
        result[:, idx, idx] = True
        return result

    raise ValueError("accessible mask must have shape (N, N) or (T, N, N)")


def _as_positive_float_array(values: np.ndarray | float, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        raise ValueError(f"{name} cannot be empty")
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    if np.any(array <= 0.0):
        raise ValueError(f"{name} must be positive")
    return array


def _as_nonnegative_float_array(values: np.ndarray | float, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        raise ValueError(f"{name} cannot be empty")
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    if np.any(array < 0.0):
        raise ValueError(f"{name} cannot be negative")
    return array


def _as_boolean_array(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=bool)
    if array.size == 0:
        raise ValueError(f"{name} cannot be empty")
    return array


def _validate_n_nodes(N: int) -> int:
    n_nodes = int(N)
    if n_nodes <= 0:
        raise ValueError("N must be positive")
    return n_nodes


def _maybe_scalar(values: np.ndarray) -> np.ndarray | float:
    if np.ndim(values) == 0:
        return float(values)
    return values


"""Deviation decomposition for ARP reference comparisons."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .jensen_gap import JensenGapResult, jensen_gap_components


@dataclass(frozen=True)
class DeviationDecomposition:
    """Deviation terms relative to the homogeneous topology reference."""

    observed_ratio: float
    reference_ratio: float
    delta_total: float
    delta_jensen: float
    delta_residual: float
    jensen: JensenGapResult
    residual_interpretation: str


@dataclass(frozen=True)
class AdmecDelta:
    """ADMEC-vs-ideal-local MSE delta and sign interpretation."""

    delta: float
    interpretation: str


def mse_ratio(local_mse: float, central_mse: float) -> float:
    """Return local/central MSE ratio."""

    local = _as_nonnegative_scalar(local_mse, name="local_mse")
    central = _as_positive_scalar(central_mse, name="central_mse")
    return local / central


def total_deviation(
    local_mse: float,
    central_mse: float,
    N: int,
    k_bar: float,
) -> float:
    """Return ``MSE_local/MSE_cent - N/k_bar``."""

    n_nodes = _validate_n_nodes(N)
    bar = _as_positive_scalar(k_bar, name="k_bar")
    if bar > n_nodes:
        raise ValueError("k_bar cannot exceed N")
    return mse_ratio(local_mse, central_mse) - n_nodes / bar


def residual_deviation(delta_total: float, delta_jensen: float) -> float:
    """Return corrected residual term ``Delta_total - Delta_J``."""

    return _as_finite_scalar(delta_total, name="delta_total") - _as_finite_scalar(
        delta_jensen,
        name="delta_jensen",
    )


def deviation_decomposition(
    local_mse: float,
    central_mse: float,
    N: int,
    neighbor_count: np.ndarray | float,
    *,
    include_self: bool = True,
) -> DeviationDecomposition:
    """Return total, Jensen, and residual deviations for exported counts."""

    jensen = jensen_gap_components(N, neighbor_count, include_self=include_self)
    observed = mse_ratio(local_mse, central_mse)
    total = observed - jensen.ratio_at_k_bar
    residual = residual_deviation(total, jensen.gap)
    return DeviationDecomposition(
        observed_ratio=observed,
        reference_ratio=jensen.ratio_at_k_bar,
        delta_total=total,
        delta_jensen=jensen.gap,
        delta_residual=residual,
        jensen=jensen,
        residual_interpretation=residual_sign_label(residual),
    )


def residual_sign_label(delta_residual: float) -> str:
    """Return the mandatory ARP sign annotation for residual deviations."""

    delta = _as_finite_scalar(delta_residual, name="delta_residual")
    if delta < 0.0:
        return (
            "helpful violation: temporal pooling/correlations increase "
            "effective information beyond the static independent-reading assumption"
        )
    if delta > 0.0:
        return "unmodelled degradation: staleness bias or adversarial topology"
    return "on reference: no residual deviation"


def admec_vs_ideal_local(admec_mse: float, ideal_local_mse: float) -> AdmecDelta:
    """Return ``MSE_ADMEC - MSE_ideal_local`` with bias-variance interpretation."""

    delta = _as_nonnegative_scalar(admec_mse, name="admec_mse") - _as_nonnegative_scalar(
        ideal_local_mse,
        name="ideal_local_mse",
    )
    if delta > 0.0:
        label = "information loss dominates"
    elif delta < 0.0:
        label = "bias reduction dominates"
    else:
        label = "matched ADMEC and ideal-local MSE"
    return AdmecDelta(delta=delta, interpretation=label)


def _validate_n_nodes(N: int) -> int:
    n_nodes = int(N)
    if n_nodes <= 0:
        raise ValueError("N must be positive")
    return n_nodes


def _as_positive_scalar(value: float, *, name: str) -> float:
    result = _as_finite_scalar(value, name=name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _as_nonnegative_scalar(value: float, *, name: str) -> float:
    result = _as_finite_scalar(value, name=name)
    if result < 0.0:
        raise ValueError(f"{name} cannot be negative")
    return result


def _as_finite_scalar(value: float, *, name: str) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result

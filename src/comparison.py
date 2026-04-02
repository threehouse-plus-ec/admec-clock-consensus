"""
Comparison figures of merit for positioning IC.

Three established measures for context:

    1. chi2: per-point squared normalised residual
    2. Huber loss: robust alternative that down-weights large residuals
    3. Allan deviation: temporal stability measure (structurally different)

These are not competitors to IC in the project's design — IC operates on
a different axis (distributional inconsistency via interval probability).
This module exists solely for Entry 005, which positions IC against
familiar quantities. Entry 005 applies IC in cross-sectional mode
(N clocks at one time step), previewing WP2 methodology; WP1's core
calibration uses IC longitudinally (one clock, N readings over time).

Author: U. Warring
Version: 0.1.0
Status: WP1 addendum (post DG-1 closure)
"""

import numpy as np


def compute_chi2(values: np.ndarray,
                 sigmas: np.ndarray) -> np.ndarray:
    """
    Per-point squared normalised residual.

    For each point k with value x_k and declared uncertainty sigma_k,
    computes (x_k / sigma_k)^2.

    This is the per-point squared normalised residual, not the summed
    chi-squared test statistic. The summed statistic would be
    sum((x_k / sigma_k)^2), which tests the ensemble against a null
    hypothesis. Here we return the per-point contribution to allow
    pointwise comparison with IC.

    Parameters
    ----------
    values : array of shape (N,)
        Observed values (residuals from expected).
    sigmas : array of shape (N,)
        Per-point uncertainty estimates (must be > 0).

    Returns
    -------
    chi2 : array of shape (N,)
        Per-point squared normalised residual.
    """
    values = np.asarray(values, dtype=np.float64)
    sigmas = np.asarray(sigmas, dtype=np.float64)
    if values.shape != sigmas.shape or values.ndim != 1:
        raise ValueError("values and sigmas must be 1-D arrays of equal length")
    if np.any(sigmas <= 0):
        raise ValueError("All sigmas must be positive")
    u = values / sigmas
    return u ** 2


def compute_huber(values: np.ndarray,
                  sigmas: np.ndarray,
                  c: float = 1.345) -> np.ndarray:
    """
    Per-point Huber loss on normalised residuals.

    For normalised residual u_k = x_k / sigma_k, the Huber loss is:

        rho_c(u) = u^2 / 2           if |u| <= c
                   c * |u| - c^2 / 2  otherwise

    The threshold c = 1.345 gives 95% asymptotic efficiency at the
    Gaussian model while bounding the influence of large residuals.

    Parameters
    ----------
    values : array of shape (N,)
        Observed values (residuals from expected).
    sigmas : array of shape (N,)
        Per-point uncertainty estimates (must be > 0).
    c : float
        Huber threshold. Default 1.345.

    Returns
    -------
    huber : array of shape (N,)
        Per-point Huber loss.
    """
    values = np.asarray(values, dtype=np.float64)
    sigmas = np.asarray(sigmas, dtype=np.float64)
    if values.shape != sigmas.shape or values.ndim != 1:
        raise ValueError("values and sigmas must be 1-D arrays of equal length")
    if np.any(sigmas <= 0):
        raise ValueError("All sigmas must be positive")
    u = values / sigmas
    abs_u = np.abs(u)
    huber = np.where(abs_u <= c,
                     u ** 2 / 2,
                     c * abs_u - c ** 2 / 2)
    return huber


def compute_allan_deviation(values: np.ndarray,
                            taus: np.ndarray) -> np.ndarray:
    """
    Overlapping Allan deviation for a single time series.

    The Allan deviation characterises the frequency stability of a clock
    as a function of averaging time tau. It is a temporal stability
    measure — structurally different from chi2, Huber, and IC, which
    are all pointwise anomaly scores. Allan deviation describes how
    noise scales with averaging interval, not whether individual points
    are anomalous.

    Included here for completeness in the property table (Entry 005),
    but deliberately excluded from the three-panel comparison figure
    because it answers a different question.

    Parameters
    ----------
    values : array of shape (T,)
        Time series of clock readings (phase or frequency).
    taus : array of shape (M,)
        Averaging times (in sample units, must be positive integers).

    Returns
    -------
    adevs : array of shape (M,)
        Overlapping Allan deviation at each tau.
    """
    values = np.asarray(values, dtype=np.float64)
    taus = np.asarray(taus, dtype=np.intp)
    T = len(values)
    adevs = np.zeros(len(taus), dtype=np.float64)

    for i, tau in enumerate(taus):
        if tau < 1 or 2 * tau >= T:
            adevs[i] = np.nan
            continue
        # Overlapping Allan variance
        diffs = values[2 * tau:] - 2 * values[tau:-tau] + values[:T - 2 * tau]
        adevs[i] = np.sqrt(np.mean(diffs ** 2) / (2 * tau ** 2))

    return adevs

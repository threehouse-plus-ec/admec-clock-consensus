"""
Temporal-structure statistics for the three-way classifier.

The classifier separates anomalies into structured (persistent temporal
trend) and unstructured (memoryless). Two statistics over a trailing
window of length W:

    1. Variance slope: linear regression of log(running variance) over
       the trailing window. Positive slope → growing instability.
    2. Lag-1 autocorrelation: sample autocorrelation at lag 1 over the
       trailing window. Rising autocorrelation is the classic critical-
       slowing-down indicator.

The effect-size threshold δ_min is calibrated from the null distributions
of these statistics (see logbook entry 004).

Author: U. Warring
Version: 0.1.0
Status: WP1 implementation
"""

import numpy as np
from typing import Optional, Tuple


def compute_temporal_structure(values: np.ndarray,
                               window: int = 20
                               ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute trailing variance slope and lag-1 autocorrelation.

    For each time step t ≥ window, computes statistics over
    values[t-window:t].

    Parameters
    ----------
    values : array of shape (T,)
        Time series (single node).
    window : int
        Trailing window length. Default 20.

    Returns
    -------
    var_slopes : array of shape (T,)
        Trailing variance slope at each step. NaN for t < window.
        Computed as the slope of log(running variance) over sub-windows
        of size window//4 within the trailing window.
    autocorrs : array of shape (T,)
        Trailing lag-1 autocorrelation at each step. NaN for t < window.
    """
    values = np.asarray(values, dtype=np.float64)
    T = len(values)
    var_slopes = np.full(T, np.nan)
    autocorrs = np.full(T, np.nan)

    if T < window:
        return var_slopes, autocorrs

    # Sub-window size for variance slope estimation
    sub_w = max(window // 4, 3)
    n_subs = window - sub_w + 1

    for t in range(window, T):
        segment = values[t - window:t]

        # --- Variance slope ---
        # Compute running variance over sub-windows within the segment
        log_vars = np.zeros(n_subs)
        for i in range(n_subs):
            v = np.var(segment[i:i + sub_w])
            log_vars[i] = np.log(max(v, 1e-30))
        # Linear regression slope
        x = np.arange(n_subs, dtype=np.float64)
        x_mean = x.mean()
        y_mean = log_vars.mean()
        var_slopes[t] = np.sum((x - x_mean) * (log_vars - y_mean)) / \
                        max(np.sum((x - x_mean) ** 2), 1e-30)

        # --- Lag-1 autocorrelation ---
        seg_mean = segment.mean()
        seg_centered = segment - seg_mean
        c0 = np.sum(seg_centered ** 2)
        if c0 > 1e-30:
            c1 = np.sum(seg_centered[:-1] * seg_centered[1:])
            autocorrs[t] = c1 / c0
        else:
            autocorrs[t] = 0.0

    return var_slopes, autocorrs


def calibrate_delta_min(null_var_slopes: np.ndarray,
                        null_autocorrs: np.ndarray,
                        var_multiplier: float = 3.0,
                        acf_percentile: float = 95.0
                        ) -> Tuple[float, float]:
    """
    Compute δ_min thresholds from null distributions.

    Two different calibration methods, chosen for the statistical
    properties of each statistic:

    - Variance slope (unbounded): δ_min = var_multiplier × median(|slope|)
    - Autocorrelation (bounded to [-1, 1]): δ_min = percentile of |acf|

    Parameters
    ----------
    null_var_slopes : array
        Variance slope values under null.
    null_autocorrs : array
        Autocorrelation values under null.
    var_multiplier : float
        Multiplier for median absolute variance slope. Default 3.0.
    acf_percentile : float
        Percentile for |autocorrelation|. Default 95.0.

    Returns
    -------
    delta_min_var : float
        Effect-size threshold for variance slope.
    delta_min_acf : float
        Effect-size threshold for autocorrelation.
    """
    clean_var = null_var_slopes[~np.isnan(null_var_slopes)]
    clean_acf = null_autocorrs[~np.isnan(null_autocorrs)]
    delta_var = var_multiplier * np.median(np.abs(clean_var))
    delta_acf = np.percentile(np.abs(clean_acf), acf_percentile)
    return delta_var, delta_acf

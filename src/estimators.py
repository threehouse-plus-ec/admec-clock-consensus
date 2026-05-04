"""
Consensus estimators for the clock-network benchmark (WP2 batch a).

Implemented in this module (seven of nine):
    freq_global         Inverse-variance weighted mean over all nodes
    freq_local          Same, restricted per node to delay-accessible
                        neighbours (and self)
    freq_exclude        Inverse-variance weighted mean excluding nodes
                        with cross-sectional IC >= threshold
    huber               Huber M-estimator via IRLS
    admec_unconstrained Three-way classification; consensus over STABLE
                        nodes (centralised, no delay or update bounds)
    admec_delay         Per-node consensus over delay-accessible STABLE
                        neighbours
    admec_full          ADMEC-delay + sequential constraint projection
                        on the per-node update vector

BOCPD and IMM are deferred to subsequent commits.

Common interface
----------------
Every estimator takes
    Y       : array (T, N) of fractional-frequency residuals
    Sigmas  : array (T, N) of declared per-sample uncertainties
    adj     : optional bool array (N, N) of adjacency
    delays  : optional int array (N, N) of communication delays
plus method-specific keyword arguments. Each returns
    Estimates : array (T, N), the per-node consensus estimate at each
                time step. For centralised methods (freq_global,
                freq_exclude, huber, admec_unconstrained) all rows are
                constant across nodes (Estimates[t, i] == Estimates[t, j]).

ADMEC design choices
--------------------
1. Classification operates on cross-sectional per-reading IC at each
   time step (the natural network usage previewed in entry 005),
   combined with longitudinal temporal-structure stats per clock
   (var_slope and acf over a trailing window of the clock's own history).
2. The consensus is a weighted mean over STABLE nodes only. STRUCTURED
   nodes are intentionally NOT averaged in (the proposal's
   "tracked and gated rather than absorbed" rule). UNSTRUCTURED nodes
   are excluded as memoryless noise bursts.
3. ADMEC-full computes a per-node proposed update Delta_i = target_i -
   prev_estimate_i, then projects the full Delta vector through the
   constraints defined in src/constraints.py.

Fallbacks
---------
If at time t no node satisfies the inclusion criterion (e.g. all
flagged anomalous, or no delay-accessible STABLE neighbour exists),
the estimator carries forward the previous estimate. At t=0 the
fallback uses the per-node reading itself.
"""

from typing import Callable, Optional

import numpy as np

from ic import compute_ic
from temporal import compute_temporal_structure
from classify import (Mode, classify_array,
                      THRESHOLD_95, DELTA_MIN_VAR, DELTA_MIN_ACF)
from constraints import ConstraintParams, project_update


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def _weighted_mean(values: np.ndarray,
                   sigmas: np.ndarray,
                   mask: Optional[np.ndarray] = None) -> float:
    """Inverse-variance weighted mean of `values`. If `mask` is given,
    use only entries where mask is True. Returns NaN if no entries."""
    if mask is not None:
        values = values[mask]
        sigmas = sigmas[mask]
    if values.size == 0:
        return np.nan
    w = 1.0 / np.square(sigmas)
    return float(np.sum(w * values) / np.sum(w))


def _carry_forward(estimates: np.ndarray, t: int, fallback: np.ndarray):
    """Fill row t of `estimates` from t-1 (or `fallback` if t == 0)."""
    if t == 0:
        estimates[t, :] = fallback
    else:
        estimates[t, :] = estimates[t - 1, :]


# ---------------------------------------------------------------
# FREQ family
# ---------------------------------------------------------------

def freq_global(Y: np.ndarray,
                Sigmas: np.ndarray,
                adj: Optional[np.ndarray] = None,
                delays: Optional[np.ndarray] = None) -> np.ndarray:
    """Inverse-variance weighted mean over all nodes at each step."""
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    estimates = np.zeros((T, N))
    for t in range(T):
        m = _weighted_mean(Y[t, :], Sigmas[t, :])
        if not np.isnan(m):
            estimates[t, :] = m
        else:
            _carry_forward(estimates, t, Y[t, :])
    return estimates


def freq_local(Y: np.ndarray,
               Sigmas: np.ndarray,
               adj: np.ndarray,
               delays: np.ndarray,
               freshness: int = 1) -> np.ndarray:
    """Per-node weighted mean over delay-accessible neighbours and self.

    A neighbour j is accessible to i at step t iff
        adj[i, j]  AND  delays[i, j] <= freshness.
    The node itself is always included (delay 0 to itself).
    """
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    accessible = adj & (delays <= freshness)
    np.fill_diagonal(accessible, True)
    estimates = np.zeros((T, N))
    for t in range(T):
        for i in range(N):
            mask = accessible[i]
            m = _weighted_mean(Y[t, :], Sigmas[t, :], mask=mask)
            if np.isnan(m):
                estimates[t, i] = (estimates[t - 1, i] if t > 0
                                    else Y[t, i])
            else:
                estimates[t, i] = m
    return estimates


def freq_exclude(Y: np.ndarray,
                 Sigmas: np.ndarray,
                 adj: Optional[np.ndarray] = None,
                 delays: Optional[np.ndarray] = None,
                 threshold: float = THRESHOLD_95) -> np.ndarray:
    """Centralised weighted mean excluding nodes with cross-sectional
    per-reading IC >= threshold. If all nodes are flagged at step t,
    the previous consensus is carried forward."""
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    estimates = np.zeros((T, N))
    for t in range(T):
        ic_t = compute_ic(Y[t, :], Sigmas[t, :])
        keep = ic_t < threshold
        if not keep.any():
            _carry_forward(estimates, t, Y[t, :])
            continue
        m = _weighted_mean(Y[t, :], Sigmas[t, :], mask=keep)
        if np.isnan(m):
            _carry_forward(estimates, t, Y[t, :])
        else:
            estimates[t, :] = m
    return estimates


# ---------------------------------------------------------------
# Huber M-estimator (IRLS)
# ---------------------------------------------------------------

def huber(Y: np.ndarray,
          Sigmas: np.ndarray,
          adj: Optional[np.ndarray] = None,
          delays: Optional[np.ndarray] = None,
          c: float = 1.345,
          max_iter: int = 30,
          tol: float = 1e-8) -> np.ndarray:
    """Centralised Huber M-estimator via iteratively reweighted least
    squares. Tuning constant c defaults to the conventional 1.345
    (95% efficiency under Gaussian); the proposal evaluates
    c in {1.0, 1.345, 2.0} on null scenarios and fixes the best.

    Per iteration:
        r_i        = (y_i - m) / sigma_i
        w_i^Huber  = 1 if |r_i| <= c else c / |r_i|
        w_i        = w_i^Huber / sigma_i^2
        m_new      = sum(w_i * y_i) / sum(w_i)
    """
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    estimates = np.zeros((T, N))
    for t in range(T):
        y = Y[t, :]
        s = Sigmas[t, :]
        m = _weighted_mean(y, s)
        if np.isnan(m):
            _carry_forward(estimates, t, y)
            continue
        for _ in range(max_iter):
            r_norm = np.abs(y - m) / s
            w_huber = np.where(r_norm <= c, 1.0,
                                c / np.maximum(r_norm, 1e-30))
            w = w_huber / np.square(s)
            m_new = float(np.sum(w * y) / np.sum(w))
            if abs(m_new - m) < tol:
                m = m_new
                break
            m = m_new
        estimates[t, :] = m
    return estimates


# ---------------------------------------------------------------
# ADMEC family
# ---------------------------------------------------------------

def _classify_network_full(Y: np.ndarray,
                           Sigmas: np.ndarray,
                           window: int,
                           threshold: float,
                           delta_min_var: float,
                           delta_min_acf: float
                           ) -> np.ndarray:
    """Compute the (T, N) Mode array from raw readings.

    Cross-sectional IC at each timestep, longitudinal temporal stats
    per clock. Returns the same int-encoded mode array that
    classify_array produces.
    """
    T, N = Y.shape
    IC = np.zeros((T, N))
    for t in range(T):
        IC[t, :] = compute_ic(Y[t, :], Sigmas[t, :])
    var_slopes = np.full((T, N), np.nan)
    acfs = np.full((T, N), np.nan)
    for i in range(N):
        var_slopes[:, i], acfs[:, i] = compute_temporal_structure(
            Y[:, i], window=window)
    return classify_array(IC, var_slopes, acfs,
                          threshold=threshold,
                          delta_min_var=delta_min_var,
                          delta_min_acf=delta_min_acf)


def admec_unconstrained(Y: np.ndarray,
                        Sigmas: np.ndarray,
                        adj: Optional[np.ndarray] = None,
                        delays: Optional[np.ndarray] = None,
                        threshold: float = THRESHOLD_95,
                        delta_min_var: float = DELTA_MIN_VAR,
                        delta_min_acf: float = DELTA_MIN_ACF,
                        window: int = 20) -> np.ndarray:
    """Centralised ADMEC: weighted mean over STABLE nodes; STRUCTURED
    and UNSTRUCTURED nodes are excluded from the consensus output
    (STRUCTURED is "tracked and gated" per the proposal -- not absorbed
    into the consensus)."""
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    modes = _classify_network_full(Y, Sigmas, window, threshold,
                                    delta_min_var, delta_min_acf)
    estimates = np.zeros((T, N))
    for t in range(T):
        keep = modes[t, :] == int(Mode.STABLE)
        if not keep.any():
            _carry_forward(estimates, t, Y[t, :])
            continue
        m = _weighted_mean(Y[t, :], Sigmas[t, :], mask=keep)
        if np.isnan(m):
            _carry_forward(estimates, t, Y[t, :])
        else:
            estimates[t, :] = m
    return estimates


def admec_delay(Y: np.ndarray,
                Sigmas: np.ndarray,
                adj: np.ndarray,
                delays: np.ndarray,
                freshness: int = 1,
                threshold: float = THRESHOLD_95,
                delta_min_var: float = DELTA_MIN_VAR,
                delta_min_acf: float = DELTA_MIN_ACF,
                window: int = 20) -> np.ndarray:
    """Per-node ADMEC: weighted mean over delay-accessible STABLE
    neighbours (including self if STABLE)."""
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    accessible = adj & (delays <= freshness)
    np.fill_diagonal(accessible, True)
    modes = _classify_network_full(Y, Sigmas, window, threshold,
                                    delta_min_var, delta_min_acf)
    estimates = np.zeros((T, N))
    stable = (modes == int(Mode.STABLE))
    for t in range(T):
        for i in range(N):
            mask = accessible[i] & stable[t, :]
            m = _weighted_mean(Y[t, :], Sigmas[t, :], mask=mask)
            if np.isnan(m):
                estimates[t, i] = (estimates[t - 1, i] if t > 0
                                    else Y[t, i])
            else:
                estimates[t, i] = m
    return estimates


def admec_full(Y: np.ndarray,
               Sigmas: np.ndarray,
               adj: np.ndarray,
               delays: np.ndarray,
               freshness: int = 1,
               threshold: float = THRESHOLD_95,
               delta_min_var: float = DELTA_MIN_VAR,
               delta_min_acf: float = DELTA_MIN_ACF,
               window: int = 20,
               constraint_params: Optional[ConstraintParams] = None
               ) -> np.ndarray:
    """ADMEC-delay + sequential constraint projection on the per-node
    update vector.

    At each step the proposed update Delta_i = target_i - prev_i is
    formed from delay-accessible STABLE neighbours; the full Delta
    vector is then projected through src/constraints.py:project_update,
    using Sigmas[t, :] as per-node sigmas. Rejection (variance ratio
    out of [0.5, 1.5]) carries the previous estimate forward.
    """
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape
    if constraint_params is None:
        constraint_params = ConstraintParams()

    accessible = adj & (delays <= freshness)
    np.fill_diagonal(accessible, True)
    modes = _classify_network_full(Y, Sigmas, window, threshold,
                                    delta_min_var, delta_min_acf)
    stable = (modes == int(Mode.STABLE))

    estimates = np.zeros((T, N))
    estimates[0, :] = Y[0, :]
    for t in range(1, T):
        proposed = np.zeros(N)
        for i in range(N):
            mask = accessible[i] & stable[t, :]
            target = _weighted_mean(Y[t, :], Sigmas[t, :], mask=mask)
            if np.isnan(target):
                # No STABLE neighbour -> propose no update
                proposed[i] = 0.0
            else:
                proposed[i] = target - estimates[t - 1, i]
        # Project the network-wide proposed update
        projected, _ = project_update(estimates[t - 1, :], proposed,
                                       Sigmas[t, :],
                                       params=constraint_params)
        estimates[t, :] = estimates[t - 1, :] + projected
    return estimates


# ---------------------------------------------------------------
# Registry
# ---------------------------------------------------------------

ESTIMATORS = {
    'freq_global': freq_global,
    'freq_local': freq_local,
    'freq_exclude': freq_exclude,
    'huber': huber,
    'admec_unconstrained': admec_unconstrained,
    'admec_delay': admec_delay,
    'admec_full': admec_full,
}
"""Registry of estimators implemented so far. BOCPD and IMM will
be added in subsequent commits."""

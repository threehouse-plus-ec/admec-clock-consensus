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

    NOTE: an inaccessible neighbour (delay > freshness) is dropped
    from the consensus at step t. This estimator does NOT use stale
    readings Y[t - delays[i, j], j] from past steps. Storing and
    correlating delayed readings would be a different estimator (a
    delayed Kalman variant), to be considered as a WP3 ablation if
    reviewers raise it. See user-feedback comment after batch (a)
    review.
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
    neighbours (including self if STABLE).

    NOTE: same delay convention as freq_local -- a neighbour with
    delays[i, j] > freshness is dropped, not pulled from history.
    Stale-reading variants are deferred to WP3 ablations.
    """
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

    NOTE: same delay convention as freq_local and admec_delay --
    a neighbour with delays[i, j] > freshness is dropped, not
    pulled from history. Stale-reading variants are deferred to WP3.
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
# BOCPD (Adams & MacKay 2007)
# ---------------------------------------------------------------

def _logsumexp(x: np.ndarray) -> float:
    """Stable log-sum-exp for a 1-D array."""
    m = float(np.max(x))
    if not np.isfinite(m):
        return m
    return m + float(np.log(np.sum(np.exp(x - m))))


def bocpd_run_length_posterior(values: np.ndarray,
                               sigmas: np.ndarray,
                               hazard_lambda: float,
                               r_max: int = 200,
                               prior_mean: float = 0.0,
                               prior_var: float = 1.0e6
                               ) -> np.ndarray:
    """Per-node Bayesian online changepoint detection (Adams & MacKay 2007).

    Gaussian observations with known per-sample sigma; the unknown
    segment mean has prior N(prior_mean, prior_var). The hazard is
    constant: h(r) = 1 / hazard_lambda.

    Implementation follows Adams & MacKay (2007) eq. 1-7 in log-space
    with truncation at r_max (the standard message-passing
    truncation): once a hypothetical run length exceeds r_max it is
    dropped. This keeps the per-step cost O(r_max) instead of O(t).

    Run-length convention: r_t is the number of observations PRECEDING
    x_t in the current segment (Adams & MacKay's convention). r_t = 0
    means a changepoint occurred at time t.

    Parameters
    ----------
    values : array of shape (T,)
    sigmas : array of shape (T,)
    hazard_lambda : float
        Hazard parameter; expected segment length under the geometric
        run-length distribution. Tested at {50, 100, 200} per proposal.
    r_max : int
        Truncation point for the run-length posterior. r_max = 200
        is safe for T up to a few thousand at lambda <= 200.
    prior_mean, prior_var : float
        Gaussian prior on the segment mean. Defaults are weakly
        informative.

    Returns
    -------
    posterior : array of shape (T, r_max + 1)
        posterior[t, r] = P(r_t = r | x_{1:t}). Rows sum to 1.
    """
    values = np.asarray(values, dtype=np.float64)
    sigmas = np.asarray(sigmas, dtype=np.float64)
    T = values.size
    if T == 0:
        return np.zeros((0, r_max + 1))
    if hazard_lambda <= 1.0:
        raise ValueError(
            f"hazard_lambda must be > 1, got {hazard_lambda}")
    if np.any(sigmas <= 0):
        raise ValueError("sigmas must be positive")

    log_h = -np.log(hazard_lambda)
    log_1mh = np.log1p(-1.0 / hazard_lambda)

    prior_prec = 1.0 / prior_var

    # Sufficient statistics indexed by r_{t-1} (= number of
    # observations in the run BEFORE the current step's observation).
    post_prec = np.full(r_max + 1, prior_prec)
    post_mean = np.full(r_max + 1, prior_mean)

    # Joint log P(r_{t-1} = r, x_{1:t-1}). Initialise at t = 0 with
    # P(r_{-1} = 0) = 1 by convention.
    log_joint = np.full(r_max + 1, -np.inf)
    log_joint[0] = 0.0

    posterior = np.zeros((T, r_max + 1))

    for t in range(T):
        x = values[t]
        s2 = sigmas[t] ** 2

        # Predictive log-likelihood for each r_{t-1}
        pred_var = 1.0 / post_prec + s2
        log_pi = (-0.5 * np.log(2.0 * np.pi * pred_var)
                  - 0.5 * (x - post_mean) ** 2 / pred_var)

        # Update joint
        log_growth = log_joint + log_pi + log_1mh   # for r_t = r + 1
        log_change = _logsumexp(log_joint + log_pi + log_h)  # r_t = 0

        new_log_joint = np.full(r_max + 1, -np.inf)
        new_log_joint[0] = log_change
        new_log_joint[1:r_max + 1] = log_growth[:r_max]

        # Normalise to posterior at step t
        log_evidence = _logsumexp(new_log_joint)
        log_post = new_log_joint - log_evidence
        posterior[t, :] = np.exp(log_post)

        # Sufficient statistics for the next step
        new_post_prec = np.full(r_max + 1, prior_prec)
        new_post_mean = np.full(r_max + 1, prior_mean)
        new_post_prec[1:r_max + 1] = post_prec[:r_max] + 1.0 / s2
        new_post_mean[1:r_max + 1] = (
            (post_prec[:r_max] * post_mean[:r_max] + x / s2)
            / new_post_prec[1:r_max + 1])
        post_prec = new_post_prec
        post_mean = new_post_mean

        log_joint = log_post

    return posterior


def bocpd_excluded(values: np.ndarray,
                   sigmas: np.ndarray,
                   hazard_lambda: float,
                   r_max: int = 200,
                   min_run_keep: int = 10,
                   prior_mean: float = 0.0,
                   prior_var: float = 1.0e6) -> np.ndarray:
    """Per-step exclusion mask for one node based on BOCPD.

    Excludes the node at step t if the MAP run-length is less than
    min_run_keep (recently changed; the proposal's "post-changepoint
    nodes excluded" rule). Returns a (T,) bool array.
    """
    posterior = bocpd_run_length_posterior(
        values, sigmas, hazard_lambda,
        r_max=r_max, prior_mean=prior_mean, prior_var=prior_var)
    r_map = np.argmax(posterior, axis=1)
    return r_map < min_run_keep


def bocpd(Y: np.ndarray,
          Sigmas: np.ndarray,
          adj: Optional[np.ndarray] = None,
          delays: Optional[np.ndarray] = None,
          hazard_lambda: float = 100.0,
          r_max: int = 200,
          min_run_keep: int = 10,
          prior_mean: float = 0.0,
          prior_var: float = 1.0e6) -> np.ndarray:
    """Centralised consensus via BOCPD-based per-node exclusion.

    Each node runs Adams & MacKay 2007 BOCPD over its own reading
    sequence. At each step, nodes whose MAP run-length is below
    min_run_keep are excluded; the consensus is an inverse-variance
    weighted mean over the rest.

    The proposal evaluates hazard_lambda in {50, 100, 200} on null
    scenarios (S4/S5) and fixes the best for signal scenarios.
    """
    Y = np.asarray(Y, dtype=np.float64)
    Sigmas = np.asarray(Sigmas, dtype=np.float64)
    T, N = Y.shape

    excluded = np.zeros((T, N), dtype=bool)
    for j in range(N):
        excluded[:, j] = bocpd_excluded(
            Y[:, j], Sigmas[:, j], hazard_lambda,
            r_max=r_max, min_run_keep=min_run_keep,
            prior_mean=prior_mean, prior_var=prior_var)

    estimates = np.zeros((T, N))
    for t in range(T):
        keep = ~excluded[t, :]
        if keep.any():
            m = _weighted_mean(Y[t, :], Sigmas[t, :], mask=keep)
        else:
            m = np.nan
        if np.isnan(m):
            # Fallback: centralised all-nodes mean at t=0 (BOCPD's
            # MAP run-length always starts at 1, so the first step
            # is excluded by construction). Carry forward later.
            if t == 0:
                m_all = _weighted_mean(Y[t, :], Sigmas[t, :])
                estimates[t, :] = m_all if not np.isnan(m_all) else 0.0
            else:
                estimates[t, :] = estimates[t - 1, :]
        else:
            estimates[t, :] = m
    return estimates


# ---------------------------------------------------------------
# Registry
# ---------------------------------------------------------------

ESTIMATORS = {
    'freq_global': freq_global,
    'freq_local': freq_local,
    'freq_exclude': freq_exclude,
    'huber': huber,
    'bocpd': bocpd,
    'admec_unconstrained': admec_unconstrained,
    'admec_delay': admec_delay,
    'admec_full': admec_full,
}
"""Registry of estimators. IMM will be added in the next commit."""

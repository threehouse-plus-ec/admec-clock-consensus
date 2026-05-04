"""
Update-size constraint projection for ADMEC-full.

A proposed network update Delta is projected onto the feasible set
defined by three constraints (per project proposal sec. WP2):

    1. Step bound        |Delta_i| <= max_step_factor * sigma_i
                         per node (default 3 * sigma per node).
    2. Energy bound      sum(Delta_i^2) <= N * energy_factor *
                         mean(sigma^2), the expected total squared
                         fluctuation under the null.
    3. Variance ratio    var(state + Delta) / var(state) in
                         [var_ratio_min, var_ratio_max] (default
                         [0.5, 1.5]). A single update step should
                         neither halve nor double the ensemble
                         variance.

Projection is implemented as sequential projection: clip to the
per-node box, then uniformly scale onto the energy ball if needed.
The variance-ratio constraint is checked post-projection and, if
violated, the update is REJECTED (replaced by zero), because the
proposal specifies "if the feasible set is empty, the update is
rejected entirely and the previous state is retained" (sec. WP2).

Sequential projection is not in general the true Euclidean
projection onto the intersection of the box and the ball, but is
the standard approximation when an exact projector is not needed
and the constraints are loose enough that the active set is small.
The variance-ratio constraint is a quadratic-in-Delta inequality
on top of state; rejecting on violation matches the proposal's
fallback rule and avoids introducing a custom QP solver.

Constraint thresholds are fixed a priori from the running noise
scale (sigma); WP3 ablation tests sensitivity under +/- 30%
variation of the box and energy factors.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass
class ConstraintParams:
    """Thresholds for the three update-size constraints.

    Defaults mirror the proposal's spec verbatim (3-sigma per-node,
    N*sigma^2 energy, [0.5, 1.5] variance ratio).
    """
    max_step_factor: float = 3.0
    energy_factor: float = 1.0
    var_ratio_min: float = 0.5
    var_ratio_max: float = 1.5


def project_update(state: np.ndarray,
                   proposed_update: np.ndarray,
                   sigmas: np.ndarray,
                   params: Optional[ConstraintParams] = None
                   ) -> Tuple[np.ndarray, dict]:
    """Project a proposed update onto the feasible set.

    Parameters
    ----------
    state : array of shape (N,)
        Current network state (consensus estimates per node).
    proposed_update : array of shape (N,)
        Update vector that ADMEC would like to apply.
    sigmas : array of shape (N,) or scalar
        Per-node declared uncertainty. A scalar is broadcast across
        all nodes.
    params : ConstraintParams or None
        Constraint thresholds; defaults are the spec values.

    Returns
    -------
    filtered_update : array of shape (N,)
        Update after projection. May be all-zeros if the variance-
        ratio constraint cannot be satisfied (rejection fallback).
    status : dict
        Keys: 'box_clipped' (bool), 'energy_scaled' (bool),
        'rejected' (bool), 'reason' (str), 'energy_ratio' (float),
        'var_ratio' (float). 'energy_ratio' is sum(upd^2) /
        energy_max BEFORE scaling; 'var_ratio' is var(state +
        filtered_update) / var(state).
    """
    if params is None:
        params = ConstraintParams()

    state = np.asarray(state, dtype=np.float64)
    upd = np.asarray(proposed_update, dtype=np.float64).copy()
    sigmas = np.asarray(sigmas, dtype=np.float64)
    if sigmas.ndim == 0:
        sigmas = np.full(state.shape, float(sigmas))

    if state.shape != upd.shape or state.shape != sigmas.shape:
        raise ValueError(
            f"state {state.shape}, proposed_update {upd.shape}, "
            f"sigmas {sigmas.shape} must all match")
    if state.ndim != 1:
        raise ValueError(f"expected 1-D arrays, got ndim={state.ndim}")
    if np.any(sigmas <= 0):
        raise ValueError("sigmas must be positive")

    n = state.size
    status = {
        'box_clipped': False,
        'energy_scaled': False,
        'rejected': False,
        'reason': '',
        'energy_ratio': 0.0,
        'var_ratio': 1.0,
    }

    # 1. Step (box) constraint
    bound = params.max_step_factor * sigmas
    clipped = np.clip(upd, -bound, bound)
    if not np.allclose(clipped, upd):
        status['box_clipped'] = True
    upd = clipped

    # 2. Energy (ball) constraint
    sigma_bar_sq = float(np.mean(sigmas ** 2))
    energy_max = n * params.energy_factor * sigma_bar_sq
    energy = float(np.sum(upd ** 2))
    if energy_max > 0:
        status['energy_ratio'] = energy / energy_max
    if energy > energy_max and energy_max > 0:
        upd = upd * np.sqrt(energy_max / energy)
        status['energy_scaled'] = True

    # 3. Variance-ratio constraint
    var_before = float(np.var(state))
    var_after = float(np.var(state + upd))
    # Guard against floating-point noise: np.var on a constant array
    # returns ~1e-33 instead of 0.0.  Using the raw value causes
    # var_after/var_before to blow up to ~1e30, rejecting every
    # update on dense networks where the consensus state is nearly
    # uniform.  See logbook entry 007.
    if var_before > 1e-20:
        ratio = var_after / var_before
        status['var_ratio'] = ratio
        if not (params.var_ratio_min <= ratio <= params.var_ratio_max):
            status['rejected'] = True
            status['reason'] = (
                f"variance ratio {ratio:.3f} outside "
                f"[{params.var_ratio_min}, {params.var_ratio_max}]")
            upd = np.zeros_like(upd)
            status['var_ratio'] = 1.0
    # If state is constant (var_before <= 1e-20), any non-zero upd
    # would produce var_after > 0, an undefined ratio.  We pass
    # through silently; this is the expected case at consensus time.

    return upd, status


def is_feasible(state: np.ndarray,
                update: np.ndarray,
                sigmas: np.ndarray,
                params: Optional[ConstraintParams] = None) -> bool:
    """Check whether an update lies in the feasible set without projecting.

    Useful for diagnostics: the WP3 ablation can count how often
    proposed updates were already feasible vs needed projection.
    """
    if params is None:
        params = ConstraintParams()
    state = np.asarray(state, dtype=np.float64)
    upd = np.asarray(update, dtype=np.float64)
    sigmas = np.asarray(sigmas, dtype=np.float64)
    if sigmas.ndim == 0:
        sigmas = np.full(state.shape, float(sigmas))

    bound = params.max_step_factor * sigmas
    if np.any(np.abs(upd) > bound):
        return False

    sigma_bar_sq = float(np.mean(sigmas ** 2))
    energy_max = state.size * params.energy_factor * sigma_bar_sq
    if np.sum(upd ** 2) > energy_max:
        return False

    var_before = float(np.var(state))
    # Same FP guard as project_update -- np.var of a constant array can
    # return ~3e-33, not exactly 0. Treat anything below 1e-20 as zero
    # so is_feasible agrees with project_update on near-uniform states.
    if var_before > 1e-20:
        ratio = float(np.var(state + upd)) / var_before
        if not (params.var_ratio_min <= ratio <= params.var_ratio_max):
            return False
    return True

"""
Three-way node classification for WP2.

Classification rule (per project proposal sec. WP2; calibrated in WP1):

    STABLE                 I_k <  threshold
    STRUCTURED ANOMALY     I_k >= threshold AND
                           (|var_slope| > delta_min_var OR
                            |lag-1 acf|  > delta_min_acf)
    UNSTRUCTURED ANOMALY   I_k >= threshold AND
                           |var_slope| <= delta_min_var AND
                           |lag-1 acf|  <= delta_min_acf

The temporal-structure criteria are heuristic classifiers (per proposal
2.1.3 / 2.1.5), not formal structural inference. They are sensitive to
noise colour and window length; the project tests whether the heuristic
suffices for measurable estimator improvement, not whether it is optimal.

Calibrated default thresholds:
    THRESHOLD_95   = 2.976  bit  (per-reading I_k P95, worst-case -20% sigma;
                                  heteroscedastic Gaussian binding;
                                  see logbook entry 006)
    DELTA_MIN_VAR  = 0.2105      (3 x median |var slope| under Student-t(3);
                                  see logbook entry 004)
    DELTA_MIN_ACF  = 0.8703      (95th percentile of |acf| under random walk;
                                  see logbook entry 004)

The earlier AIPP-derived threshold of 1.835 bit (entries 001/002) does
NOT apply per-reading: it would inflate the false-positive rate by ~1.6x.
Robustness of delta_min tested under W in {10, 15, 20, 30}.

UNDEFINED is returned for time steps where the temporal statistics are
not yet defined (t < trailing window) or where IC is NaN.

Note on what "structured" detects: the delta_min thresholds were
calibrated for early-warning indicators of critical slowing down
(rising variance, rising autocorrelation; entry 004). They are
sensitive to growing-variance and near-fold-bifurcation dynamics
(scenario S8) but largely INSENSITIVE to a smooth linear drift
(scenario S6) -- a linear trend at rate r << sigma/W contributes
negligibly to within-window variance slope and autocorrelation, so
linear-drift anomalies typically classify as UNSTRUCTURED. This
matches the proposal's own scenario taxonomy (S6 is labelled
"anomaly detection, NOT near-critical").

Note on what crosses the per-reading IC threshold: the calibrated
THRESHOLD_95 = 2.976 bit (Entry 006) is strict. Crossing it
typically requires ISOLATED extreme readings -- coherent processes
(AR(1) with high rho, smooth drifts, slowly evolving signals)
broaden the mixture density along with the readings, leaving each
individual reading still relatively likely. The combination
"flagged-by-IC AND high-temporal-structure" is therefore selective:
the WP2 simulation campaign will reveal which scenarios populate
each of the STRUCTURED and UNSTRUCTURED bins in practice.
"""

from enum import IntEnum
from typing import Optional, Tuple

import numpy as np

from temporal import compute_temporal_structure


# ---------------------------------------------------------------
# Default calibrated thresholds (do not edit without a logbook entry)
# ---------------------------------------------------------------

THRESHOLD_95 = 2.976
"""Operational per-reading I_k threshold (Entry 006, worst-case sigma)."""

DELTA_MIN_VAR = 0.2105
"""Effect-size threshold for trailing variance slope (Entry 004)."""

DELTA_MIN_ACF = 0.8703
"""Effect-size threshold for trailing lag-1 autocorrelation (Entry 004)."""


class Mode(IntEnum):
    """Three-way classification result.

    Integer values are chosen so np.where / boolean masks compose
    cleanly with mode arrays. UNDEFINED = -1 sorts before the three
    valid modes and survives bincount/histogram counts as a clearly
    distinct value.
    """
    UNDEFINED = -1
    STABLE = 0
    STRUCTURED = 1
    UNSTRUCTURED = 2


# ---------------------------------------------------------------
# Scalar classifier
# ---------------------------------------------------------------

def classify_node(ic_value: float,
                  var_slope: float,
                  acf: float,
                  threshold: float = THRESHOLD_95,
                  delta_min_var: float = DELTA_MIN_VAR,
                  delta_min_acf: float = DELTA_MIN_ACF) -> Mode:
    """Apply the three-way rule to one (ic, var_slope, acf) tuple.

    Returns UNDEFINED if any of ic_value, var_slope, or acf is NaN.
    """
    if np.isnan(ic_value):
        return Mode.UNDEFINED
    if ic_value < threshold:
        return Mode.STABLE
    # IC flagged as anomalous: need temporal stats to subdivide
    if np.isnan(var_slope) or np.isnan(acf):
        return Mode.UNDEFINED
    has_structure = (abs(var_slope) > delta_min_var
                     or abs(acf) > delta_min_acf)
    return Mode.STRUCTURED if has_structure else Mode.UNSTRUCTURED


# ---------------------------------------------------------------
# Vectorised classifier
# ---------------------------------------------------------------

def classify_array(ic: np.ndarray,
                   var_slopes: np.ndarray,
                   acfs: np.ndarray,
                   threshold: float = THRESHOLD_95,
                   delta_min_var: float = DELTA_MIN_VAR,
                   delta_min_acf: float = DELTA_MIN_ACF,
                   two_way: bool = False) -> np.ndarray:
    """Vectorised classification.

    Accepts arrays of any matching shape (1-D for a single clock series,
    or 2-D for a network: typically (T, N)). Returns an int array of
    Mode values with the same shape.

    If `two_way` is True (WP3 ablation 4 -- DG-3 sub-criterion), the
    temporal-statistic split is skipped: every reading with
    `ic >= threshold` is labelled UNSTRUCTURED (acting as a generic
    "ANOMALOUS" class). The var_slopes / acfs arrays are still
    consumed for NaN handling consistency. The default `two_way=False`
    preserves the WP2 three-way rule.

    The collapse direction (STRUCTURED -> UNSTRUCTURED rather than a
    new ANOMALOUS code) is chosen so that `Mode.UNSTRUCTURED` continues
    to mean "exclude from consensus" in both modes; the downstream
    estimators do not need a code change.
    """
    ic = np.asarray(ic, dtype=np.float64)
    var_slopes = np.asarray(var_slopes, dtype=np.float64)
    acfs = np.asarray(acfs, dtype=np.float64)
    if ic.shape != var_slopes.shape or ic.shape != acfs.shape:
        raise ValueError(
            f"shape mismatch: ic {ic.shape}, var_slopes "
            f"{var_slopes.shape}, acfs {acfs.shape}")

    out = np.full(ic.shape, int(Mode.UNDEFINED), dtype=np.int8)

    flagged = ic >= threshold
    stable = (~flagged) & ~np.isnan(ic)
    out[stable] = int(Mode.STABLE)

    if two_way:
        # Anything flagged with finite IC -> UNSTRUCTURED (= anomalous);
        # NaN IC stays UNDEFINED. Temporal stats are not consulted.
        anomalous = flagged & ~np.isnan(ic)
        out[anomalous] = int(Mode.UNSTRUCTURED)
        return out

    # Three-way: subdivide flagged readings using temporal stats
    temporal_ok = flagged & ~np.isnan(var_slopes) & ~np.isnan(acfs)
    has_structure = (np.abs(var_slopes) > delta_min_var) | \
                    (np.abs(acfs) > delta_min_acf)
    out[temporal_ok & has_structure] = int(Mode.STRUCTURED)
    out[temporal_ok & ~has_structure] = int(Mode.UNSTRUCTURED)
    # flagged & ~temporal_ok stays UNDEFINED (already initialised)
    return out


# ---------------------------------------------------------------
# End-to-end: from raw values to classification
# ---------------------------------------------------------------

def classify_series(ic: np.ndarray,
                    values: np.ndarray,
                    window: int = 20,
                    threshold: float = THRESHOLD_95,
                    delta_min_var: float = DELTA_MIN_VAR,
                    delta_min_acf: float = DELTA_MIN_ACF
                    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Classify a single clock's reading sequence.

    Computes temporal statistics from `values` over a trailing window,
    then applies the three-way rule. The first `window` time steps will
    be classified as UNDEFINED (where IC was flagged) or STABLE (where
    IC stayed below threshold even without temporal stats).

    Returns
    -------
    modes : int array of shape (T,)
        Mode value at each time step.
    var_slopes : array of shape (T,)
        Trailing variance slope (NaN for t < window).
    acfs : array of shape (T,)
        Trailing lag-1 autocorrelation (NaN for t < window).
    """
    var_slopes, acfs = compute_temporal_structure(values, window=window)
    modes = classify_array(ic, var_slopes, acfs,
                           threshold=threshold,
                           delta_min_var=delta_min_var,
                           delta_min_acf=delta_min_acf)
    return modes, var_slopes, acfs


def classify_network(IC: np.ndarray,
                     Y: np.ndarray,
                     window: int = 20,
                     threshold: float = THRESHOLD_95,
                     delta_min_var: float = DELTA_MIN_VAR,
                     delta_min_acf: float = DELTA_MIN_ACF
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Classify all nodes in a (T, N) network reading matrix.

    Same return convention as classify_series, but each output has
    shape (T, N).
    """
    IC = np.asarray(IC, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    if IC.shape != Y.shape:
        raise ValueError(
            f"IC and Y must share shape: {IC.shape} vs {Y.shape}")
    if IC.ndim != 2:
        raise ValueError(f"Expected 2-D arrays (T, N); got ndim={IC.ndim}")

    T, N = IC.shape
    var_slopes = np.full((T, N), np.nan)
    acfs = np.full((T, N), np.nan)
    for j in range(N):
        vs, ac = compute_temporal_structure(Y[:, j], window=window)
        var_slopes[:, j] = vs
        acfs[:, j] = ac
    modes = classify_array(IC, var_slopes, acfs,
                           threshold=threshold,
                           delta_min_var=delta_min_var,
                           delta_min_acf=delta_min_acf)
    return modes, var_slopes, acfs


# ---------------------------------------------------------------
# Summary helper
# ---------------------------------------------------------------

def mode_counts(modes: np.ndarray) -> dict:
    """Return a dict {Mode -> count} from an array of mode values."""
    flat = np.asarray(modes).ravel()
    return {m: int(np.sum(flat == int(m))) for m in Mode}

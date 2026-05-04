"""
IC-independent performance metrics for the WP2 simulation campaign.

Three primary metrics (per project proposal sec. WP2):

    1. MSE              — mean squared error of consensus estimates
                          against the true reference (0 for frequency
                          residuals)
    2. Collapse index   — time-averaged standard deviation of estimates
                          across nodes, normalised by the mean declared
                          sigma. Measures variance preservation.
    3. Structure corr.  — Pearson r between (reading − estimate) and
                          the injected true signal, averaged over signal
                          clocks after onset. High = estimator preserved
                          the signal in the residual rather than
                          absorbing it into the consensus.

Plus DG-2b diagnostics:

    4. Classification   — TPR / FPR / precision / F1 for estimators that
       metrics          produce an exclusion or classification mask,
       (TPR/FPR)        evaluated against designer-injected structure.
"""

import numpy as np
from scipy import stats


def mse(estimates: np.ndarray, reference: float = 0.0) -> float:
    """Mean squared error against a scalar reference.

    Parameters
    ----------
    estimates : array of shape (T, N) or any shape
        Consensus estimator output.
    reference : float
        True reference value. Default 0 because the simulation uses
        fractional-frequency residuals centred on the nominal frequency.

    Returns
    -------
    mse : float
    """
    return float(np.mean((estimates - reference) ** 2))


def collapse_index(estimates: np.ndarray, sigmas: np.ndarray) -> float:
    """Variance-preservation metric ("collapse index").

    Defined as the time average of
        std_i(estimates[t, i]) / mean_i(sigmas[t, i])

    For a fully centralised estimator all rows are identical, giving
    std = 0 and therefore CI = 0 (complete collapse).  Local
    estimators that preserve per-node diversity score > 0.

    Parameters
    ----------
    estimates : array of shape (T, N)
    sigmas : array of shape (T, N)
        Declared per-sample uncertainties.

    Returns
    -------
    ci : float
    """
    std_t = np.std(estimates, axis=1)
    mean_sigma_t = np.mean(sigmas, axis=1)
    ratios = np.divide(
        std_t, mean_sigma_t,
        out=np.zeros_like(std_t, dtype=np.float64),
        where=mean_sigma_t > 0,
    )
    return float(np.mean(ratios))


def structure_correlation(
    Y: np.ndarray,
    estimates: np.ndarray,
    signals: np.ndarray,
    signal_clocks: np.ndarray,
    onset_idx: int = 0,
) -> float:
    """Pearson r between residual and injected signal.

    For each signal clock, correlates (Y[:, i] − estimates[:, i]) with
    signals[:, i] over the post-onset period.  A high correlation means
    the estimator left the signal in the residual (preserved it as a
    separate channel); a low correlation means the estimator absorbed
    or suppressed the signal into the consensus value.

    Parameters
    ----------
    Y : array of shape (T, N)
        Raw readings.
    estimates : array of shape (T, N)
        Consensus estimates.
    signals : array of shape (T, N)
        Ground-truth injected signal component.
    signal_clocks : array of int
        Indices of clocks that carry an injected signal.
    onset_idx : int
        First time index after signal onset (inclusive).

    Returns
    -------
    r : float
        Mean Pearson r across signal clocks.  NaN if no signal clocks
        or if all correlations are undefined.
    """
    signal_clocks = np.asarray(signal_clocks)
    if signal_clocks.size == 0:
        return np.nan

    residuals = Y - estimates
    valid = slice(onset_idx, None)

    corrs = []
    for i in signal_clocks:
        y1 = residuals[valid, i]
        y2 = signals[valid, i]
        std1 = np.std(y1)
        std2 = np.std(y2)
        if std1 > 0 and std2 > 0:
            r, _ = stats.pearsonr(y1, y2)
            if np.isfinite(r):
                corrs.append(r)
        elif std2 == 0 and np.mean(np.abs(y2)) > 0:
            # Constant signal (e.g. step change): Pearson r is undefined.
            # Use the ratio of mean absolute residual to mean absolute
            # signal as a proxy.  1.0 = signal fully preserved in residual;
            # 0.0 = signal fully absorbed into consensus.
            ratio = float(np.mean(np.abs(y1)) / np.mean(np.abs(y2)))
            corrs.append(ratio)

    return float(np.mean(corrs)) if corrs else np.nan


def classification_metrics(
    excluded: np.ndarray, true_anomalous: np.ndarray
) -> dict:
    """Binary classification accuracy for an exclusion mask.

    Parameters
    ----------
    excluded : array of shape (T, N) or (T,) bool
        Estimator's exclusion / anomaly flag.
    true_anomalous : array of shape (T, N) or (T,) bool
        Designer-injected ground-truth anomaly mask.

    Returns
    -------
    dict with keys 'tpr', 'fpr', 'precision', 'f1', and raw counts
    'tp', 'fp', 'fn', 'tn'.
    """
    excluded = np.asarray(excluded, dtype=bool)
    true_anomalous = np.asarray(true_anomalous, dtype=bool)

    tp = int(np.sum(excluded & true_anomalous))
    fp = int(np.sum(excluded & ~true_anomalous))
    fn = int(np.sum(~excluded & true_anomalous))
    tn = int(np.sum(~excluded & ~true_anomalous))

    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = (
        2 * tp / (2 * tp + fp + fn)
        if (2 * tp + fp + fn) > 0
        else 0.0
    )

    return {
        "tpr": float(tpr),
        "fpr": float(fpr),
        "precision": float(precision),
        "f1": float(f1),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }

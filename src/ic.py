"""
Information Content (IC) — interval-probability definition.

IC measures distributional inconsistency: how improbable is each observation
under the ensemble's own background distribution?

Definition:
    P(y) = (1/N) Σ_i  N(y; x_i, σ_i)      [Gaussian mixture background]

    p_k = ∫_{x_k - σ_k}^{x_k + σ_k} P(y) dy   [interval probability]

    I_k = -log₂(p_k)                         [information content in bits]

Aggregates:
    AIPP = (1/N) Σ_k I_k                     [average information per point]
    TI   = Σ_k I_k                            [total information]

IC requires no parametric signal model but is calibrated under specific
null noise assumptions.

Analytic evaluation via Gaussian CDF (scipy.special.erf). No numerical
integration, no KDE.

Expected null behaviour:
    For Gaussian i.i.d. with σ_data = σ_declared = 1, as N → ∞:
        The mixture P(y) converges to N(0, √2) (convolution of data
        distribution with kernel), giving AIPP → ≈ 1.25 bit.
        The earlier claim of 0.55 bit was incorrect — see logbook entry 001.

Author: U. Warring
Version: 0.1.0
Status: WP1 implementation
"""

import numpy as np
from scipy.special import erf
from typing import Optional


def compute_ic(values: np.ndarray,
               sigmas: np.ndarray) -> np.ndarray:
    """
    Compute information content per point.

    Parameters
    ----------
    values : array of shape (N,)
        Observed values.
    sigmas : array of shape (N,)
        Per-point uncertainty estimates (must be > 0).

    Returns
    -------
    ic : array of shape (N,)
        Information content in bits per point.

    Notes
    -----
    Each component integral of N(y; x_i, σ_i) over [a, b] is:
        0.5 * [erf((b - x_i) / (σ_i √2)) - erf((a - x_i) / (σ_i √2))]

    The interval probability for point k is the average over all N components.
    """
    values = np.asarray(values, dtype=np.float64)
    sigmas = np.asarray(sigmas, dtype=np.float64)

    if values.shape != sigmas.shape:
        raise ValueError(
            f"values and sigmas must have the same shape: "
            f"{values.shape} vs {sigmas.shape}"
        )
    if values.ndim != 1:
        raise ValueError(f"Expected 1-D arrays, got ndim={values.ndim}")

    n = len(values)
    if n == 0:
        return np.array([], dtype=np.float64)
    if n == 1:
        p = erf(1.0 / np.sqrt(2.0))
        return np.array([-np.log2(p)])

    if np.any(sigmas <= 0):
        raise ValueError("All sigmas must be positive")

    # Interval bounds for each point k
    a = values - sigmas  # shape (N,)
    b = values + sigmas  # shape (N,)

    # Vectorised: erf arguments for all (k, i) pairs
    # b[k] - values[i] and a[k] - values[i], scaled by sigmas[i] * sqrt(2)
    sqrt2 = np.sqrt(2.0)
    si_sqrt2 = sigmas * sqrt2  # shape (N,)

    erf_upper = erf((b[:, None] - values[None, :]) / si_sqrt2[None, :])
    erf_lower = erf((a[:, None] - values[None, :]) / si_sqrt2[None, :])

    # Contribution matrix [k, i]: probability mass of component i in interval of k
    contributions = 0.5 * (erf_upper - erf_lower)

    # Interval probability: average over all N components
    p = np.mean(contributions, axis=1)

    # Clamp to avoid log(0)
    p = np.clip(p, 1e-300, 1.0)

    # Information content in bits
    ic = -np.log2(p)

    return ic


def compute_aipp(ic: np.ndarray) -> float:
    """Average information per point."""
    if len(ic) == 0:
        return 0.0
    return float(np.mean(ic))


def compute_ti(ic: np.ndarray) -> float:
    """Total information."""
    return float(np.sum(ic))


def aipp_gaussian_limit(sigma_data: float = 1.0,
                        sigma_declared: float = 1.0,
                        n_mc: int = 500_000) -> float:
    """
    Theoretical AIPP for Gaussian i.i.d. in the large-N limit.

    As N → ∞, the Gaussian mixture P(y) = (1/N) Σ N(y; x_i, σ_d)
    converges to the convolution of the true data distribution N(0, σ_data)
    with the Gaussian kernel N(0, σ_declared):

        P(y) → N(y; 0, σ_eff)  where σ_eff = √(σ_data² + σ_declared²)

    The expected AIPP is then:

        E[-log₂(Φ((X + σ_d)/σ_eff) - Φ((X - σ_d)/σ_eff))]

    where X ~ N(0, σ_data) and Φ is the standard normal CDF.

    For σ_data = σ_declared = 1: AIPP_∞ ≈ 1.25 bit.

    Note: the earlier claim of 0.55 bit was incorrect — it considered only
    the self-contribution erf(1/√2) and neglected that the mixture density
    broadens as N grows, reducing the interval probability.

    Parameters
    ----------
    sigma_data : float
        Standard deviation of the true data distribution.
    sigma_declared : float
        Declared per-point uncertainty (interval half-width).
    n_mc : int
        Number of Monte Carlo samples for the expectation.

    Returns
    -------
    aipp_limit : float
        Expected AIPP in bits.
    """
    from scipy.stats import norm as norm_dist
    sigma_eff = np.sqrt(sigma_data**2 + sigma_declared**2)
    rng = np.random.default_rng(42)
    x = rng.normal(0, sigma_data, n_mc)
    p = norm_dist.cdf((x + sigma_declared) / sigma_eff) - \
        norm_dist.cdf((x - sigma_declared) / sigma_eff)
    p = np.clip(p, 1e-300, 1.0)
    ic = -np.log2(p)
    return float(np.mean(ic))


def perturb_sigmas(sigmas: np.ndarray,
                   mode: str = 'random',
                   magnitude: float = 0.2,
                   rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Perturb declared uncertainties for σ-sensitivity analysis.

    Each σ_k is replaced by σ_k × (1 + ε_k), where ε_k depends on mode:
      - 'random':       ε_k ~ Uniform(-magnitude, +magnitude)  i.i.d.
      - 'systematic+':  ε_k = +magnitude  (coherent overestimate)
      - 'systematic-':  ε_k = -magnitude  (coherent underestimate)

    Parameters
    ----------
    sigmas : array of shape (N,)
        Original declared uncertainties (must be > 0).
    mode : str
        Perturbation mode: 'random', 'systematic+', or 'systematic-'.
    magnitude : float
        Perturbation magnitude (fraction of σ). Default 0.2 (±20%).
    rng : numpy Generator, optional
        Random number generator (used only for 'random' mode).

    Returns
    -------
    perturbed : array of shape (N,)
        Perturbed σ values, guaranteed > 0.
    """
    sigmas = np.asarray(sigmas, dtype=np.float64)
    if mode == 'random':
        if rng is None:
            rng = np.random.default_rng()
        eps = rng.uniform(-magnitude, magnitude, sigmas.shape)
    elif mode == 'systematic+':
        eps = magnitude
    elif mode == 'systematic-':
        eps = -magnitude
    else:
        raise ValueError(f"Unknown mode: {mode!r}. "
                         f"Use 'random', 'systematic+', or 'systematic-'.")
    perturbed = sigmas * (1.0 + eps)
    # Ensure positivity (relevant for large random perturbations)
    perturbed = np.maximum(perturbed, 1e-10)
    return perturbed


def verify_sigmas(values: np.ndarray,
                  sigmas: np.ndarray,
                  window: int = 20,
                  factor_threshold: float = 2.0) -> np.ndarray:
    """
    Check declared σ against observed variance over a trailing window.

    Parameters
    ----------
    values : array of shape (T,) or (T, N)
        Time series. If 2-D, columns are nodes.
    sigmas : array matching values shape
        Declared uncertainties.
    window : int
        Trailing window for empirical σ.
    factor_threshold : float
        Flag if ratio exceeds threshold in either direction.

    Returns
    -------
    flags : boolean array, same shape as values
        True where discrepancy exceeds threshold.
    """
    values = np.asarray(values, dtype=np.float64)
    sigmas = np.asarray(sigmas, dtype=np.float64)

    is_1d = values.ndim == 1
    if is_1d:
        values = values[:, None]
        sigmas = sigmas[:, None]

    t, n_nodes = values.shape
    flags = np.zeros((t, n_nodes), dtype=bool)

    for col in range(n_nodes):
        for i in range(window, t):
            empirical = np.std(values[i - window:i, col])
            declared = sigmas[i, col]
            if declared > 0:
                ratio = empirical / declared
                if ratio > factor_threshold or ratio < 1.0 / factor_threshold:
                    flags[i, col] = True

    if is_1d:
        flags = flags.squeeze()

    return flags

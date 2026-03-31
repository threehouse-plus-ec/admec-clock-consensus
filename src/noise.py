"""
Noise generators for null-model calibration (WP1) and clock simulation (WP2).

Power-law noise types following the standard h_α hierarchy:
    h_α =  0  →  white frequency noise
    h_α = -1  →  flicker frequency noise (1/f)
    h_α = -2  →  random-walk frequency noise (1/f²)

Heavy-tailed models:
    Symmetric Pareto (power-law tails, finite variance for α > 2)

Author: U. Warring
Version: 0.1.0
Status: WP1 implementation
"""

import numpy as np
from typing import Optional


def generate_pareto_symmetric(n: int,
                              alpha: float,
                              rng: Optional[np.random.Generator] = None
                              ) -> np.ndarray:
    """
    Generate symmetric Pareto-distributed samples.

    Samples from a Pareto distribution and symmetrises by random sign flip.
    Centred to zero mean. For α > 2, variance is finite.

    Parameters
    ----------
    n : int
        Number of samples.
    alpha : float
        Shape parameter (tail index). Must be > 2 for finite variance.
    rng : numpy Generator, optional

    Returns
    -------
    values : array of shape (n,)
    """
    if rng is None:
        rng = np.random.default_rng()
    # Pareto type I: P(X > x) = x^{-alpha} for x >= 1
    raw = (rng.pareto(alpha, n) + 1.0)  # shift to x >= 1
    signs = rng.choice([-1, 1], n)
    values = raw * signs
    values -= np.mean(values)  # centre
    return values


def generate_flicker(n: int,
                     H: float = 0.9,
                     rng: Optional[np.random.Generator] = None
                     ) -> np.ndarray:
    """
    Generate fractional Gaussian noise (fGn) with Hurst exponent H.

    Uses the Davies-Harte (circulant embedding) method for exact synthesis.
    H = 0.5 gives white noise; H > 0.5 gives long-memory (positive correlation);
    H = 0.9 approximates 1/f noise over the relevant frequency band.

    Parameters
    ----------
    n : int
        Number of samples.
    H : float
        Hurst exponent, 0 < H < 1. Default 0.9 (flicker-like).
    rng : numpy Generator, optional

    Returns
    -------
    values : array of shape (n,)
    """
    if rng is None:
        rng = np.random.default_rng()

    # Autocovariance of fGn: γ(k) = 0.5 * (|k-1|^{2H} - 2|k|^{2H} + |k+1|^{2H})
    def _autocov(k, H):
        k = np.abs(k)
        return 0.5 * (np.abs(k - 1) ** (2 * H) - 2 * np.abs(k) ** (2 * H)
                       + np.abs(k + 1) ** (2 * H))

    # Davies-Harte: embed in circulant of size 2m where m >= n
    m = 1
    while m < n:
        m *= 2

    # First row of the circulant matrix
    k = np.arange(m + 1)
    row = _autocov(k, H)
    # Mirror to get full circulant row of length 2m
    c = np.concatenate([row, row[-2:0:-1]])

    # Eigenvalues via FFT
    eigenvalues = np.fft.fft(c).real

    if np.any(eigenvalues < -1e-10):
        # Double the embedding size if eigenvalues are negative
        m *= 2
        k = np.arange(m + 1)
        row = _autocov(k, H)
        c = np.concatenate([row, row[-2:0:-1]])
        eigenvalues = np.fft.fft(c).real

    eigenvalues = np.maximum(eigenvalues, 0)

    # Generate complex Gaussian in frequency domain
    z = rng.standard_normal(2 * m) + 1j * rng.standard_normal(2 * m)
    w = np.fft.fft(np.sqrt(eigenvalues / (2 * m)) * z)

    return w.real[:n]


def generate_random_walk(n: int,
                         rng: Optional[np.random.Generator] = None
                         ) -> np.ndarray:
    """
    Generate random-walk frequency noise (cumulative sum of white noise).

    This models h_α = -2 (random-walk frequency). The variance grows
    with sample index, making it non-stationary.

    Parameters
    ----------
    n : int
        Number of samples.
    rng : numpy Generator, optional

    Returns
    -------
    values : array of shape (n,)
    """
    if rng is None:
        rng = np.random.default_rng()
    increments = rng.standard_normal(n)
    return np.cumsum(increments)


def generate_ar1(n: int,
                 rho: float = 0.7,
                 rng: Optional[np.random.Generator] = None
                 ) -> np.ndarray:
    """
    Generate AR(1) process with coefficient ρ.

    Stationary marginal variance = 1 (innovation variance scaled).

    Parameters
    ----------
    n : int
        Number of samples.
    rho : float
        AR(1) coefficient. |ρ| < 1 for stationarity.
    rng : numpy Generator, optional

    Returns
    -------
    values : array of shape (n,)
    """
    if rng is None:
        rng = np.random.default_rng()
    innovation_std = np.sqrt(1 - rho ** 2)
    values = np.zeros(n)
    values[0] = rng.normal()
    for i in range(1, n):
        values[i] = rho * values[i - 1] + rng.normal() * innovation_std
    return values

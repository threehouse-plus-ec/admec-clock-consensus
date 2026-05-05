"""Plot ARP topology-reference overlays from exported metrics."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from analysis.metrics.deviation_metrics import DeviationDecomposition


def plot_reference_overlay(
    k_bar_values: Sequence[float],
    observed_ratios: Sequence[float],
    *,
    N: int,
    labels: Sequence[str] | None = None,
    ax=None,
):
    """Plot observed local/central ratios against the ``N/k_bar`` reference."""

    import matplotlib.pyplot as plt

    axis = ax if ax is not None else plt.subplots(figsize=(5, 3.2))[1]
    k_bar = np.asarray(k_bar_values, dtype=float)
    observed = np.asarray(observed_ratios, dtype=float)
    if k_bar.shape != observed.shape:
        raise ValueError("k_bar_values and observed_ratios must have matching shape")
    if np.any(k_bar <= 0.0):
        raise ValueError("k_bar_values must be positive")

    reference = float(N) / k_bar
    axis.plot(k_bar, reference, color="black", linewidth=1.5, label="N/k_bar reference")
    axis.scatter(k_bar, observed, color="#0072B2", zorder=3, label="exported result")
    if labels is not None:
        if len(labels) != len(k_bar):
            raise ValueError("labels must match k_bar_values")
        for x_value, y_value, label in zip(k_bar, observed, labels):
            axis.annotate(str(label), (x_value, y_value), xytext=(4, 4), textcoords="offset points")

    axis.set_xlabel(r"$\bar{k}$ (mean accessible-set size)")
    axis.set_ylabel("MSE_local / MSE_cent")
    axis.legend(frameon=False)
    return axis


def plot_deviation_decomposition(
    decompositions: Sequence[DeviationDecomposition],
    *,
    labels: Sequence[str] | None = None,
    ax=None,
):
    """Plot total, Jensen, and residual deviations with sign annotation."""

    import matplotlib.pyplot as plt

    axis = ax if ax is not None else plt.subplots(figsize=(6, 3.2))[1]
    x = np.arange(len(decompositions))
    total = np.array([item.delta_total for item in decompositions], dtype=float)
    jensen = np.array([item.delta_jensen for item in decompositions], dtype=float)
    residual = np.array([item.delta_residual for item in decompositions], dtype=float)

    width = 0.24
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.bar(x - width, total, width, label=r"$\Delta_{\mathrm{total}}$", color="#0072B2")
    axis.bar(x, jensen, width, label=r"$\Delta_J \geq 0$", color="#009E73")
    axis.bar(x + width, residual, width, label=r"$\Delta_{\mathrm{res}}$", color="#D55E00")
    for xpos, value in zip(x + width, residual):
        sign = "helpful" if value < 0 else "degrading" if value > 0 else "on reference"
        axis.annotate(sign, (xpos, value), xytext=(0, 4), textcoords="offset points", ha="center")

    if labels is not None:
        if len(labels) != len(decompositions):
            raise ValueError("labels must match decompositions")
        axis.set_xticks(x)
        axis.set_xticklabels(labels, rotation=30, ha="right")
    else:
        axis.set_xticks(x)

    axis.set_ylabel("Deviation")
    axis.legend(frameon=False)
    return axis

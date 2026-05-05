"""Heteroscedastic helpers for the ARP reference model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .reference_model import central_variance, local_variance


@dataclass(frozen=True)
class HeteroscedasticReference:
    """Central/local variance comparison under exported sigmas and masks."""

    central: np.ndarray | float
    local: np.ndarray

    @property
    def local_to_central_ratio(self) -> np.ndarray:
        return np.asarray(self.local, dtype=float) / np.asarray(self.central, dtype=float)[
            ..., None
        ]


def heteroscedastic_reference(
    sigmas: np.ndarray,
    accessible: np.ndarray,
    *,
    include_self: bool = False,
) -> HeteroscedasticReference:
    """Compute central and ideal-local variances for heteroscedastic exports."""

    return HeteroscedasticReference(
        central=central_variance(sigmas),
        local=local_variance(sigmas, accessible, include_self=include_self),
    )


"""Analytic reference models.

Modules in this package must not import from the simulation layer. They consume
arrays exported by campaigns or synthetic arrays created directly in tests.
"""

from .reference_model import (
    ENDORSEMENT_MARKER,
    ReferenceAssumptions,
    central_variance,
    homogeneous_mse_ratio,
    homogeneous_mse_ratio_from_neighbor_count,
    local_variance,
)

__all__ = [
    "ENDORSEMENT_MARKER",
    "ReferenceAssumptions",
    "central_variance",
    "homogeneous_mse_ratio",
    "homogeneous_mse_ratio_from_neighbor_count",
    "local_variance",
]


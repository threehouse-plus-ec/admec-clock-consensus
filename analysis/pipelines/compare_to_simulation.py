"""Compare exported simulation data against the ARP analytic reference.

This module enforces the ARP data boundary: it loads arrays from export files
and does not import clocks, networks, estimators, or campaign harnesses.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from analysis.analytic.heteroscedastic import HeteroscedasticReference, heteroscedastic_reference
from analysis.analytic.reference_model import ENDORSEMENT_MARKER, ReferenceAssumptions
from analysis.metrics.deviation_metrics import (
    AdmecDelta,
    DeviationDecomposition,
    admec_vs_ideal_local,
    deviation_decomposition,
)


@dataclass(frozen=True)
class SimulationExport:
    """Minimal exported data required for ARP comparison."""

    neighbor_count: np.ndarray
    local_mse: float
    central_mse: float
    topology_id: str
    seed: int
    delay_parameters: dict[str, Any]
    assumption_flags: dict[str, Any]
    sigmas: np.ndarray | None = None
    accessible_mask: np.ndarray | None = None
    admec_mse: float | None = None
    ideal_local_mse: float | None = None


@dataclass(frozen=True)
class ComparisonResult:
    """ARP comparison result with mandatory assumption metadata."""

    topology_id: str
    seed: int
    assumptions: ReferenceAssumptions
    deviation: DeviationDecomposition
    admec_delta: AdmecDelta | None
    endorsement_marker: str = ENDORSEMENT_MARKER


@dataclass(frozen=True)
class HeteroscedasticComparisonResult:
    """ARP comparison with both homogeneous and heteroscedastic references."""

    topology_id: str
    seed: int
    assumptions: ReferenceAssumptions
    homogeneous: DeviationDecomposition
    heteroscedastic: HeteroscedasticReference
    admec_delta: AdmecDelta | None
    endorsement_marker: str = ENDORSEMENT_MARKER


def compare_export(
    export: SimulationExport,
    *,
    N: int,
    include_self: bool = True,
) -> ComparisonResult:
    """Compute ARP metrics for one exported simulation record."""

    deviation = deviation_decomposition(
        export.local_mse,
        export.central_mse,
        N,
        export.neighbor_count,
        include_self=include_self,
    )
    admec_delta = None
    if export.admec_mse is not None and export.ideal_local_mse is not None:
        admec_delta = admec_vs_ideal_local(export.admec_mse, export.ideal_local_mse)

    return ComparisonResult(
        topology_id=export.topology_id,
        seed=export.seed,
        assumptions=ReferenceAssumptions(),
        deviation=deviation,
        admec_delta=admec_delta,
    )


def compare_heteroscedastic_export(
    export: SimulationExport,
    *,
    N: int,
    include_self: bool = True,
) -> HeteroscedasticComparisonResult:
    """Compute ARP metrics with both homogeneous and heteroscedastic references.

    Requires ``export.sigmas`` and ``export.accessible_mask`` to be set.
    """

    if export.sigmas is None or export.accessible_mask is None:
        raise ValueError(
            "Heteroscedastic comparison requires sigmas and accessible_mask"
        )

    homogeneous = deviation_decomposition(
        export.local_mse,
        export.central_mse,
        N,
        export.neighbor_count,
        include_self=include_self,
    )
    heteroscedastic = heteroscedastic_reference(
        export.sigmas,
        export.accessible_mask,
        include_self=include_self,
    )
    admec_delta = None
    if export.admec_mse is not None and export.ideal_local_mse is not None:
        admec_delta = admec_vs_ideal_local(export.admec_mse, export.ideal_local_mse)

    return HeteroscedasticComparisonResult(
        topology_id=export.topology_id,
        seed=export.seed,
        assumptions=ReferenceAssumptions(),
        homogeneous=homogeneous,
        heteroscedastic=heteroscedastic,
        admec_delta=admec_delta,
    )


def load_csv_matrix(path: str | Path, *, delimiter: str = ",") -> np.ndarray:
    """Load a numeric CSV matrix from an ARP export."""

    return np.loadtxt(Path(path), delimiter=delimiter)


def load_npz_export(
    path: str | Path,
    *,
    neighbor_count_key: str = "k_i",
    local_mse_key: str = "local_mse",
    central_mse_key: str = "central_mse",
    topology_id_key: str = "topology_id",
    seed_key: str = "seed",
    delay_parameters_key: str = "delay_parameters",
    assumption_flags_key: str = "assumption_flags",
    sigmas_key: str = "sigmas",
    accessible_mask_key: str = "accessible_mask",
    admec_mse_key: str = "admec_mse",
    ideal_local_mse_key: str = "ideal_local_mse",
) -> SimulationExport:
    """Load a single-record ARP export from an ``.npz`` archive.

    ``.npz`` is supported for existing local archives. The analytic layer still
    consumes only exported arrays and metadata, never simulation code.
    """

    with np.load(Path(path), allow_pickle=True) as archive:
        keys = set(archive.files)
        _require_keys(keys, [neighbor_count_key, local_mse_key, central_mse_key])

        return SimulationExport(
            neighbor_count=np.asarray(archive[neighbor_count_key], dtype=float),
            local_mse=float(np.asarray(archive[local_mse_key])),
            central_mse=float(np.asarray(archive[central_mse_key])),
            topology_id=_load_scalar_metadata(
                archive,
                topology_id_key,
                default="unknown",
            ),
            seed=int(_load_scalar_metadata(archive, seed_key, default=-1)),
            delay_parameters=_load_dict_metadata(archive, delay_parameters_key),
            assumption_flags=_load_dict_metadata(archive, assumption_flags_key),
            sigmas=_load_optional_array(archive, sigmas_key),
            accessible_mask=_load_optional_array(archive, accessible_mask_key, dtype=bool),
            admec_mse=_load_optional_float(archive, admec_mse_key),
            ideal_local_mse=_load_optional_float(archive, ideal_local_mse_key),
        )


def load_hdf5_export(
    path: str | Path,
    *,
    neighbor_count_key: str = "k_i",
    local_mse_key: str = "local_mse",
    central_mse_key: str = "central_mse",
    topology_id_key: str = "topology_id",
    seed_key: str = "seed",
    delay_parameters_key: str = "delay_parameters",
    assumption_flags_key: str = "assumption_flags",
    sigmas_key: str = "sigmas",
    accessible_mask_key: str = "accessible_mask",
    admec_mse_key: str = "admec_mse",
    ideal_local_mse_key: str = "ideal_local_mse",
) -> SimulationExport:
    """Load a single-record ARP export from HDF5 if ``h5py`` is installed."""

    try:
        import h5py
    except ImportError as exc:
        raise ImportError("HDF5 exports require optional dependency h5py") from exc

    with h5py.File(Path(path), "r") as archive:
        _require_keys(set(archive.keys()), [neighbor_count_key, local_mse_key, central_mse_key])
        return SimulationExport(
            neighbor_count=np.asarray(archive[neighbor_count_key], dtype=float),
            local_mse=float(np.asarray(archive[local_mse_key])),
            central_mse=float(np.asarray(archive[central_mse_key])),
            topology_id=_hdf5_metadata(archive, topology_id_key, default="unknown"),
            seed=int(_hdf5_metadata(archive, seed_key, default=-1)),
            delay_parameters=_hdf5_dict_metadata(archive, delay_parameters_key),
            assumption_flags=_hdf5_dict_metadata(archive, assumption_flags_key),
            sigmas=_hdf5_optional_array(archive, sigmas_key),
            accessible_mask=_hdf5_optional_array(archive, accessible_mask_key, dtype=bool),
            admec_mse=_hdf5_optional_float(archive, admec_mse_key),
            ideal_local_mse=_hdf5_optional_float(archive, ideal_local_mse_key),
        )


def _require_keys(keys: set[str], required: list[str]) -> None:
    missing = sorted(set(required) - keys)
    if missing:
        raise KeyError(f"missing required ARP export key(s): {', '.join(missing)}")


def _load_optional_float(archive: Any, key: str) -> float | None:
    if key not in archive.files:
        return None
    return float(np.asarray(archive[key]))


def _load_optional_array(archive: Any, key: str, dtype: type | None = None) -> np.ndarray | None:
    if key not in archive.files:
        return None
    if dtype is not None:
        return np.asarray(archive[key], dtype=dtype)
    return np.asarray(archive[key])


def _load_scalar_metadata(archive: Any, key: str, *, default: Any) -> Any:
    if key not in archive.files:
        return default
    value = np.asarray(archive[key])
    if value.shape == ():
        return value.item()
    return value.tolist()


def _load_dict_metadata(archive: Any, key: str) -> dict[str, Any]:
    if key not in archive.files:
        return {}
    value = np.asarray(archive[key], dtype=object)
    if value.shape == ():
        item = value.item()
        if isinstance(item, dict):
            return dict(item)
    raise ValueError(f"{key} must be a scalar dict metadata object")


def _hdf5_optional_float(archive: Any, key: str) -> float | None:
    if key not in archive:
        return None
    return float(np.asarray(archive[key]))


def _hdf5_optional_array(archive: Any, key: str, dtype: type | None = None) -> np.ndarray | None:
    if key not in archive:
        return None
    if dtype is not None:
        return np.asarray(archive[key], dtype=dtype)
    return np.asarray(archive[key])


def _hdf5_metadata(archive: Any, key: str, *, default: Any) -> Any:
    if key not in archive.attrs and key not in archive:
        return default
    if key in archive.attrs:
        value = archive.attrs[key]
    else:
        value = np.asarray(archive[key])
        if value.shape == ():
            value = value.item()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def _hdf5_dict_metadata(archive: Any, key: str) -> dict[str, Any]:
    value = _hdf5_metadata(archive, key, default={})
    if isinstance(value, dict):
        return dict(value)
    if value == {}:
        return {}
    raise ValueError(f"{key} must be stored as dict metadata")


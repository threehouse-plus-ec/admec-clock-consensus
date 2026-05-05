"""Tests for ARP analytic reference formulas."""

import numpy as np
import pytest

from analysis.analytic.reference_model import (
    ENDORSEMENT_MARKER,
    ReferenceAssumptions,
    central_variance,
    homogeneous_mse_ratio,
    homogeneous_mse_ratio_from_neighbor_count,
    local_variance,
)
from analysis.analytic.heteroscedastic import heteroscedastic_reference
from analysis.analytic.fisher_information_stub import unavailable_in_v02


class TestBoundaryEnforcement:
    def test_analysis_package_does_not_import_simulation_code(self):
        """ARP must not transitively load clocks, networks, estimators, or campaigns."""
        import sys

        # Clear any prior simulation imports so the test is self-contained
        simulation_modules = {
            k for k in sys.modules if k.startswith(("src.", "clocks", "network", "estimators", "metrics", "classify", "constraints", "campaign"))
        }
        for mod in list(simulation_modules):
            del sys.modules[mod]

        import analysis

        loaded = {k for k in sys.modules if k.startswith(("src.", "clocks", "network", "estimators", "metrics", "classify", "constraints", "campaign"))}
        assert not loaded, f"ARP leaked simulation modules: {loaded}"


class TestReferenceModel:
    def test_central_variance_homogeneous(self):
        sigmas = np.full(4, 2.0)

        assert central_variance(sigmas) == pytest.approx(1.0)

    def test_central_variance_heteroscedastic(self):
        sigmas = np.array([1.0, 2.0, 4.0])
        expected = 1.0 / (1.0 + 0.25 + 0.0625)

        assert central_variance(sigmas) == pytest.approx(expected)

    def test_local_variance_static_mask(self):
        sigmas = np.array([1.0, 2.0, 1.0])
        accessible = np.array(
            [
                [True, True, False],
                [False, True, False],
                [True, False, True],
            ]
        )

        local = local_variance(sigmas, accessible)

        assert np.allclose(local, np.array([0.8, 4.0, 0.5]))

    def test_local_variance_can_add_self_to_neighbor_export(self):
        sigmas = np.ones(2)
        neighbor_only = np.array(
            [
                [False, True],
                [False, False],
            ]
        )

        local = local_variance(sigmas, neighbor_only, include_self=True)

        assert np.allclose(local, np.array([0.5, 1.0]))

    def test_local_variance_time_varying_sigmas_static_mask(self):
        sigmas = np.array(
            [
                [1.0, 1.0],
                [1.0, 2.0],
            ]
        )
        accessible = np.array(
            [
                [True, False],
                [True, True],
            ]
        )

        local = local_variance(sigmas, accessible)

        assert np.allclose(local, np.array([[1.0, 0.5], [1.0, 0.8]]))

    def test_homogeneous_mse_ratio(self):
        assert homogeneous_mse_ratio(10, 5) == pytest.approx(2.0)
        assert homogeneous_mse_ratio_from_neighbor_count(10, 4) == pytest.approx(2.0)

    def test_heteroscedastic_reference_ratio(self):
        sigmas = np.ones(3)
        accessible = np.eye(3, dtype=bool)

        reference = heteroscedastic_reference(sigmas, accessible)

        assert reference.central == pytest.approx(1.0 / 3.0)
        assert np.allclose(reference.local, np.ones(3))
        assert np.allclose(reference.local_to_central_ratio, np.full(3, 3.0))

    def test_invalid_sigma_rejected(self):
        with pytest.raises(ValueError, match="positive"):
            central_variance(np.array([1.0, 0.0]))

    def test_assumption_marker_is_full_text(self):
        assumptions = ReferenceAssumptions()

        assert assumptions.endorsement_marker == ENDORSEMENT_MARKER
        assert "no parity implied" in assumptions.endorsement_marker
        assert "not a physical law" in assumptions.endorsement_marker

    def test_local_variance_time_varying_mask_3d(self):
        """Regression: 3D (T, N, N) mask branch must compute per-timestep local variance."""
        sigmas = np.array(
            [
                [1.0, 1.0, 1.0],
                [1.0, 2.0, 1.0],
            ]
        )
        # t=0: fully connected
        # t=1: node 0 sees {0,1}, node 1 sees {1}, node 2 sees {1,2}
        accessible = np.array(
            [
                [
                    [True, True, True],
                    [True, True, True],
                    [True, True, True],
                ],
                [
                    [True, True, False],
                    [False, True, False],
                    [False, True, True],
                ],
            ]
        )

        local = local_variance(sigmas, accessible)

        # t=0: all see all 3 nodes with sigma=1.0 -> variance = 1/3 each
        # t=1: node 0 sees {0,1} with sigma [1.0, 2.0] -> info = 1 + 0.25 = 1.25 -> var = 0.8
        #      node 1 sees {1} with sigma 2.0 -> var = 4.0
        #      node 2 sees {1,2} with sigma [2.0, 1.0] -> info = 0.25 + 1 = 1.25 -> var = 0.8
        expected = np.array(
            [
                [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
                [0.8, 4.0, 0.8],
            ]
        )
        assert np.allclose(local, expected)

    def test_fisher_information_stub_is_non_load_bearing(self):
        with pytest.raises(NotImplementedError, match="outside ARP v0.2"):
            unavailable_in_v02()


"""Tests for ARP topology and deviation metrics."""

import numpy as np
import pytest

from analysis.metrics.deviation_metrics import (
    admec_vs_ideal_local,
    deviation_decomposition,
    residual_deviation,
    residual_sign_label,
    total_deviation,
)
from analysis.metrics.jensen_gap import jensen_gap, jensen_gap_components
from analysis.metrics.k_eff import (
    effective_neighborhood_size,
    k_bar,
    k_eff,
    mean_accessible_set_size,
    total_accessible_count,
)
from analysis.pipelines.compare_to_simulation import (
    compare_export,
    compare_heteroscedastic_export,
    load_csv_matrix,
    load_npz_export,
)


class TestEffectiveNeighborhood:
    def test_mean_accessible_set_size_adds_self_to_exported_neighbor_counts(self):
        counts = np.array([[2, 0], [4, 2]])

        assert mean_accessible_set_size(counts) == pytest.approx(3.0)
        assert k_bar(counts) == pytest.approx(3.0)

    def test_backward_compatibility_aliases_match_new_names(self):
        counts = np.array([1, 2, 3])

        assert effective_neighborhood_size(counts) == mean_accessible_set_size(counts)
        assert k_eff(counts) == k_bar(counts)

    def test_total_accessible_count_can_accept_counts_that_include_self(self):
        counts = np.array([1, 3, 5])

        total = total_accessible_count(counts, include_self=False)

        assert np.allclose(total, counts)


class TestJensenGap:
    def test_uniform_topology_has_zero_jensen_gap(self):
        counts = np.array([2, 2, 2])

        assert jensen_gap(4, counts) == pytest.approx(0.0)

    def test_heterogeneous_topology_has_positive_jensen_gap(self):
        counts = np.array([0, 3])

        components = jensen_gap_components(4, counts)

        assert components.expected_ratio == pytest.approx(2.5)
        assert components.ratio_at_k_bar == pytest.approx(1.6)
        assert components.gap == pytest.approx(0.9)
        assert components.gap > 0.0
        assert components.k_bar == pytest.approx(2.5)


class TestDeviationMetrics:
    def test_deviation_decomposition_uses_corrected_residual_sign(self):
        result = deviation_decomposition(
            local_mse=1.4,
            central_mse=1.0,
            N=4,
            neighbor_count=np.array([0, 3]),
        )

        assert result.reference_ratio == pytest.approx(1.6)
        assert result.delta_total == pytest.approx(-0.2)
        assert result.delta_jensen == pytest.approx(0.9)
        assert result.delta_residual == pytest.approx(-1.1)
        assert result.residual_interpretation.startswith("helpful violation")

    def test_total_deviation_rejects_impossible_k_bar(self):
        with pytest.raises(ValueError, match="cannot exceed N"):
            total_deviation(local_mse=1.0, central_mse=1.0, N=4, k_bar=5.0)

    def test_residual_sign_labels_are_explicit(self):
        assert residual_sign_label(-0.1).startswith("helpful violation")
        assert residual_sign_label(0.1).startswith("unmodelled degradation")
        assert residual_sign_label(0.0).startswith("on reference")

    def test_residual_deviation_subtracts_jensen_gap(self):
        assert residual_deviation(-0.2, 0.9) == pytest.approx(-1.1)

    def test_admec_delta_has_no_fixed_sign_assumption(self):
        information_loss = admec_vs_ideal_local(0.7, 0.5)
        bias_reduction = admec_vs_ideal_local(0.4, 0.5)

        assert information_loss.delta == pytest.approx(0.2)
        assert information_loss.interpretation == "information loss dominates"
        assert bias_reduction.delta == pytest.approx(-0.1)
        assert bias_reduction.interpretation == "bias reduction dominates"


class TestExportPipeline:
    def test_load_npz_export_and_compare_without_simulation_code(self, tmp_path):
        path = tmp_path / "arp_export.npz"
        np.savez(
            path,
            k_i=np.array([0, 3]),
            local_mse=np.array(1.4),
            central_mse=np.array(1.0),
            topology_id=np.array("S-test"),
            seed=np.array(7),
            delay_parameters=np.array({"delay": 2}, dtype=object),
            assumption_flags=np.array({"null_signal": True}, dtype=object),
            admec_mse=np.array(0.4),
            ideal_local_mse=np.array(0.5),
        )

        export = load_npz_export(path)
        result = compare_export(export, N=4)

        assert export.topology_id == "S-test"
        assert export.seed == 7
        assert export.delay_parameters == {"delay": 2}
        assert export.assumption_flags == {"null_signal": True}
        assert result.deviation.delta_residual == pytest.approx(-1.1)
        assert result.admec_delta is not None
        assert result.admec_delta.interpretation == "bias reduction dominates"
        assert "not a physical law" in result.endorsement_marker

    def test_load_csv_matrix(self, tmp_path):
        path = tmp_path / "k_i.csv"
        np.savetxt(path, np.array([[0, 1], [2, 3]]), delimiter=",")

        loaded = load_csv_matrix(path)

        assert np.allclose(loaded, np.array([[0, 1], [2, 3]]))

    @pytest.mark.skipif(
        __import__("importlib").util.find_spec("h5py") is None,
        reason="h5py not installed",
    )
    def test_load_hdf5_export_with_heteroscedastic_fields(self, tmp_path):
        import h5py

        path = tmp_path / "arp_export.h5"
        with h5py.File(path, "w") as f:
            f.create_dataset("k_i", data=np.array([0, 3]))
            f.create_dataset("local_mse", data=1.4)
            f.create_dataset("central_mse", data=1.0)
            f.create_dataset("sigmas", data=np.ones(4))
            f.create_dataset("accessible_mask", data=np.eye(4, dtype=bool))
            f.attrs["topology_id"] = "S-test"
            f.attrs["seed"] = 7

        from analysis.pipelines.compare_to_simulation import load_hdf5_export

        export = load_hdf5_export(path)
        assert export.sigmas is not None
        assert export.accessible_mask is not None
        assert np.allclose(export.sigmas, np.ones(4))
        assert np.allclose(export.accessible_mask, np.eye(4, dtype=bool))

    def test_heteroscedastic_comparison_requires_sigmas_and_mask(self, tmp_path):
        path = tmp_path / "arp_export.npz"
        np.savez(
            path,
            k_i=np.array([0, 3]),
            local_mse=np.array(1.4),
            central_mse=np.array(1.0),
            topology_id=np.array("S-test"),
            seed=np.array(7),
            delay_parameters=np.array({}, dtype=object),
            assumption_flags=np.array({}, dtype=object),
        )

        export = load_npz_export(path)
        with pytest.raises(ValueError, match="sigmas and accessible_mask"):
            compare_heteroscedastic_export(export, N=4)

    def test_heteroscedastic_comparison_computes_both_references(self, tmp_path):
        path = tmp_path / "arp_export.npz"
        np.savez(
            path,
            k_i=np.array([0, 3]),
            local_mse=np.array(1.4),
            central_mse=np.array(1.0),
            sigmas=np.array([1.0, 1.0, 1.0, 1.0]),
            accessible_mask=np.eye(4, dtype=bool),
            topology_id=np.array("S-test"),
            seed=np.array(7),
            delay_parameters=np.array({}, dtype=object),
            assumption_flags=np.array({}, dtype=object),
        )

        export = load_npz_export(path)
        result = compare_heteroscedastic_export(export, N=4, include_self=True)

        assert result.homogeneous.delta_residual == pytest.approx(-1.1)
        # Heteroscedastic: 4 independent nodes, each sees only itself -> local variance = 1.0
        assert np.allclose(result.heteroscedastic.local, np.ones(4))
        assert result.heteroscedastic.central == pytest.approx(0.25)

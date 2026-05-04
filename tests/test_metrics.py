"""
Tests for WP2 simulation metrics (src/metrics.py).
"""

import numpy as np
import pytest
from scipy import stats

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from metrics import mse, collapse_index, structure_correlation, classification_metrics


class TestMSE:
    def test_zero(self):
        est = np.zeros((10, 5))
        assert mse(est) == 0.0

    def test_ones(self):
        est = np.ones((10, 5))
        assert mse(est) == 1.0

    def test_reference_offset(self):
        est = np.ones((10, 5))
        assert mse(est, reference=1.0) == 0.0

    def test_mixed(self):
        est = np.array([[0.0, 2.0], [4.0, 6.0]])
        assert mse(est) == (0 + 4 + 16 + 36) / 4


class TestCollapseIndex:
    def test_centralised_zero(self):
        """Centralised estimator: all nodes identical -> CI = 0."""
        est = np.ones((20, 10))
        sig = np.full((20, 10), 1.0)
        assert collapse_index(est, sig) == 0.0

    def test_spread_positive(self):
        """Estimates with spread -> CI > 0."""
        rng = np.random.default_rng(42)
        est = rng.normal(0, 1, (20, 10))
        sig = np.ones((20, 10))
        ci = collapse_index(est, sig)
        assert ci > 0.0

    def test_scale_invariance(self):
        """Doubling sigmas should halve CI."""
        rng = np.random.default_rng(42)
        est = rng.normal(0, 1, (20, 10))
        sig1 = np.ones((20, 10))
        sig2 = np.full((20, 10), 2.0)
        ci1 = collapse_index(est, sig1)
        ci2 = collapse_index(est, sig2)
        assert ci1 == pytest.approx(2.0 * ci2, rel=1e-10)


class TestStructureCorrelation:
    def test_perfect_correlation(self):
        """If estimates = 0 and Y = signal, residual = signal -> r = 1."""
        T, N = 100, 3
        t = np.arange(T)
        signals = np.zeros((T, N))
        signals[:, 0] = np.sin(2 * np.pi * t / 20)  # non-constant signal
        Y = signals.copy()
        estimates = np.zeros((T, N))

        r = structure_correlation(Y, estimates, signals, [0], onset_idx=0)
        assert r == pytest.approx(1.0, abs=1e-6)

    def test_zero_correlation(self):
        """If estimates absorb the signal, residual is noise -> r ≈ 0."""
        rng = np.random.default_rng(42)
        T = 200
        signal = np.sin(np.linspace(0, 4 * np.pi, T))
        noise = rng.normal(0, 0.1, T)
        Y = signal + noise
        estimates = signal.copy()  # perfectly absorb
        residuals = noise

        r = structure_correlation(
            Y[:, None],
            estimates[:, None],
            signal[:, None],
            [0],
            onset_idx=0,
        )
        # Residual is pure noise, so correlation with signal should be near 0
        assert abs(r) < 0.3

    def test_no_signal_clocks(self):
        r = structure_correlation(
            np.zeros((10, 2)),
            np.zeros((10, 2)),
            np.zeros((10, 2)),
            np.array([], dtype=int),
            onset_idx=0,
        )
        assert np.isnan(r)

    def test_constant_signal_preserved(self):
        """Constant signal with residual == signal -> ratio = 1.0."""
        T = 50
        signals = np.full((T, 1), 2.5)
        Y = signals.copy()
        estimates = np.zeros((T, 1))  # residual = signal
        r = structure_correlation(Y, estimates, signals, [0], onset_idx=0)
        assert r == pytest.approx(1.0, abs=1e-9)

    def test_constant_residual(self):
        """Constant signal with zero residual -> fully absorbed -> 0.0."""
        T = 50
        Y = np.ones((T, 1))
        estimates = np.ones((T, 1))  # residual = 0 everywhere
        signals = np.ones((T, 1))
        r = structure_correlation(Y, estimates, signals, [0], onset_idx=0)
        assert r == pytest.approx(0.0, abs=1e-9)


class TestClassificationMetrics:
    def test_perfect(self):
        excl = np.array([True, True, False, False])
        true = np.array([True, True, False, False])
        m = classification_metrics(excl, true)
        assert m["tpr"] == 1.0
        assert m["fpr"] == 0.0
        assert m["precision"] == 1.0
        assert m["f1"] == 1.0

    def test_all_wrong(self):
        excl = np.array([True, True, False, False])
        true = np.array([False, False, True, True])
        m = classification_metrics(excl, true)
        assert m["tpr"] == 0.0
        assert m["fpr"] == 1.0
        assert m["precision"] == 0.0

    def test_mixed(self):
        excl = np.array([True, True, False, False])
        true = np.array([True, False, True, False])
        m = classification_metrics(excl, true)
        assert m["tpr"] == 0.5  # 1 TP / (1 TP + 1 FN)
        assert m["fpr"] == 0.5  # 1 FP / (1 FP + 1 TN)
        assert m["precision"] == 0.5  # 1 TP / (1 TP + 1 FP)
        assert m["f1"] == 0.5

    def test_2d_arrays(self):
        excl = np.array([[True, False], [False, True]])
        true = np.array([[True, True], [False, False]])
        m = classification_metrics(excl, true)
        assert m["tp"] == 1
        assert m["fp"] == 1
        assert m["fn"] == 1
        assert m["tn"] == 1

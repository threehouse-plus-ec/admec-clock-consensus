"""
Tests for DG-1 threshold stability under power-law and long-memory nulls.

Extends the five-model test from test_ic.py::TestAIPPThresholdStability
with Pareto (heavy-tailed), fGn (long-memory), AR(1) ρ=0.9, and
random-walk null models.

Pass criterion: all pairwise 95th-percentile ratios within ×1.5.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)


class TestExtendedThresholdStability:
    """
    DG-1 test: threshold stability across ALL null models.

    Includes the original five models plus power-law, flicker,
    AR(1) ρ=0.9, and random-walk nulls.

    Criterion: all pairwise 95th-percentile ratios within ×1.5.
    """

    N = 50
    N_REAL = 300

    def _compute_aipp_distribution(self, model_name, rng):
        """Compute AIPP distribution for a noise model."""
        aipps = []
        for _ in range(self.N_REAL):
            values, sigmas = self._generate(model_name, rng)
            ic = compute_ic(values, sigmas)
            aipps.append(compute_aipp(ic))
        return np.array(aipps)

    def _generate(self, model_name, rng):
        n = self.N
        if model_name == "gaussian":
            return rng.normal(0, 1, n), np.ones(n)
        elif model_name == "heteroscedastic":
            s = np.exp(rng.normal(0, 0.5, n))
            return rng.normal(0, s), s
        elif model_name == "student_t_3":
            return rng.standard_t(3, n), np.ones(n) * np.sqrt(3)
        elif model_name == "student_t_5":
            return rng.standard_t(5, n), np.ones(n) * np.sqrt(5 / 3)
        elif model_name == "ar1_07":
            return generate_ar1(n, rho=0.7, rng=rng), np.ones(n)
        elif model_name == "pareto_25":
            v = generate_pareto_symmetric(n, alpha=2.5, rng=rng)
            return v, np.ones(n) * np.std(v)
        elif model_name == "pareto_30":
            v = generate_pareto_symmetric(n, alpha=3.0, rng=rng)
            return v, np.ones(n) * np.std(v)
        elif model_name == "fgn_09":
            v = generate_flicker(n, H=0.9, rng=rng)
            return v, np.ones(n) * max(np.std(v), 1e-6)
        elif model_name == "ar1_09":
            return generate_ar1(n, rho=0.9, rng=rng), np.ones(n)
        elif model_name == "random_walk":
            v = generate_random_walk(n, rng=rng)
            s = np.maximum(np.sqrt(np.arange(1, n + 1, dtype=float)), 1.0)
            return v, s
        else:
            raise ValueError(f"Unknown model: {model_name}")

    def test_all_models_within_1_5x(self):
        """All pairwise 95th-percentile ratios within ×1.5."""
        rng = np.random.default_rng(2026)
        models = [
            "gaussian", "heteroscedastic", "student_t_3", "student_t_5",
            "ar1_07", "pareto_25", "pareto_30", "fgn_09", "ar1_09",
            "random_walk"
        ]
        thresholds = {}
        for model in models:
            aipps = self._compute_aipp_distribution(model, rng)
            thresholds[model] = np.percentile(aipps, 95)

        thresh_values = list(thresholds.values())
        thresh_names = list(thresholds.keys())
        for i in range(len(thresh_values)):
            for j in range(i + 1, len(thresh_values)):
                ratio = max(thresh_values[i], thresh_values[j]) / \
                        min(thresh_values[i], thresh_values[j])
                assert ratio < 1.5, (
                    f"Threshold ratio {ratio:.3f} between "
                    f"{thresh_names[i]} ({thresh_values[i]:.4f}) and "
                    f"{thresh_names[j]} ({thresh_values[j]:.4f}) exceeds ×1.5"
                )

    @pytest.mark.parametrize("model", ["pareto_25", "pareto_30", "fgn_09",
                                        "ar1_09", "random_walk"])
    def test_new_model_vs_gaussian(self, model):
        """Each new model's 95th percentile within ×1.5 of Gaussian."""
        rng = np.random.default_rng(2026)
        gauss_aipps = self._compute_aipp_distribution("gaussian", rng)
        gauss_p95 = np.percentile(gauss_aipps, 95)

        rng2 = np.random.default_rng(2026)
        model_aipps = self._compute_aipp_distribution(model, rng2)
        model_p95 = np.percentile(model_aipps, 95)

        ratio = max(gauss_p95, model_p95) / min(gauss_p95, model_p95)
        assert ratio < 1.5, (
            f"{model}: P95={model_p95:.4f}, Gaussian P95={gauss_p95:.4f}, "
            f"ratio={ratio:.3f} exceeds ×1.5"
        )


class TestFiniteNBias:
    """
    Finite-N bias quantification.

    Fit AIPP(N) = AIPP_∞ + a/N + b/N² and verify the bias is < 1%
    for N ≥ 75.
    """

    def test_bias_below_1pct_at_n75(self):
        """Finite-N bias < 1% at N ≥ 75."""
        from ic import aipp_gaussian_limit
        limit = aipp_gaussian_limit()
        rng = np.random.default_rng(2026)

        Ns = np.array([10, 20, 50, 75, 100, 200, 500], dtype=float)
        means = []
        for n in Ns.astype(int):
            aipps = []
            for _ in range(200):
                values = rng.normal(0, 1, n)
                sigmas = np.ones(n)
                ic = compute_ic(values, sigmas)
                aipps.append(compute_aipp(ic))
            means.append(np.mean(aipps))

        means = np.array(means)

        # Fit a/N + b/N²
        X = np.column_stack([1.0 / Ns, 1.0 / Ns ** 2])
        y = means - limit
        coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        a, b = coeffs

        # Check bias at N=75
        bias_75 = a / 75 + b / 75 ** 2
        rel_75 = abs(bias_75) / limit
        assert rel_75 < 0.015, (
            f"Finite-N bias at N=75 is {rel_75:.3f} ({rel_75*100:.1f}%), "
            f"expected < 1.5%"
        )

        # Check bias at N=100
        bias_100 = a / 100 + b / 100 ** 2
        rel_100 = abs(bias_100) / limit
        assert rel_100 < 0.01, (
            f"Finite-N bias at N=100 is {rel_100:.3f} ({rel_100*100:.1f}%), "
            f"expected < 1%"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

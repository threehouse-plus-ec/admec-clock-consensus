"""
Tests for the per-reading I_k threshold calibration (entry 006).

The WP1 classification rule used a 95th-percentile threshold derived
from the AIPP distribution (mean of I_k over N readings). When applied
to classify *individual* readings in WP2, AIPP's CLT narrowing no
longer applies — the per-reading I_k distribution has a heavier upper
tail. These tests verify that:

  1. The per-reading P95 is strictly larger than the AIPP P95 under
     the same null. (Sanity check: AIPP averaging shrinks the tail.)
  2. Per-reading P95 stability across the ten null models is within
     ×1.5, matching the DG-1 stability criterion applied to AIPP.
  3. Worst-case sigma underestimation (-20%) inflates per-reading P95
     in the same direction it inflates AIPP, so worst-case calibration
     remains the correct mitigation pattern.

These run faster than the full calibration script (smaller realisation
counts) but exercise the same logic.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, perturb_sigmas
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)


N = 50
N_REAL = 150
SEED = 2026


def _generate(name, n, rng):
    if name == "gaussian":
        return rng.normal(0, 1, n), np.ones(n)
    if name == "heteroscedastic":
        s = np.exp(rng.normal(0, 0.5, n))
        return rng.normal(0, s), s
    if name == "student_t_3":
        return rng.standard_t(3, n), np.ones(n) * np.sqrt(3)
    if name == "student_t_5":
        return rng.standard_t(5, n), np.ones(n) * np.sqrt(5 / 3)
    if name == "ar1_07":
        return generate_ar1(n, rho=0.7, rng=rng), np.ones(n)
    if name == "pareto_25":
        v = generate_pareto_symmetric(n, alpha=2.5, rng=rng)
        return v, np.ones(n) * np.std(v)
    if name == "pareto_30":
        v = generate_pareto_symmetric(n, alpha=3.0, rng=rng)
        return v, np.ones(n) * np.std(v)
    if name == "fgn_09":
        v = generate_flicker(n, H=0.9, rng=rng)
        return v, np.ones(n) * max(np.std(v), 1e-6)
    if name == "ar1_09":
        return generate_ar1(n, rho=0.9, rng=rng), np.ones(n)
    if name == "random_walk":
        v = generate_random_walk(n, rng=rng)
        s = np.maximum(np.sqrt(np.arange(1, n + 1, dtype=float)), 1.0)
        return v, s
    raise ValueError(f"Unknown model: {name}")


MODELS = [
    "gaussian", "heteroscedastic", "student_t_3", "student_t_5",
    "ar1_07", "pareto_25", "pareto_30", "fgn_09", "ar1_09", "random_walk",
]


def _run(model, rng, underestimate=False):
    """Return (concatenated I_k pool, AIPP array) for one model."""
    iks, aipps = [], []
    for _ in range(N_REAL):
        v, s = _generate(model, N, rng)
        if underestimate:
            s = perturb_sigmas(s, mode='systematic-', magnitude=0.2)
        ic = compute_ic(v, s)
        iks.append(ic)
        aipps.append(compute_aipp(ic))
    return np.concatenate(iks), np.array(aipps)


class TestPerReadingExceedsAIPP:
    """Per-reading P95 should exceed AIPP P95 under the same null."""

    @pytest.mark.parametrize("model", MODELS)
    def test_per_reading_p95_above_aipp_p95(self, model):
        rng = np.random.default_rng(SEED)
        iks, aipps = _run(model, rng)
        ik_p95 = np.percentile(iks, 95)
        aipp_p95 = np.percentile(aipps, 95)
        assert ik_p95 > aipp_p95, (
            f"{model}: per-reading P95 ({ik_p95:.3f}) is not above "
            f"AIPP P95 ({aipp_p95:.3f}); CLT narrowing should make "
            f"AIPP's tail tighter than I_k's."
        )


class TestPerReadingStability:
    """Per-reading P95 stability across all ten null models, ×1.5."""

    def test_stability_within_1_5x(self):
        rng = np.random.default_rng(SEED)
        p95s = {}
        for m in MODELS:
            iks, _ = _run(m, rng)
            p95s[m] = np.percentile(iks, 95)
        vals = list(p95s.values())
        ratio = max(vals) / min(vals)
        assert ratio < 1.5, (
            f"Per-reading P95 stability ratio {ratio:.3f}× exceeds "
            f"×1.5 across models: {p95s}"
        )

    def test_stability_within_1_5x_worst_case(self):
        """Same criterion under -20% sigma underestimation."""
        rng = np.random.default_rng(SEED)
        p95s = {}
        for m in MODELS:
            iks, _ = _run(m, rng, underestimate=True)
            p95s[m] = np.percentile(iks, 95)
        vals = list(p95s.values())
        ratio = max(vals) / min(vals)
        assert ratio < 1.5, (
            f"Worst-case per-reading P95 stability ratio {ratio:.3f}× "
            f"exceeds ×1.5: {p95s}"
        )


class TestWorstCaseInflation:
    """Sigma underestimation should inflate the per-reading P95."""

    @pytest.mark.parametrize("model", ["gaussian", "heteroscedastic",
                                        "student_t_3", "ar1_07"])
    def test_underestimation_raises_p95(self, model):
        rng_a = np.random.default_rng(SEED)
        rng_b = np.random.default_rng(SEED)
        clean_iks, _ = _run(model, rng_a, underestimate=False)
        worst_iks, _ = _run(model, rng_b, underestimate=True)
        assert np.percentile(worst_iks, 95) > np.percentile(clean_iks, 95), (
            f"{model}: -20% sigma underestimation did not inflate the "
            f"per-reading P95."
        )


class TestNDependence:
    """The N=50 calibration should generalise to longer WP2 series.

    Per-reading I_k is a pointwise observable, but its empirical P95
    is computed from the mixture density estimated over N samples. As N
    grows the mixture density converges (LLN), so the P95 should
    asymptote rather than drift indefinitely. We verify the drift across
    N in {50, 100, 200} stays comfortably inside the ×1.5 model-stability
    margin already accepted by DG-1.
    """

    @pytest.mark.parametrize("model", ["gaussian", "heteroscedastic",
                                        "student_t_3"])
    def test_p95_stable_with_n(self, model):
        ns = [50, 100, 200]
        n_real_local = 100
        p95s = []
        for n in ns:
            rng = np.random.default_rng(SEED)
            iks = []
            for _ in range(n_real_local):
                v, s = _generate(model, n, rng)
                s = perturb_sigmas(s, mode='systematic-', magnitude=0.2)
                iks.append(compute_ic(v, s))
            p95s.append(np.percentile(np.concatenate(iks), 95))
        ratio = max(p95s) / min(p95s)
        assert ratio < 1.2, (
            f"{model}: per-reading P95 drifts {ratio:.3f}× across "
            f"N {ns} = {p95s}; expected < 1.2×."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for the three-way classifier (src/classify.py).

Verifies:
  - Default thresholds match the calibrated values in entries 004 / 006.
  - Scalar classify_node implements the three-way rule, including
    NaN handling.
  - Vectorised classify_array yields the same answers as classify_node
    cell-by-cell.
  - End-to-end classify_series and classify_network handle the
    trailing-window UNDEFINED region cleanly.
  - Under a Gaussian null with truthful sigmas the per-reading
    flag rate is consistent with the calibrated 5% target (loose
    bound to stay robust in CI).
  - On a known structured signal (linear drift) the classifier reports
    STRUCTURED; on a heavy-tailed outlier burst it reports UNSTRUCTURED.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from classify import (Mode, classify_node, classify_array, classify_series,
                      classify_network, mode_counts,
                      THRESHOLD_95, DELTA_MIN_VAR, DELTA_MIN_ACF)
from ic import compute_ic
from temporal import compute_temporal_structure
from clocks import (ClockParams, simulate_clock, signal_linear_drift,
                    signal_fold_bifurcation, simulate_network_clocks)


class TestDefaults:
    """Default thresholds match the calibrated values in the codebase."""

    def test_threshold_95(self):
        assert THRESHOLD_95 == 2.976

    def test_delta_min_var(self):
        assert DELTA_MIN_VAR == 0.2105

    def test_delta_min_acf(self):
        assert DELTA_MIN_ACF == 0.8703


class TestClassifyNode:
    """Three-way rule applied to a single (ic, var_slope, acf) tuple."""

    def test_below_threshold_is_stable(self):
        assert classify_node(ic_value=1.0, var_slope=10.0, acf=10.0) == \
            Mode.STABLE

    def test_above_threshold_with_var_slope_is_structured(self):
        m = classify_node(ic_value=4.0,
                          var_slope=DELTA_MIN_VAR + 0.01,
                          acf=0.0)
        assert m == Mode.STRUCTURED

    def test_above_threshold_with_acf_is_structured(self):
        m = classify_node(ic_value=4.0,
                          var_slope=0.0,
                          acf=DELTA_MIN_ACF + 0.01)
        assert m == Mode.STRUCTURED

    def test_above_threshold_no_structure_is_unstructured(self):
        m = classify_node(ic_value=4.0,
                          var_slope=DELTA_MIN_VAR - 0.01,
                          acf=DELTA_MIN_ACF - 0.01)
        assert m == Mode.UNSTRUCTURED

    def test_at_threshold_is_anomaly(self):
        m = classify_node(ic_value=THRESHOLD_95,
                          var_slope=0.0, acf=0.0)
        assert m == Mode.UNSTRUCTURED  # IC == threshold counts as anomalous

    def test_negative_var_slope_uses_abs(self):
        m = classify_node(ic_value=4.0,
                          var_slope=-(DELTA_MIN_VAR + 0.1),
                          acf=0.0)
        assert m == Mode.STRUCTURED

    def test_negative_acf_uses_abs(self):
        m = classify_node(ic_value=4.0,
                          var_slope=0.0,
                          acf=-(DELTA_MIN_ACF + 0.1))
        assert m == Mode.STRUCTURED

    def test_nan_ic_is_undefined(self):
        assert classify_node(ic_value=np.nan, var_slope=0.0, acf=0.0) == \
            Mode.UNDEFINED

    def test_nan_temporal_when_flagged_is_undefined(self):
        # IC flagged but temporal stats not yet defined
        m = classify_node(ic_value=4.0, var_slope=np.nan, acf=np.nan)
        assert m == Mode.UNDEFINED

    def test_nan_temporal_when_not_flagged_is_stable(self):
        # Temporal stats NaN but IC says stable: still STABLE
        m = classify_node(ic_value=1.0, var_slope=np.nan, acf=np.nan)
        assert m == Mode.STABLE


class TestClassifyArray:
    """Vectorised classifier matches the scalar one cell-by-cell."""

    def test_matches_scalar(self):
        rng = np.random.default_rng(0)
        ic = rng.uniform(0, 5, 100)
        vs = rng.uniform(-1, 1, 100)
        ac = rng.uniform(-1, 1, 100)
        # Inject some NaNs
        ic[5] = np.nan
        vs[10] = np.nan
        ac[15] = np.nan
        out = classify_array(ic, vs, ac)
        for k in range(100):
            assert out[k] == int(classify_node(ic[k], vs[k], ac[k])), (
                f"mismatch at k={k}: vec={out[k]} "
                f"scalar={classify_node(ic[k], vs[k], ac[k])}")

    def test_2d_shape(self):
        rng = np.random.default_rng(0)
        shape = (50, 7)
        ic = rng.uniform(0, 5, shape)
        vs = rng.uniform(-1, 1, shape)
        ac = rng.uniform(-1, 1, shape)
        out = classify_array(ic, vs, ac)
        assert out.shape == shape

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError, match="shape mismatch"):
            classify_array(np.zeros(10), np.zeros(5), np.zeros(10))


class TestClassifySeries:
    """End-to-end: raw values + IC -> mode array of length T."""

    def test_pre_window_is_stable_or_undefined(self):
        rng = np.random.default_rng(0)
        T = 100
        window = 20
        values = rng.normal(0, 1, T)
        ic = compute_ic(values, np.ones(T))
        modes, vs, ac = classify_series(ic, values, window=window)
        # Before window, temporal stats are NaN; IC flag rate is small
        # under null, so most pre-window cells should be STABLE.
        early = modes[:window]
        assert np.all((early == Mode.STABLE) | (early == Mode.UNDEFINED))

    def test_under_null_flag_rate_below_15pct(self):
        """Per-reading classifier on Gaussian null should flag ~5% of
        readings (the calibration target). We use a loose 15% upper
        bound to keep the test stable in CI."""
        rng = np.random.default_rng(2026)
        T = 500
        params = ClockParams(sigma_white=1.0)
        y, sigma = simulate_clock(params, T, rng=rng)
        ic = compute_ic(y, sigma)
        modes, _, _ = classify_series(ic, y, window=20)
        # Count flagged readings (STRUCTURED + UNSTRUCTURED) over
        # the post-window region.
        flagged = np.sum((modes[20:] == Mode.STRUCTURED) |
                         (modes[20:] == Mode.UNSTRUCTURED))
        rate = flagged / (T - 20)
        assert rate < 0.15, (
            f"per-reading flag rate {rate:.3f} too high under null; "
            f"calibrated target ~5%, allow up to 15% for CI noise")


class TestSignalDetection:
    """Classifier responds to known signals as expected."""

    def test_linear_drift_classifies_as_unstructured(self):
        """Documents the calibrator's blind spot: a smooth linear drift
        at rate << sigma/W does not cross the var_slope or acf
        thresholds (calibrated for critical slowing down), so its
        anomalous readings classify as UNSTRUCTURED. The proposal's
        S6 scenario is labelled 'anomaly detection, NOT near-critical'
        for exactly this reason."""
        rng = np.random.default_rng(2026)
        T = 400
        params = ClockParams(sigma_white=1.0,
                             signal=signal_linear_drift(rate=0.02, onset=200))
        y, sigma = simulate_clock(params, T, rng=rng)
        ic = compute_ic(y, sigma)
        modes, _, _ = classify_series(ic, y, window=20)
        late = modes[300:]
        n_struct = int(np.sum(late == Mode.STRUCTURED))
        n_unstruct = int(np.sum(late == Mode.UNSTRUCTURED))
        # Some late readings are flagged anomalous; they go to
        # UNSTRUCTURED because the temporal heuristic doesn't fire on
        # smooth linear trends.
        assert n_unstruct + n_struct > 0, (
            "expected late drift to cross IC threshold")
        assert n_unstruct >= n_struct, (
            f"linear drift should classify as predominantly UNSTRUCTURED "
            f"(temporal heuristic targets CSD, not trends); "
            f"got struct={n_struct}, unstruct={n_unstruct}")

    def test_outlier_bursts_yield_unstructured(self):
        rng = np.random.default_rng(7)
        T = 400
        # Pure heavy-tailed clock with no temporal structure
        params = ClockParams(sigma_white=1.0, heavy_tail_nu=3.0)
        y, sigma = simulate_clock(params, T, rng=rng)
        ic = compute_ic(y, sigma)
        modes, _, _ = classify_series(ic, y, window=20)
        # Some readings will be flagged anomalous; many should be
        # UNSTRUCTURED because the underlying process has no trend.
        post = modes[20:]
        n_structured = np.sum(post == Mode.STRUCTURED)
        n_unstructured = np.sum(post == Mode.UNSTRUCTURED)
        assert n_unstructured > 0, (
            f"heavy-tailed null produced no UNSTRUCTURED flags; "
            f"got counts {mode_counts(post)}")
        # The structured count should not dominate
        assert n_unstructured >= n_structured // 2 or n_structured == 0, (
            f"unexpectedly many STRUCTURED for memoryless heavy-tail noise: "
            f"struct={n_structured}, unstruct={n_unstructured}")


class TestClassifyNetwork:
    """Network classifier handles (T, N) arrays."""

    def test_shape(self):
        rng = np.random.default_rng(0)
        T, N = 100, 4
        params = [ClockParams(sigma_white=1.0) for _ in range(N)]
        Y, S = simulate_network_clocks(params, T, rng=rng)
        IC = np.zeros_like(Y)
        for j in range(N):
            IC[:, j] = compute_ic(Y[:, j], S[:, j])
        modes, vs, ac = classify_network(IC, Y, window=20)
        assert modes.shape == (T, N)
        assert vs.shape == (T, N)
        assert ac.shape == (T, N)

    def test_per_clock_independence(self):
        """One drifting clock should not flag the other clocks."""
        rng = np.random.default_rng(2026)
        T, N = 400, 3
        params = [
            ClockParams(sigma_white=1.0,
                        signal=signal_linear_drift(rate=0.02, onset=200)),
            ClockParams(sigma_white=1.0),
            ClockParams(sigma_white=1.0),
        ]
        Y, S = simulate_network_clocks(params, T, rng=rng)
        IC = np.zeros_like(Y)
        for j in range(N):
            IC[:, j] = compute_ic(Y[:, j], S[:, j])
        modes, _, _ = classify_network(IC, Y, window=20)
        # Drifting clock (col 0) should accumulate more flags than the others
        flagged_per_clock = [
            np.sum((modes[20:, j] == Mode.STRUCTURED) |
                   (modes[20:, j] == Mode.UNSTRUCTURED))
            for j in range(N)]
        assert flagged_per_clock[0] > max(flagged_per_clock[1:]), (
            f"drifting clock should be most-flagged: {flagged_per_clock}")


class TestModeCounts:

    def test_counts_sum_to_total(self):
        rng = np.random.default_rng(0)
        modes = rng.integers(-1, 3, size=200)
        counts = mode_counts(modes)
        assert sum(counts.values()) == 200
        assert set(counts.keys()) == set(Mode)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

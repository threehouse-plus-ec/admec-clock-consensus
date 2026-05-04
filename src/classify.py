"""
Three-way node classification.

    STABLE:              IC < threshold
    STRUCTURED ANOMALY:  IC ≥ threshold AND (|variance slope| > δ_min_var OR |lag-1 acf| > δ_min_acf)
    UNSTRUCTURED ANOMALY: IC ≥ threshold AND |variance slope| ≤ δ_min_var AND |lag-1 acf| ≤ δ_min_acf

The temporal-structure criteria are heuristic classifiers, not formal structural
inference methods. They are sensitive to noise colour and window length.
The project tests whether this simple heuristic is sufficient to yield
measurable estimator improvement, not whether it is optimal.

Calibrated thresholds:
    threshold_95 = 2.976  bit  (per-reading I_k P95, worst-case -20% σ;
                                heteroscedastic Gaussian binding; Entry 006)
    δ_min_var    = 0.2105     (k=3 × median |var slope| under Student-t(3) null;
                                Entry 004)
    δ_min_acf    = 0.8703     (95th percentile of |acf| under random-walk null;
                                Entry 004)

The earlier AIPP-derived threshold (1.835 bit, Entries 001/002) does not
apply per-reading: it would inflate the false-positive rate by ≈1.6×.
Robustness of δ_min tested under W ∈ {10, 15, 20, 30}.

Status: STUB. Full implementation is WP2.
"""

# TODO (WP2):
# 1. classify_node(ic_value, var_slope, acf, threshold, delta_min_var, delta_min_acf) → mode
# 2. classify_network(ic_array, var_slopes, acfs, ...) → mode_array
# 3. Window-robustness sweep

raise NotImplementedError("WP2 not yet started. This module is a stub.")

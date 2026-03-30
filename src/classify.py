"""
Three-way node classification.

    STABLE:              IC < threshold
    STRUCTURED ANOMALY:  IC ≥ threshold AND (variance trend > 0 OR autocorrelation trend > 0)
    UNSTRUCTURED ANOMALY: IC ≥ threshold AND no temporal trend

The temporal-trend criteria are heuristic classifiers, not formal structural
inference methods. They are sensitive to noise colour and window length.
The project tests whether this simple heuristic is sufficient to yield
measurable estimator improvement, not whether it is optimal.

Robustness tested under W ∈ {10, 15, 20, 30}.

Status: STUB. Implementation is WP2.
"""

# TODO (WP2):
# 1. classify_node(ic_history, variance_history, acf_history, threshold, window) → mode
# 2. Trend detection (linear fit slope > 0 over trailing window)
# 3. Window-robustness sweep

raise NotImplementedError("WP2 not yet started. This module is a stub.")

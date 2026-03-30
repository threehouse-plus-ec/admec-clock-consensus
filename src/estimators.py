"""
Consensus estimators for the clock-network benchmark.

Nine estimators:

    FREQ-global     Stability-weighted global average
    FREQ-local      Same, restricted to delay-accessible neighbours
    FREQ-exclude    Weighted mean excluding high-IC nodes
    HUBER           Huber M-estimator (c ∈ {1.0, 1.345, 2.0}, best per scenario)
    BOCPD           Bayesian online changepoint detection (Adams & MacKay 2007)
                    (λ ∈ {50, 100, 200}, best per scenario)
    IMM             Interacting multiple model filter (Blom & Bar-Shalom 1988)
                    (p_switch ∈ {0.01, 0.05, 0.1}, best per scenario)
    ADMEC-uncon     IC classification, no constraints
    ADMEC-delay     IC classification + delay constraints
    ADMEC-full      IC classification + delay + update-size constraints

Baselines are given per-scenario tuning to prevent strawman comparisons.

Status: STUB. Implementation is WP2.
"""

# TODO (WP2):
# 1. FrequentistEstimator (global, local, exclude variants)
# 2. HuberEstimator with IRLS
# 3. BOCPDEstimator (run-length posterior, hazard rate)
# 4. IMMEstimator (two-mode Kalman bank, Markov switching)
# 5. ADMECEstimator (three variants: unconstrained, delay, full)

raise NotImplementedError("WP2 not yet started. This module is a stub.")

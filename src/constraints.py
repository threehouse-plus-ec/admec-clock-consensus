"""
Update-size constraint projection.

Proposed updates are projected onto the feasible set defined by:

    1. Variance ratio ∈ [0.5, 1.5]  — neither halve nor double ensemble variance
    2. Step size ≤ 3σ per node      — no catastrophic jumps
    3. Total energy ≤ Nσ²           — expected total squared fluctuation under null

Projection is Euclidean (closest point in feasible set).
If the feasible set is empty, the update is rejected and previous state retained.

Thresholds are fixed a priori from the running-noise scale, not tuned post hoc.
Sensitivity tested under ±30% variation in WP3.

Status: STUB. Implementation is WP2/WP3.
"""

# TODO (WP2/WP3):
# 1. project_update(state, proposed_update, sigmas) → filtered_update
# 2. Feasibility check
# 3. Rejection fallback (return zero update)

raise NotImplementedError("WP2 not yet started. This module is a stub.")

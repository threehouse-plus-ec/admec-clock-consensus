"""
Clock model with power-law noise.

Each clock has instantaneous frequency:

    df_i = drift_i · dt + σ_wf · dW_i + σ_ff · dB_i(flicker) + signal_i(t) · dt

Reference parameterisation: active hydrogen maser from Panfilo & Arias (2019, Table 1):
    σ_y(τ = 1 day) ≈ 1.5 × 10⁻¹⁵ (white frequency)
    flicker floor σ_y ≈ 7 × 10⁻¹⁶ at τ ≈ 10 days

Status: STUB. Implementation is WP2.
"""

# TODO (WP2):
# 1. Clock dataclass with noise parameters
# 2. Power-law noise generation (white, flicker via AR(1) with h_α = -1, random-walk)
# 3. Signal injection (sinusoidal, linear drift, step, fold bifurcation)
# 4. Heavy-tailed outlier clock (Student-t, ν = 3)

raise NotImplementedError("WP2 not yet started. This module is a stub.")

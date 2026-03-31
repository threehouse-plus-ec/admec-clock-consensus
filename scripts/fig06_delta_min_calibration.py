"""
Generate fig06: δ_min calibration — null distributions of temporal-structure
statistics across all ten noise models.

Pre-registered multiplier: k = 3.

Saves: logbook/figures/fig06_delta_min_calibration.png
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from temporal import compute_temporal_structure, calibrate_delta_min
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)

MULTIPLIER = 3.0
WINDOW = 20
T = 200
N_REAL = 300
rng = np.random.default_rng(2026)


def generate_null(model, T, rng):
    if model == "Gaussian":
        return rng.normal(0, 1, T)
    elif model == "Heteroscedastic":
        s = np.exp(rng.normal(0, 0.5, T))
        return rng.normal(0, s)
    elif model == "Student-t(3)":
        return rng.standard_t(3, T)
    elif model == "Student-t(5)":
        return rng.standard_t(5, T)
    elif model == "AR(1) ρ=0.7":
        return generate_ar1(T, rho=0.7, rng=rng)
    elif model == "Pareto α=2.5":
        return generate_pareto_symmetric(T, alpha=2.5, rng=rng)
    elif model == "Pareto α=3.0":
        return generate_pareto_symmetric(T, alpha=3.0, rng=rng)
    elif model == "fGn H=0.9":
        return generate_flicker(T, H=0.9, rng=rng)
    elif model == "AR(1) ρ=0.9":
        return generate_ar1(T, rho=0.9, rng=rng)
    elif model == "Random walk":
        return generate_random_walk(T, rng=rng)
    else:
        raise ValueError(model)


models = [
    "Gaussian", "Heteroscedastic", "Student-t(3)", "Student-t(5)",
    "AR(1) ρ=0.7", "Pareto α=2.5", "Pareto α=3.0", "fGn H=0.9",
    "AR(1) ρ=0.9", "Random walk"
]

# Collect per-model statistics
per_model_var = {}
per_model_acf = {}
all_var = []
all_acf = []

for model in models:
    var_slopes = []
    autocorrs = []
    for _ in range(N_REAL):
        series = generate_null(model, T, rng)
        vs, ac = compute_temporal_structure(series, window=WINDOW)
        var_slopes.append(vs[~np.isnan(vs)])
        autocorrs.append(ac[~np.isnan(ac)])
    var_slopes = np.concatenate(var_slopes)
    autocorrs = np.concatenate(autocorrs)
    per_model_var[model] = var_slopes
    per_model_acf[model] = autocorrs
    all_var.append(var_slopes)
    all_acf.append(autocorrs)

all_var = np.concatenate(all_var)
all_acf = np.concatenate(all_acf)

# Per-model medians
print(f"{'Model':<20} {'med|var_slope|':>14} {'med|acf|':>10}")
print("-" * 48)
hardest_var_model = ""
hardest_acf_model = ""
hardest_var = 0
hardest_acf = 0
for model in models:
    mv = np.median(np.abs(per_model_var[model]))
    ma = np.median(np.abs(per_model_acf[model]))
    print(f"{model:<20} {mv:14.6f} {ma:10.6f}")
    if mv > hardest_var:
        hardest_var = mv
        hardest_var_model = model
    if ma > hardest_acf:
        hardest_acf = ma
        hardest_acf_model = model

print(f"\nHardest null (var_slope): {hardest_var_model} (med = {hardest_var:.6f})")
print(f"Hardest null (autocorr): {hardest_acf_model} (med = {hardest_acf:.6f})")

# δ_min: variance slope uses k × median, autocorrelation uses percentile
delta_var = MULTIPLIER * hardest_var

# For autocorrelation: use 95th percentile of |acf| under hardest null
ACF_PERCENTILE = 95.0
hardest_acf_data = per_model_acf[hardest_acf_model]
delta_acf = np.percentile(np.abs(hardest_acf_data), ACF_PERCENTILE)

# Also compute from pooled distribution for comparison
dv_pooled, da_pooled = calibrate_delta_min(all_var, all_acf,
                                            var_multiplier=MULTIPLIER,
                                            acf_percentile=ACF_PERCENTILE)

print(f"\nδ_min (var_slope, k={MULTIPLIER} × median of {hardest_var_model}): {delta_var:.6f}")
print(f"δ_min (autocorr, p{ACF_PERCENTILE} of {hardest_acf_model}):     {delta_acf:.6f}")
print(f"δ_min (var_slope, pooled):        {dv_pooled:.6f}")
print(f"δ_min (autocorr, pooled):         {da_pooled:.6f}")

print(f"\nChosen δ_min values:")
print(f"  δ_min(var_slope) = {delta_var:.4f}  (k={MULTIPLIER} × median, {hardest_var_model})")
print(f"  δ_min(autocorr)  = {delta_acf:.4f}  (p{ACF_PERCENTILE}, {hardest_acf_model})")

# --- Figure ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# Panel (a): Variance slope
ax = axes[0]
data_var = [np.abs(per_model_var[m]) for m in models]
bp = ax.boxplot(data_var, labels=models, patch_artist=True, widths=0.6,
                medianprops=dict(color='darkorange', linewidth=1.5),
                showfliers=False)
colors = ['#5DA5DA'] * 5 + ['#F17CB0'] * 2 + ['#60BD68'] * 2 + ['#FAA43A']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.axhline(delta_var, color='red', linestyle='--', linewidth=1.5,
           label=f'δ_min = {delta_var:.4f}')
ax.set_ylabel('|variance slope|')
ax.set_title(f'(a) Variance slope null distributions (k={MULTIPLIER})')
ax.legend(fontsize=8)
ax.tick_params(axis='x', rotation=35)

# Panel (b): Autocorrelation
ax = axes[1]
data_acf = [np.abs(per_model_acf[m]) for m in models]
bp = ax.boxplot(data_acf, labels=models, patch_artist=True, widths=0.6,
                medianprops=dict(color='darkorange', linewidth=1.5),
                showfliers=False)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.axhline(delta_acf, color='red', linestyle='--', linewidth=1.5,
           label=f'δ_min = {delta_acf:.4f}')
ax.set_ylabel('|lag-1 autocorrelation|')
ax.set_title(f'(b) Autocorrelation null distributions (k={MULTIPLIER})')
ax.legend(fontsize=8)
ax.tick_params(axis='x', rotation=35)

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig06_delta_min_calibration.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {out_path}")
plt.close()

"""
Generate fig05: AIPP threshold stability across all null models (DG-1).

Combines the five original models from Entry 001 with the new power-law,
flicker, and random-walk models. Computes 95th-percentile thresholds
at N=50 (300 realisations) and checks the ×1.5 stability criterion.

Saves: logbook/figures/fig05_powerlaw_thresholds.png
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)

N = 50
N_REAL = 300
rng = np.random.default_rng(2026)


def run_model(name, gen_func):
    """Run AIPP over realisations for a noise model."""
    aipps = []
    for _ in range(N_REAL):
        values, sigmas = gen_func(rng)
        ic = compute_ic(values, sigmas)
        aipps.append(compute_aipp(ic))
    return np.array(aipps)


# --- Define all noise models ---
def gaussian(rng):
    v = rng.normal(0, 1, N)
    return v, np.ones(N)

def heteroscedastic(rng):
    s = np.exp(rng.normal(0, 0.5, N))
    v = rng.normal(0, s)
    return v, s

def student_t3(rng):
    v = rng.standard_t(3, N)
    return v, np.ones(N) * np.sqrt(3)

def student_t5(rng):
    v = rng.standard_t(5, N)
    return v, np.ones(N) * np.sqrt(5 / 3)

def ar1_07(rng):
    v = generate_ar1(N, rho=0.7, rng=rng)
    return v, np.ones(N)

def pareto_25(rng):
    v = generate_pareto_symmetric(N, alpha=2.5, rng=rng)
    s = np.ones(N) * np.std(v)  # use empirical std as declared σ
    return v, s

def pareto_30(rng):
    v = generate_pareto_symmetric(N, alpha=3.0, rng=rng)
    s = np.ones(N) * np.std(v)
    return v, s

def flicker_09(rng):
    v = generate_flicker(N, H=0.9, rng=rng)
    return v, np.ones(N) * max(np.std(v), 1e-6)

def ar1_09(rng):
    v = generate_ar1(N, rho=0.9, rng=rng)
    return v, np.ones(N)

def random_walk(rng):
    v = generate_random_walk(N, rng=rng)
    # Use running std as declared σ (since variance grows)
    s = np.maximum(np.sqrt(np.arange(1, N + 1, dtype=float)), 1.0)
    return v, s


models = [
    # Original five from Entry 001
    ("Gaussian", gaussian),
    ("Heteroscedastic", heteroscedastic),
    ("Student-t(3)", student_t3),
    ("Student-t(5)", student_t5),
    ("AR(1) ρ=0.7", ar1_07),
    # New models
    ("Pareto α=2.5", pareto_25),
    ("Pareto α=3.0", pareto_30),
    ("fGn H=0.9", flicker_09),
    ("AR(1) ρ=0.9", ar1_09),
    ("Random walk", random_walk),
]

results = {}
for name, gen in models:
    results[name] = run_model(name, gen)

# --- Print summary table ---
print(f"{'Model':<20} {'Mean':>8} {'Std':>8} {'P95':>8}")
print("-" * 48)
gaussian_p95 = np.percentile(results["Gaussian"], 95)
for name, aipps in results.items():
    m = np.mean(aipps)
    s = np.std(aipps)
    p95 = np.percentile(aipps, 95)
    print(f"{name:<20} {m:8.4f} {s:8.4f} {p95:8.4f}")

print(f"\nGaussian 95th percentile (reference): {gaussian_p95:.4f}")
print("\nPairwise 95th-percentile ratios (max):")
all_p95 = {name: np.percentile(aipps, 95) for name, aipps in results.items()}
p95_vals = list(all_p95.values())
p95_names = list(all_p95.keys())
max_ratio = 0
max_pair = ("", "")
for i in range(len(p95_vals)):
    for j in range(i + 1, len(p95_vals)):
        ratio = max(p95_vals[i], p95_vals[j]) / min(p95_vals[i], p95_vals[j])
        if ratio > max_ratio:
            max_ratio = ratio
            max_pair = (p95_names[i], p95_names[j])
print(f"  Max ratio: {max_ratio:.3f}× between {max_pair[0]} and {max_pair[1]}")
print(f"  Within ×1.5? {'YES' if max_ratio < 1.5 else 'NO'}")

# --- Figure ---
fig, ax = plt.subplots(figsize=(12, 5.5))

labels = list(results.keys())
data = [results[l] for l in labels]

# Colour: original models blue-ish, new models orange-ish
colors = (['#5DA5DA'] * 5 + ['#F17CB0', '#F17CB0', '#60BD68', '#60BD68', '#FAA43A'])

bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.6,
                medianprops=dict(color='darkorange', linewidth=1.5))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Mark 95th percentiles
p95s = [np.percentile(d, 95) for d in data]
ax.scatter(range(1, len(p95s) + 1), p95s, marker='v', color='darkred',
           s=50, zorder=5, label='95th percentile')

# ×1.5 band around Gaussian reference
ax.axhspan(gaussian_p95 / 1.5, gaussian_p95 * 1.5,
           color='gray', alpha=0.12, label=f'×1.5 band (ref={gaussian_p95:.3f})')
ax.axhline(gaussian_p95, color='gray', linestyle='--', linewidth=0.8)

ax.set_ylabel('AIPP (bits)')
ax.set_title(f'DG-1 threshold stability: all null models (N={N}, {N_REAL} realisations)')
ax.legend(loc='upper left', fontsize=8)

# Annotate max ratio
ax.annotate(f'Max ratio: {max_ratio:.2f}×',
            xy=(0.98, 0.02), xycoords='axes fraction',
            ha='right', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))

plt.xticks(rotation=30, ha='right')
plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig05_powerlaw_thresholds.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {out_path}")
plt.close()

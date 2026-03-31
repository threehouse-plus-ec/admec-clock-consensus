"""
Generate fig04: σ-sensitivity analysis — AIPP distributions under perturbation.

Four conditions at N=200, 300 realisations each:
  1. Unperturbed (baseline)
  2. Random ±20% perturbation
  3. Systematic +20% (overestimate)
  4. Systematic −20% (underestimate)

Saves: logbook/figures/fig04_sigma_sensitivity.png
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, perturb_sigmas

N = 200
N_REAL = 300
MAGNITUDE = 0.2

conditions = [
    ('Unperturbed', None),
    ('Random ±20%', 'random'),
    ('Systematic +20%', 'systematic+'),
    ('Systematic −20%', 'systematic-'),
]

rng = np.random.default_rng(2026)
results = {}

for label, mode in conditions:
    aipps = []
    for _ in range(N_REAL):
        values = rng.normal(0, 1, N)
        sigmas_true = np.ones(N)
        if mode is None:
            sigmas_used = sigmas_true
        else:
            sigmas_used = perturb_sigmas(sigmas_true, mode=mode,
                                         magnitude=MAGNITUDE, rng=rng)
        ic = compute_ic(values, sigmas_used)
        aipps.append(compute_aipp(ic))
    results[label] = np.array(aipps)

# Print summary table
print(f"{'Condition':<22} {'Mean':>8} {'Std':>8} {'P95':>8} {'Shift%':>8}")
print("-" * 58)
baseline_mean = np.mean(results['Unperturbed'])
baseline_p95 = np.percentile(results['Unperturbed'], 95)
for label, aipps in results.items():
    m = np.mean(aipps)
    s = np.std(aipps)
    p95 = np.percentile(aipps, 95)
    shift = abs(m - baseline_mean) / baseline_mean * 100
    print(f"{label:<22} {m:8.4f} {s:8.4f} {p95:8.4f} {shift:7.1f}%")

# Figure
fig, ax = plt.subplots(figsize=(8, 5))

labels = list(results.keys())
data = [results[l] for l in labels]
colors = ['#5DA5DA', '#FAA43A', '#60BD68', '#F15854']

bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.6,
                medianprops=dict(color='darkorange', linewidth=1.5))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Mark means
means = [np.mean(d) for d in data]
ax.scatter(range(1, len(means) + 1), means, marker='^', color='black',
           s=60, zorder=5, label='Mean')

# Mark 95th percentiles
p95s = [np.percentile(d, 95) for d in data]
ax.scatter(range(1, len(p95s) + 1), p95s, marker='v', color='darkred',
           s=50, zorder=5, label='95th percentile')

# 15% band around baseline
ax.axhspan(baseline_mean * 0.85, baseline_mean * 1.15,
           color='gray', alpha=0.15, label='±15% of baseline')
ax.axhline(baseline_mean, color='gray', linestyle='--', linewidth=0.8)

ax.set_ylabel('AIPP (bits)')
ax.set_title(f'σ-sensitivity analysis (N={N}, {N_REAL} realisations, ±{int(MAGNITUDE*100)}% perturbation)')
ax.legend(loc='upper left', fontsize=8)

# Annotate the systematic- shift
sys_neg_mean = np.mean(results['Systematic −20%'])
shift_pct = (sys_neg_mean - baseline_mean) / baseline_mean * 100
ax.annotate(f'+{shift_pct:.1f}%', xy=(4, sys_neg_mean),
            xytext=(4.3, sys_neg_mean + 0.02),
            fontsize=9, color='#F15854', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#F15854', lw=1.2))

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig04_sigma_sensitivity.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {out_path}")
plt.close()

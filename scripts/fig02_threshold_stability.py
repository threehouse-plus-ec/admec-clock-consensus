"""
Generate fig02: AIPP threshold stability across five noise models.

Box plots of AIPP null distributions at N=50, 300 realisations.
95th percentile marked with triangles. Max ratio annotated.

Saves: logbook/figures/fig02_threshold_stability.png
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp
from noise import generate_ar1

N = 50
N_REAL = 300
rng = np.random.default_rng(2026)


def run_model(name):
    aipps = []
    for _ in range(N_REAL):
        if name == "Gaussian":
            values = rng.normal(0, 1, N)
            sigmas = np.ones(N)
        elif name == "Heteroscedastic":
            sigmas = np.exp(rng.normal(0, 0.5, N))
            values = rng.normal(0, sigmas)
        elif name == "Student-t(3)":
            values = rng.standard_t(3, N)
            sigmas = np.ones(N) * np.sqrt(3)
        elif name == "Student-t(5)":
            values = rng.standard_t(5, N)
            sigmas = np.ones(N) * np.sqrt(5 / 3)
        elif name == "AR(1) ρ=0.7":
            values = generate_ar1(N, rho=0.7, rng=rng)
            sigmas = np.ones(N)
        ic = compute_ic(values, sigmas)
        aipps.append(compute_aipp(ic))
    return np.array(aipps)


models = ["Gaussian", "Heteroscedastic", "Student-t(3)", "Student-t(5)", "AR(1) ρ=0.7"]
results = {m: run_model(m) for m in models}

# Compute max ratio
p95s = {m: np.percentile(a, 95) for m, a in results.items()}
p95_vals = list(p95s.values())
max_ratio = 0
for i in range(len(p95_vals)):
    for j in range(i + 1, len(p95_vals)):
        r = max(p95_vals[i], p95_vals[j]) / min(p95_vals[i], p95_vals[j])
        if r > max_ratio:
            max_ratio = r

# Print table
print(f"{'Model':<20} {'Mean':>8} {'P95':>8}")
print("-" * 38)
for m in models:
    print(f"{m:<20} {np.mean(results[m]):8.4f} {p95s[m]:8.4f}")
print(f"\nMax 95th-pctile ratio: {max_ratio:.2f}×")

# --- Figure ---
fig, ax = plt.subplots(figsize=(8, 5))

labels = list(results.keys())
data = [results[m] for m in labels]
colors = ['#5DA5DA', '#FAA43A', '#F17CB0', '#B276B2', '#60BD68']

bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.6,
                medianprops=dict(color='darkorange', linewidth=1.5))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Mark 95th percentiles
p95_list = [p95s[m] for m in labels]
ax.scatter(range(1, len(p95_list) + 1), p95_list, marker='^', color='black',
           s=60, zorder=5, label='95th percentile')

ax.set_ylabel('AIPP (bits)')
ax.set_title(f'AIPP null distributions (N={N}, {N_REAL} realisations)\n'
             f'▲ = 95th percentile')
ax.legend(fontsize=8, loc='upper right')

ax.annotate(f'Max 95th-pctile ratio: {max_ratio:.2f}×',
            xy=(0.98, 0.02), xycoords='axes fraction',
            ha='right', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig02_threshold_stability.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

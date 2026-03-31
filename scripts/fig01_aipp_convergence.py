"""
Generate fig01: AIPP convergence under Gaussian null.

Panel (a): Empirical AIPP vs N, showing convergence to ~1.25 bit
           (not the old 0.55 claim). Error bars from 200 realisations.
Panel (b): Why the mixture is broader than self-contribution.
           True density N(0,1) vs mixture limit N(0,√2), with
           interval [x-1, x+1] shaded under each.

Saves: logbook/figures/fig01_aipp_convergence.png
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.special import erf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, aipp_gaussian_limit

# --- Panel (a): Convergence ---
Ns = [5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
n_real = 200
rng = np.random.default_rng(2026)

means = []
stds = []
for n in Ns:
    aipps = []
    for _ in range(n_real):
        values = rng.normal(0, 1, n)
        sigmas = np.ones(n)
        ic = compute_ic(values, sigmas)
        aipps.append(compute_aipp(ic))
    means.append(np.mean(aipps))
    stds.append(np.std(aipps))

means = np.array(means)
stds = np.array(stds)
limit = aipp_gaussian_limit()
old_claim = -np.log2(erf(1.0 / np.sqrt(2.0)))

# --- Figure ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Panel (a)
ax1.errorbar(Ns, means, yerr=stds, fmt='o-', color='teal', markersize=4,
             capsize=3, linewidth=1, label=f'Empirical ({n_real} realisations)')
ax1.axhline(limit, color='darkorange', linewidth=1.5,
            label=f'Correct limit ≈ {limit:.2f} bit')
ax1.axhline(old_claim, color='gray', linewidth=1, linestyle='--',
            label=f'Old claim (self-contribution) ≈ {old_claim:.2f} bit')
ax1.axhspan(limit * 0.95, limit * 1.05, color='darkorange', alpha=0.15,
            label='±5% band (DG-1)')
ax1.set_xlabel('N (number of points)')
ax1.set_ylabel('AIPP (bits)')
ax1.set_title('(a)  AIPP convergence under Gaussian null')
ax1.legend(fontsize=8, loc='upper right')
ax1.set_ylim(0, 2.0)

# Panel (b): Mixture broadening explanation
y = np.linspace(-4, 4, 500)
true_density = norm.pdf(y, 0, 1)
mixture_limit = norm.pdf(y, 0, np.sqrt(2))

ax2.plot(y, true_density, color='steelblue', linewidth=2, label='True density N(0, 1)')
ax2.plot(y, mixture_limit, color='darkorange', linewidth=2, label='Mixture limit N(0, √2)')

# Shade interval [-1, 1] under mixture
mask_interval = (y >= -1) & (y <= 1)
ax2.fill_between(y[mask_interval], mixture_limit[mask_interval],
                 alpha=0.3, color='darkorange',
                 label=f'p₀ under mixture (≈{norm.cdf(1/np.sqrt(2)) - norm.cdf(-1/np.sqrt(2)):.2f})')
# Shade interval [-1, 1] under true density
ax2.fill_between(y[mask_interval], true_density[mask_interval],
                 alpha=0.2, color='steelblue',
                 label=f'p₀ under self-only (≈{erf(1/np.sqrt(2)):.2f})')

ax2.axvline(-1, color='gray', linewidth=0.5, linestyle=':')
ax2.axvline(1, color='gray', linewidth=0.5, linestyle=':')
ax2.set_xlabel('y')
ax2.set_ylabel('P(y)')
ax2.set_title('(b)  Why the mixture is broader than self-contribution')
ax2.legend(fontsize=8)

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig01_aipp_convergence.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

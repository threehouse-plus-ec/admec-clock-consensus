"""
Generate fig07: Positioning IC against established figures of merit.

Controlled example: 20 clocks, T=200 steps.
  - 19 stable clocks: Gaussian noise, sigma = 1.
  - 1 drifting clock (index 0): Gaussian sigma = 1 + linear drift 0.02/step.

Three-panel figure:
  (a) chi2 for drifting clock vs median of stable clocks
  (b) Huber loss, same layout
  (c) IC, same layout

Allan deviation is structurally different (temporal, not pointwise) and
is discussed in the property table and text, not plotted.

Saves: logbook/figures/fig07_comparison_fom.png
Also saves: data/005_comparison_fom.npz
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from comparison import compute_chi2, compute_huber
from ic import compute_ic

# --- Controlled example ---
N_CLOCKS = 20
T = 200
DRIFT_PER_STEP = 0.02
STABLE_SIGMA = 1.0
HUBER_C = 1.345
SEED = 2026

rng = np.random.default_rng(SEED)

# Generate clock readings
values = np.zeros((T, N_CLOCKS))
sigmas_declared = np.ones((T, N_CLOCKS)) * STABLE_SIGMA

for t in range(T):
    # 19 stable clocks: pure Gaussian noise
    values[t, 1:] = rng.normal(0, STABLE_SIGMA, N_CLOCKS - 1)
    # 1 drifting clock: Gaussian noise + linear drift
    values[t, 0] = rng.normal(0, STABLE_SIGMA) + DRIFT_PER_STEP * t

# Compute per-step figures of merit across all 20 clocks
chi2_per_clock = np.zeros((T, N_CLOCKS))
huber_per_clock = np.zeros((T, N_CLOCKS))
ic_per_clock = np.zeros((T, N_CLOCKS))

for t in range(T):
    chi2_per_clock[t, :] = compute_chi2(values[t, :], sigmas_declared[t, :])
    huber_per_clock[t, :] = compute_huber(values[t, :], sigmas_declared[t, :],
                                           c=HUBER_C)
    ic_per_clock[t, :] = compute_ic(values[t, :], sigmas_declared[t, :])

# Time axis
time = np.arange(T)

# Drifting clock vs median of stable clocks
chi2_drift = chi2_per_clock[:, 0]
chi2_stable_median = np.median(chi2_per_clock[:, 1:], axis=1)

huber_drift = huber_per_clock[:, 0]
huber_stable_median = np.median(huber_per_clock[:, 1:], axis=1)

ic_drift = ic_per_clock[:, 0]
ic_stable_median = np.median(ic_per_clock[:, 1:], axis=1)

# --- Print summary ---
print("Comparison of figures of merit (drifting clock vs stable median)")
print(f"  N_clocks={N_CLOCKS}, T={T}, drift={DRIFT_PER_STEP}/step, seed={SEED}")
print()
print(f"{'Metric':<12} {'Drift mean':>12} {'Stable mean':>12} {'Ratio (last 50)':>16}")
print("-" * 56)
for name, drift, stable in [("chi2", chi2_drift, chi2_stable_median),
                              ("Huber", huber_drift, huber_stable_median),
                              ("IC", ic_drift, ic_stable_median)]:
    d_mean = np.mean(drift[-50:])
    s_mean = np.mean(stable[-50:])
    ratio = d_mean / max(s_mean, 1e-10)
    print(f"{name:<12} {d_mean:12.4f} {s_mean:12.4f} {ratio:15.2f}x")

# --- Save data ---
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)
np.savez_compressed(
    os.path.join(data_dir, '005_comparison_fom.npz'),
    values=values,
    sigmas=sigmas_declared,
    chi2_per_clock=chi2_per_clock,
    huber_per_clock=huber_per_clock,
    ic_per_clock=ic_per_clock,
    seed=SEED,
    n_clocks=N_CLOCKS,
    n_steps=T,
    drift_per_step=DRIFT_PER_STEP,
    stable_sigma=STABLE_SIGMA,
    huber_c=HUBER_C,
)
print(f"\nSaved data: {os.path.join(data_dir, '005_comparison_fom.npz')}")

# --- Figure ---
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), sharey=False)

# Panel (a): chi2
ax = axes[0]
ax.plot(time, chi2_drift, color='#F15854', linewidth=1.2, alpha=0.8,
        label='Drifting clock')
ax.plot(time, chi2_stable_median, color='#5DA5DA', linewidth=1.2, alpha=0.8,
        label='Stable median')
ax.set_xlabel('Time step')
ax.set_ylabel('Per-point chi-squared')
ax.set_title('(a)  Per-point $\\chi^2$')
ax.legend(fontsize=8)

# Panel (b): Huber
ax = axes[1]
ax.plot(time, huber_drift, color='#F15854', linewidth=1.2, alpha=0.8,
        label='Drifting clock')
ax.plot(time, huber_stable_median, color='#5DA5DA', linewidth=1.2, alpha=0.8,
        label='Stable median')
ax.set_xlabel('Time step')
ax.set_ylabel('Per-point Huber loss')
ax.set_title(f'(b)  Huber loss (c = {HUBER_C})')
ax.legend(fontsize=8)

# Panel (c): IC
ax = axes[2]
ax.plot(time, ic_drift, color='#F15854', linewidth=1.2, alpha=0.8,
        label='Drifting clock')
ax.plot(time, ic_stable_median, color='#5DA5DA', linewidth=1.2, alpha=0.8,
        label='Stable median')
ax.set_xlabel('Time step')
ax.set_ylabel('IC (bits)')
ax.set_title('(c)  Information Content')
ax.legend(fontsize=8)

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig07_comparison_fom.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"Saved figure: {out_path}")
plt.close()

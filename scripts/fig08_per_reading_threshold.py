"""
Generate fig08: per-reading I_k threshold calibration for WP2.

The classification rule developed in WP1 uses a 95th-percentile threshold.
That threshold was originally derived from the AIPP distribution (mean
of I_k over N readings). When applied to classify *individual* readings
in WP2, AIPP's central limit theorem narrowing no longer applies, and
the upper tail of I_k is substantially heavier. Using the AIPP P95 to
flag individual readings would yield a much higher false-positive rate
than the nominal 5%.

This script calibrates the per-reading I_k threshold across the same
ten null noise models used in entries 001 and 003, both with truthful
declared sigmas and under worst-case systematic underestimation
(-20%, matching the mitigation adopted in entry 002). The worst-case
P95 across the ten models becomes the operational threshold for WP2.

Saves:
    data/006_per_reading_threshold.npz
    logbook/figures/fig08_per_reading_threshold.png

Prints a summary table of per-reading P95 values, the AIPP P95 for
comparison, the worst-case operational threshold, and the ×1.5
stability check across noise models.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, perturb_sigmas
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)

N = 50
N_REAL = 300
SIGMA_UNDERESTIMATE = 0.2  # -20% systematic, matches entry 002
SEED = 2026


def gen_model(name, n, rng):
    if name == "Gaussian":
        v = rng.normal(0, 1, n)
        return v, np.ones(n)
    if name == "Heteroscedastic":
        s = np.exp(rng.normal(0, 0.5, n))
        return rng.normal(0, s), s
    if name == "Student-t(3)":
        v = rng.standard_t(3, n)
        return v, np.ones(n) * np.sqrt(3)
    if name == "Student-t(5)":
        v = rng.standard_t(5, n)
        return v, np.ones(n) * np.sqrt(5 / 3)
    if name == "AR(1) rho=0.7":
        return generate_ar1(n, rho=0.7, rng=rng), np.ones(n)
    if name == "Pareto alpha=2.5":
        v = generate_pareto_symmetric(n, alpha=2.5, rng=rng)
        return v, np.ones(n) * np.std(v)
    if name == "Pareto alpha=3.0":
        v = generate_pareto_symmetric(n, alpha=3.0, rng=rng)
        return v, np.ones(n) * np.std(v)
    if name == "fGn H=0.9":
        v = generate_flicker(n, H=0.9, rng=rng)
        return v, np.ones(n) * max(np.std(v), 1e-6)
    if name == "AR(1) rho=0.9":
        return generate_ar1(n, rho=0.9, rng=rng), np.ones(n)
    if name == "Random walk":
        v = generate_random_walk(n, rng=rng)
        s = np.maximum(np.sqrt(np.arange(1, n + 1, dtype=float)), 1.0)
        return v, s
    raise ValueError(f"Unknown model: {name!r}")


MODELS = [
    "Gaussian", "Heteroscedastic", "Student-t(3)", "Student-t(5)",
    "AR(1) rho=0.7", "Pareto alpha=2.5", "Pareto alpha=3.0",
    "fGn H=0.9", "AR(1) rho=0.9", "Random walk",
]


def calibrate(underestimate_sigma):
    """Return dict[model -> (ik_pool, aipp_pool)] for a given sigma regime.

    If underestimate_sigma is True, declared sigmas passed to compute_ic
    are scaled by (1 - SIGMA_UNDERESTIMATE) — modelling the worst-case
    operator misestimation identified in entry 002.
    """
    rng = np.random.default_rng(SEED)
    out = {}
    for name in MODELS:
        ik_pool = []
        aipp_pool = []
        for _ in range(N_REAL):
            v, s_true = gen_model(name, N, rng)
            if underestimate_sigma:
                s_used = perturb_sigmas(s_true, mode='systematic-',
                                        magnitude=SIGMA_UNDERESTIMATE)
            else:
                s_used = s_true
            ic = compute_ic(v, s_used)
            ik_pool.append(ic)
            aipp_pool.append(compute_aipp(ic))
        out[name] = (np.concatenate(ik_pool), np.array(aipp_pool))
    return out


print(f"Calibrating per-reading I_k threshold (N={N}, {N_REAL} realisations, "
      f"seed {SEED})...")
clean = calibrate(underestimate_sigma=False)
worst = calibrate(underestimate_sigma=True)

# Extract percentiles
clean_ik_p95 = {m: np.percentile(clean[m][0], 95) for m in MODELS}
clean_ik_p99 = {m: np.percentile(clean[m][0], 99) for m in MODELS}
clean_aipp_p95 = {m: np.percentile(clean[m][1], 95) for m in MODELS}

worst_ik_p95 = {m: np.percentile(worst[m][0], 95) for m in MODELS}
worst_ik_p99 = {m: np.percentile(worst[m][0], 99) for m in MODELS}
worst_aipp_p95 = {m: np.percentile(worst[m][1], 95) for m in MODELS}


def stability_ratio(values):
    vals = list(values)
    return max(vals) / min(vals)


clean_ratio = stability_ratio(clean_ik_p95.values())
worst_ratio = stability_ratio(worst_ik_p95.values())

# Operational threshold: worst-case (largest) P95 across all models under
# -20% sigma underestimation. This is the value WP2 will use to classify
# individual readings, exactly mirroring the entry-002 mitigation pattern
# applied previously to AIPP.
threshold_95_per_reading = max(worst_ik_p95.values())
threshold_99_per_reading = max(worst_ik_p99.values())
threshold_95_aipp_worst = max(worst_aipp_p95.values())

# --- Print summary ---
print()
print(f"{'Model':<22} {'AIPP P95':>10} {'I_k P95':>10} {'I_k P99':>10}")
print(f"{'(clean sigmas)':<22} {'':>10} {'':>10} {'':>10}")
print("-" * 56)
for m in MODELS:
    print(f"{m:<22} {clean_aipp_p95[m]:10.4f} {clean_ik_p95[m]:10.4f} "
          f"{clean_ik_p99[m]:10.4f}")
print(f"\n  I_k P95 stability ratio (clean):    {clean_ratio:.3f}× "
      f"({'PASS' if clean_ratio < 1.5 else 'FAIL'} ×1.5 criterion)")

print()
print(f"{'Model':<22} {'AIPP P95':>10} {'I_k P95':>10} {'I_k P99':>10}")
print(f"{'(sigma -20%)':<22} {'':>10} {'':>10} {'':>10}")
print("-" * 56)
for m in MODELS:
    print(f"{m:<22} {worst_aipp_p95[m]:10.4f} {worst_ik_p95[m]:10.4f} "
          f"{worst_ik_p99[m]:10.4f}")
print(f"\n  I_k P95 stability ratio (worst case): {worst_ratio:.3f}× "
      f"({'PASS' if worst_ratio < 1.5 else 'FAIL'} ×1.5 criterion)")

print()
print(f"  Operational WP2 threshold (per-reading P95, worst case): "
      f"{threshold_95_per_reading:.4f} bit")
print(f"  Per-reading P99 (worst case, for reference):             "
      f"{threshold_99_per_reading:.4f} bit")
print(f"  AIPP P95 (worst case, prior threshold):                  "
      f"{threshold_95_aipp_worst:.4f} bit")
print(f"  Ratio per-reading / AIPP (both worst case):              "
      f"{threshold_95_per_reading / threshold_95_aipp_worst:.2f}×")


# --- Save data ---
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
data_path = os.path.join(data_dir, '006_per_reading_threshold.npz')


def safe_key(name):
    return name.replace(' ', '_').replace('=', '').replace('(', '').replace(')', '')


np.savez_compressed(
    data_path,
    model_names=np.array(MODELS),
    sample_size=N,
    n_realisations=N_REAL,
    sigma_underestimate=SIGMA_UNDERESTIMATE,
    seed=SEED,
    clean_ik_p95=np.array([clean_ik_p95[m] for m in MODELS]),
    clean_ik_p99=np.array([clean_ik_p99[m] for m in MODELS]),
    clean_aipp_p95=np.array([clean_aipp_p95[m] for m in MODELS]),
    worst_ik_p95=np.array([worst_ik_p95[m] for m in MODELS]),
    worst_ik_p99=np.array([worst_ik_p99[m] for m in MODELS]),
    worst_aipp_p95=np.array([worst_aipp_p95[m] for m in MODELS]),
    threshold_95_per_reading=threshold_95_per_reading,
    threshold_99_per_reading=threshold_99_per_reading,
    threshold_95_aipp_worst_case=threshold_95_aipp_worst,
    clean_stability_ratio=clean_ratio,
    worst_stability_ratio=worst_ratio,
    **{f'clean_ik_{safe_key(m)}': clean[m][0] for m in MODELS},
    **{f'worst_ik_{safe_key(m)}': worst[m][0] for m in MODELS},
)
print(f"\nSaved data: {data_path} "
      f"({os.path.getsize(data_path) / 1024:.1f} KB)")


# --- Figure: two-panel comparison ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

for ax, regime, ik_p95, aipp_p95, title in [
    (axes[0], clean, clean_ik_p95, clean_aipp_p95,
     'Truthful sigmas'),
    (axes[1], worst, worst_ik_p95, worst_aipp_p95,
     f'Worst case (sigma underestimated by {int(SIGMA_UNDERESTIMATE*100)}%)'),
]:
    data = [regime[m][0] for m in MODELS]
    bp = ax.boxplot(data, labels=MODELS, patch_artist=True, widths=0.6,
                    showfliers=False,
                    medianprops=dict(color='darkorange', linewidth=1.5))
    colors = (['#5DA5DA'] * 5
              + ['#F17CB0', '#F17CB0', '#60BD68', '#60BD68', '#FAA43A'])
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ik_p95_list = [ik_p95[m] for m in MODELS]
    aipp_p95_list = [aipp_p95[m] for m in MODELS]
    ax.scatter(range(1, len(MODELS) + 1), ik_p95_list,
               marker='v', color='darkred', s=55, zorder=5,
               label='I_k 95th percentile')
    ax.scatter(range(1, len(MODELS) + 1), aipp_p95_list,
               marker='^', color='black', s=55, zorder=5,
               label='AIPP 95th percentile')

    ratio = stability_ratio(ik_p95_list)
    ax.set_title(f'{title}\nI_k P95 stability ratio: {ratio:.2f}×')
    ax.set_xticklabels(MODELS, rotation=30, ha='right')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(axis='y', alpha=0.3)

axes[0].set_ylabel('Information content (bits)')

# Operational threshold line on the right (worst-case) panel
axes[1].axhline(threshold_95_per_reading, color='darkred', linestyle='--',
                linewidth=1.0, alpha=0.7,
                label=f'WP2 threshold = {threshold_95_per_reading:.3f} bit')
axes[1].legend(loc='upper left', fontsize=8)

plt.tight_layout()

fig_path = os.path.join(os.path.dirname(__file__), '..', 'logbook',
                        'figures', 'fig08_per_reading_threshold.png')
fig.savefig(fig_path, dpi=150, bbox_inches='tight')
print(f"Saved figure: {fig_path}")
plt.close()

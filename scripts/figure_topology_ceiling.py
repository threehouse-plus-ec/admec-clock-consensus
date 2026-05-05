"""Manuscript figure: topological ceiling on local consensus.

Plots the empirical admec_full / centralised MSE ratio against the
effective neighbourhood fraction k_eff / N for each (scenario, seed)
in the canonical archives, with the theoretical ceiling 1 / (k_eff / N)
overlaid.

Effective neighbourhood:
    k_eff(i) = #{j : adj[i, j] AND delays[i, j] <= freshness} + 1
(The +1 counts self.) k_eff is averaged across nodes (and seeds for
the per-scenario marker). For 'drop' mode, freshness = 1 (the WP2
default). For 'stale' mode, freshness = infinity (every adjacency
neighbour contributes), so k_eff equals adjacency degree + 1.

Baseline reference: freq_exclude at threshold 2.5 -- the matched
across-scenario optimum (entry 011). Per-scenario values:
    S1 freq_exclude(thr 2.5) = 0.122
    S2 freq_exclude(thr 2.5) = 0.122
    S3 freq_exclude(thr 2.5) = 0.027

Saves docs/manuscript_files/fig_topology_ceiling.png.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks, signal_sinusoidal)
from network import make_network


SEEDS = list(range(2026, 2036))


def _factory(amplitude, period, onset=0.0):
    def f(i):
        phase = i * np.pi / 3.0
        return signal_sinusoidal(amplitude=amplitude, period=period,
                                 phase=phase, onset=onset)
    return f


SCENARIOS = [
    dict(name='S1', n=15, topology='ring', delay_mean=2.0,
         T=200, n_signal=3, factory=_factory(5.0, 50.0)),
    dict(name='S2', n=15, topology='fully_connected', delay_mean=0.3,
         T=200, n_signal=3, factory=_factory(5.0, 50.0)),
    dict(name='S3', n=50, topology='random_sparse', delay_mean=4.0,
         T=200, n_signal=3, factory=_factory(5.0, 50.0)),
]

# Best non-ADMEC baseline at threshold 2.5 (entry 011 cross-scenario optimum)
BASELINE_MSE = {'S1': 0.122, 'S2': 0.122, 'S3': 0.027}


def _compute_k_eff(scn, freshness=1):
    """Mean k_eff = (delay-accessible neighbour count + 1) over (seed, node)."""
    k_eff_per_seed = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        params = build_scenario_clocks(
            n=scn['n'], n_signal=scn['n_signal'],
            signal_factory=scn['factory'],
            n_degraded=1, degradation_factor=3.0,
            base=ClockParams(sigma_white=1.0))
        # Match RNG order: simulate first, then network
        _ = simulate_network_clocks(params, scn['T'], dt=1.0, rng=rng)
        adj, delays = make_network(scn['n'], scn['topology'],
                                    scn['delay_mean'], rng=rng)
        if freshness is None:
            # 'stale' mode: every adjacency neighbour counts
            mask = adj
        else:
            mask = adj & (delays <= freshness)
        k_eff_i = mask.sum(axis=1) + 1  # +1 for self
        k_eff_per_seed.append(float(np.mean(k_eff_i)))
    return float(np.mean(k_eff_per_seed))


def _per_seed_mse(npz_path, key):
    """Return shape-(n_scn, n_seed) mean MSE array from an archive key."""
    d = np.load(npz_path, allow_pickle=True)
    return d[key]


def _admec_full_mse_drop_baseline():
    """WP2 baseline: admec_full at drop, threshold 2.976. Per-seed S1/S2/S3."""
    base = '/Users/uwarring/Documents/GitHub/admec-clock-consensus/data'
    d = np.load(f'{base}/wp2_campaign_20260504_fix.npz', allow_pickle=True)
    ests = list(d['estimators'])
    j = ests.index('admec_full')
    scns = list(d['scenarios'])
    out = {}
    for s in ('S1', 'S2', 'S3'):
        out[s] = d['mse'][scns.index(s), :, j]
    return out


def _admec_full_mse_combined():
    """WP3 combined tuning: stale + thr 1.5 + var_loose. Per-seed S1/S2/S3."""
    base = '/Users/uwarring/Documents/GitHub/admec-clock-consensus/data'
    d = np.load(f'{base}/wp3_combined_tuning_20260505.npz', allow_pickle=True)
    cfgs = list(d['configs'])
    j = cfgs.index('admec_full_combined')
    scns = list(d['scenarios'])
    out = {}
    for s in ('S1', 'S2', 'S3'):
        out[s] = d['mse'][scns.index(s), :, j]
    return out


def main():
    # Compute k_eff for both modes per scenario
    k_eff_drop = {scn['name']: _compute_k_eff(scn, freshness=1)
                  for scn in SCENARIOS}
    k_eff_stale = {scn['name']: _compute_k_eff(scn, freshness=None)
                   for scn in SCENARIOS}
    N = {scn['name']: scn['n'] for scn in SCENARIOS}

    print('Effective neighbourhood (k_eff):')
    for s in ('S1', 'S2', 'S3'):
        print(f'  {s}: N={N[s]:>2d}  k_eff_drop={k_eff_drop[s]:.2f}  '
              f'k_eff_stale={k_eff_stale[s]:.2f}  '
              f'k_eff_drop/N={k_eff_drop[s] / N[s]:.3f}  '
              f'k_eff_stale/N={k_eff_stale[s] / N[s]:.3f}')

    af_baseline = _admec_full_mse_drop_baseline()
    af_combined = _admec_full_mse_combined()

    # Ratio of admec_full MSE / best non-ADMEC MSE per (scenario, seed)
    ratio_baseline = {s: af_baseline[s] / BASELINE_MSE[s] for s in af_baseline}
    ratio_combined = {s: af_combined[s] / BASELINE_MSE[s] for s in af_combined}

    fig, ax = plt.subplots(figsize=(7.5, 5.0))

    # Theoretical ceiling: ratio = 1/(k_eff/N) = N/k_eff (independent-readings limit)
    x_ref = np.geomspace(0.01, 1.0, 200)
    ax.plot(x_ref, 1.0 / x_ref, 'k--', lw=1, alpha=0.6,
            label=r'theoretical ceiling $N/k_\mathrm{eff}$')
    ax.axhline(1.0, color='gray', lw=0.7, alpha=0.5)
    ax.text(0.012, 1.05, 'admec_full = best non-ADMEC',
            fontsize=8, color='gray', ha='left', va='bottom')

    colors = {'S1': '#2E86AB', 'S2': '#A23B72', 'S3': '#F18F01'}
    markers_drop = {'S1': 'o', 'S2': 's', 'S3': '^'}

    for s in ('S1', 'S2', 'S3'):
        x_drop = np.full_like(ratio_baseline[s], k_eff_drop[s] / N[s])
        x_stale = np.full_like(ratio_combined[s], k_eff_stale[s] / N[s])
        ax.scatter(x_drop, ratio_baseline[s],
                   marker=markers_drop[s], color=colors[s],
                   alpha=0.4, s=40, edgecolors='none',
                   label=f'{s} WP2 baseline (drop, thr 2.976)')
        ax.scatter(x_stale, ratio_combined[s],
                   marker=markers_drop[s], color=colors[s],
                   alpha=0.95, s=70, edgecolors='black', linewidths=0.7,
                   label=f'{s} WP3 combined (stale, thr 1.5, var_loose)')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'Effective neighbourhood fraction $k_\mathrm{eff}/N$')
    ax.set_ylabel(r'admec_full MSE / centralised MSE')
    ax.set_title('Topological ceiling on local consensus\n'
                 'across the WP2 / WP3 ablation set')
    ax.legend(fontsize=7.5, loc='upper right', framealpha=0.92)
    ax.grid(which='both', alpha=0.25)
    ax.set_xlim(0.01, 1.0)
    ax.set_ylim(0.4, 60)

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'docs',
                           'manuscript_files')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig_topology_ceiling.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'\nSaved: {out_path}')


if __name__ == '__main__':
    main()

"""Threshold-sweep null FPR check (Atlas-integrity reader request).

The threshold-sweep ablation in entry 011 reports admec_full and
freq_exclude MSE across thresholds {1.5, 2.0, 2.5, 2.976, 3.5, 4.5,
6.0} on signal scenarios S1/S2/S3. The reader asked: in real
timekeeping, an empirical FPR > 5 % is operationally catastrophic;
report the FPR at each threshold so "wins" at threshold 1.5 can be
contextualised against operational practice.

This script runs the per-reading IC classification on the two
pre-registered null scenarios S4 (15-node ring, Poisson(2.0), no
signal) and S5 (50-node random-sparse, Poisson(4.0), no signal) at
each of the seven thresholds. Under a null-only setup every flagged
cell is, by construction, a false positive. The empirical FPR is
the fraction of (T, N) cells with `IC_k >= threshold`.

RNG order matched to scripts/wp2_campaign.py.
"""

import os
import sys
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks)
from network import make_network
from ic import compute_ic


SEEDS = list(range(2026, 2036))
THRESHOLDS = [1.5, 2.0, 2.5, 2.976, 3.5, 4.5, 6.0]

SCENARIOS = [
    dict(name='S4', n=15, topology='ring', delay_mean=2.0, T=200),
    dict(name='S5', n=50, topology='random_sparse', delay_mean=4.0, T=200),
]


def run():
    n_scn, n_seed, n_thr = len(SCENARIOS), len(SEEDS), len(THRESHOLDS)
    flagged_frac = np.zeros((n_scn, n_seed, n_thr))

    for si, scn in enumerate(SCENARIOS):
        for ki, seed in enumerate(SEEDS):
            rng = np.random.default_rng(seed)
            params = build_scenario_clocks(
                n=scn['n'], n_signal=0,
                signal_factory=None,
                n_degraded=1, degradation_factor=3.0,
                base=ClockParams(sigma_white=1.0))
            Y, Sigmas = simulate_network_clocks(
                params, scn['T'], dt=1.0, rng=rng)
            _adj, _delays = make_network(scn['n'], scn['topology'],
                                          scn['delay_mean'], rng=rng)

            T, N = Y.shape
            IC = np.zeros_like(Y)
            for t in range(T):
                IC[t, :] = compute_ic(Y[t, :], Sigmas[t, :])

            for ti, thr in enumerate(THRESHOLDS):
                flagged_frac[si, ki, ti] = float(
                    np.mean(IC >= thr))

        print(f'  done: {scn["name"]} all seeds')

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(
        out_dir, f'wp3_threshold_null_fpr_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        thresholds=np.array(THRESHOLDS),
        flagged_fraction=flagged_frac,
    )
    print(f'\nSaved: {out_path}')

    print('\nMean per-reading FPR under null (10 seeds), per (scenario, threshold):')
    print(f'{"":>4s}  ' + ''.join(f'{t:>10.3f}' for t in THRESHOLDS))
    for si, scn in enumerate(SCENARIOS):
        cells = ''.join(f'{np.mean(flagged_frac[si, :, ti]):>10.4f}'
                         for ti in range(n_thr))
        print(f'{scn["name"]:>4s}  {cells}')

    print('\nIn the operational-practice frame (NIST AT1 etc.), FPR > 0.5 % is')
    print('typically considered borderline and FPR > 1 % is unacceptable for')
    print('routine deployment. The values above contextualise the threshold-')
    print('sweep "wins" at threshold 1.5 in section 4.4 of the manuscript.')


if __name__ == '__main__':
    run()

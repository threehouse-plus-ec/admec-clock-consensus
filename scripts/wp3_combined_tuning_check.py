"""WP3 combined-tuning sanity check.

Runs admec_full with all WP3 design recommendations applied
*simultaneously*:

    delay_mode = 'stale'                 (entry 008, ablation 1)
    threshold  = 1.5                     (entry 011, ablation 2)
    constraint = var_loose [0.35, 1.65]  (entry 009, ablation 3)
    classifier = three-way (default)     (entry 010, ablation 4)
    lag        = 0  (default)            (entry 012, ablation 5)

The manuscript's "combined tuning" §4.6 numbers were initially read
off the individual ablations, which assumed (without proof) that the
three best-found design choices interact additively. This script
runs the actual combined harness so the manuscript can quote a
measured number rather than a composed one.

Comparators included so the matched-threshold and best-of-best
comparisons in §4.6 can be made consistently:

  * freq_exclude at thr = 1.5  (matched-threshold comparison)
  * freq_exclude at thr = 2.5  (freq_exclude's own optimum on S1/S2)
  * freq_exclude at thr = 2.976 (WP1 calibration baseline)
  * imm at default config       (best non-ADMEC baseline on S3 / S6 / S8)

RNG order matched to scripts/wp2_campaign.py.
"""

import os
import sys
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks, signal_sinusoidal)
from network import make_network
from constraints import ConstraintParams
from estimators import admec_full, freq_exclude, imm
from metrics import mse, collapse_index, structure_correlation


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

# (config_label, runner)
def _run_admec_full_combined(Y, Sigmas, adj, delays):
    return admec_full(
        Y, Sigmas, adj, delays,
        delay_mode='stale',
        threshold=1.5,
        constraint_params=ConstraintParams(
            max_step_factor=3.0, energy_factor=1.0,
            var_ratio_min=0.35, var_ratio_max=1.65))


def _run_admec_full_baseline(Y, Sigmas, adj, delays):
    """WP2 baseline: drop, thr 2.976, default constraints. Sanity check."""
    return admec_full(Y, Sigmas, adj, delays, delay_mode='drop',
                      threshold=2.976)


CONFIGS = [
    ('admec_full_combined', _run_admec_full_combined),
    ('admec_full_baseline', _run_admec_full_baseline),
    ('freq_exclude_thr_1.5', lambda Y, S, a, d:
        freq_exclude(Y, S, threshold=1.5)),
    ('freq_exclude_thr_2.5', lambda Y, S, a, d:
        freq_exclude(Y, S, threshold=2.5)),
    ('freq_exclude_thr_2.976', lambda Y, S, a, d:
        freq_exclude(Y, S, threshold=2.976)),
    ('imm_default', lambda Y, S, a, d:
        imm(Y, S, adj=a, delays=d)),
]


def _ground_truth_signals(params, T, dt=1.0):
    t = np.arange(T, dtype=float) * dt
    N = len(params)
    signals = np.zeros((T, N))
    for i, p in enumerate(params):
        if p.signal is not None:
            signals[:, i] = p.signal(t)
    signal_clocks = np.array([i for i, p in enumerate(params)
                              if p.signal is not None])
    return signals, signal_clocks


def run():
    n_scn, n_seed, n_cfg = len(SCENARIOS), len(SEEDS), len(CONFIGS)
    arr_mse = np.zeros((n_scn, n_seed, n_cfg))
    arr_ci = np.zeros_like(arr_mse)
    arr_sc = np.zeros_like(arr_mse)

    for si, scn in enumerate(SCENARIOS):
        for ki, seed in enumerate(SEEDS):
            rng = np.random.default_rng(seed)
            params = build_scenario_clocks(
                n=scn['n'], n_signal=scn['n_signal'],
                signal_factory=scn['factory'],
                n_degraded=1, degradation_factor=3.0,
                base=ClockParams(sigma_white=1.0))
            # WP2-matching RNG order
            Y, Sigmas = simulate_network_clocks(params, scn['T'],
                                                 dt=1.0, rng=rng)
            adj, delays = make_network(scn['n'], scn['topology'],
                                        scn['delay_mean'], rng=rng)
            signals, signal_clocks = _ground_truth_signals(params, scn['T'])

            for ci, (label, runner) in enumerate(CONFIGS):
                E = runner(Y, Sigmas, adj, delays)
                arr_mse[si, ki, ci] = mse(E)
                arr_ci[si, ki, ci] = collapse_index(E, Sigmas)
                arr_sc[si, ki, ci] = structure_correlation(
                    Y, E, signals, signal_clocks)
            print(f'  done: {scn["name"]} seed {seed}', flush=True)

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(
        out_dir, f'wp3_combined_tuning_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        configs=np.array([c[0] for c in CONFIGS]),
        mse=arr_mse, collapse_index=arr_ci, structure_corr=arr_sc,
    )
    print(f'\nSaved: {out_path}', flush=True)

    print(f'\n{"":>4s}  ' + '  '.join(f'{c[0][:18]:>18s}' for c in CONFIGS))
    for si, scn in enumerate(SCENARIOS):
        cells = '  '.join(f'{np.mean(arr_mse[si, :, ci]):>18.4f}'
                          for ci in range(n_cfg))
        print(f'{scn["name"]:>4s}  {cells}')

    print('\nstructure correlation:')
    print(f'{"":>4s}  ' + '  '.join(f'{c[0][:18]:>18s}' for c in CONFIGS))
    for si, scn in enumerate(SCENARIOS):
        cells = '  '.join(f'{np.nanmean(arr_sc[si, :, ci]):>18.4f}'
                          for ci in range(n_cfg))
        print(f'{scn["name"]:>4s}  {cells}')


if __name__ == '__main__':
    run()

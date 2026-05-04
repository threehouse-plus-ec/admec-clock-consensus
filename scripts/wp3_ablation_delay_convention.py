"""WP3 ablation 1 -- delay convention (drop vs stale).

Mirrors the WP2 campaign for the three local estimators
(freq_local, admec_delay, admec_full) on the three signal scenarios
where the WP2 result was structural (S1 ring delay 2.0, S2 fully
connected delay 0.3, S3 random_sparse delay 4.0). Each (scenario,
seed, estimator) triple is run twice -- once with the WP2 baseline
delay_mode='drop' and once with delay_mode='stale' -- and the three
IC-independent metrics are recorded for both.

Question: does using stale readings (Y[t - delays[i, j], j]) instead
of dropping inaccessible neighbours close the WP2 gap to centralised
exclusion baselines?

Centralised baselines (freq_exclude, imm) are also run and recorded
for direct comparison; they ignore delay_mode by construction.

Output: data/wp3_ablation_delay_convention_YYYYMMDD.npz with arrays
keyed by (scenario, seed, estimator, mode) where mode in {'drop',
'stale', 'baseline'}.
"""

import os
import sys
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks, signal_sinusoidal)
from network import make_network
from estimators import (freq_local, freq_exclude, imm,
                        admec_delay, admec_full)
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

LOCAL_ESTIMATORS = {
    'freq_local': freq_local,
    'admec_delay': admec_delay,
    'admec_full': admec_full,
}

DELAY_MODES = ['drop', 'stale']

BASELINES = {
    'freq_exclude': freq_exclude,
    'imm': imm,
}


def _ground_truth_signals(params, T, dt=1.0):
    """Per-clock injected signal column (T, N), used for structure_correlation."""
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
    n_local = len(LOCAL_ESTIMATORS)
    n_modes = len(DELAY_MODES)
    n_base = len(BASELINES)
    n_scn = len(SCENARIOS)
    n_seed = len(SEEDS)

    # Local estimators: (scenario, seed, estimator, mode)
    local_mse = np.zeros((n_scn, n_seed, n_local, n_modes))
    local_ci = np.zeros_like(local_mse)
    local_sc = np.zeros_like(local_mse)
    # Baselines: (scenario, seed, estimator)
    base_mse = np.zeros((n_scn, n_seed, n_base))
    base_ci = np.zeros_like(base_mse)
    base_sc = np.zeros_like(base_mse)

    for si, scn in enumerate(SCENARIOS):
        for ki, seed in enumerate(SEEDS):
            rng = np.random.default_rng(seed)
            params = build_scenario_clocks(
                n=scn['n'], n_signal=scn['n_signal'],
                signal_factory=scn['factory'],
                n_degraded=1, degradation_factor=3.0,
                base=ClockParams(sigma_white=1.0))
            # Match scripts/wp2_campaign.py RNG order so drop-mode
            # numbers reproduce the WP2 canonical archive exactly.
            Y, Sigmas = simulate_network_clocks(params, scn['T'],
                                                 dt=1.0, rng=rng)
            adj, delays = make_network(scn['n'], scn['topology'],
                                        scn['delay_mean'], rng=rng)
            signals, signal_clocks = _ground_truth_signals(params,
                                                            scn['T'])

            for ei, (name, fn) in enumerate(LOCAL_ESTIMATORS.items()):
                for mi, mode in enumerate(DELAY_MODES):
                    E = fn(Y, Sigmas, adj, delays, delay_mode=mode)
                    local_mse[si, ki, ei, mi] = mse(E)
                    local_ci[si, ki, ei, mi] = collapse_index(E, Sigmas)
                    local_sc[si, ki, ei, mi] = structure_correlation(
                        Y, E, signals, signal_clocks)

            for bi, (name, fn) in enumerate(BASELINES.items()):
                E = fn(Y, Sigmas, adj=adj, delays=delays)
                base_mse[si, ki, bi] = mse(E)
                base_ci[si, ki, bi] = collapse_index(E, Sigmas)
                base_sc[si, ki, bi] = structure_correlation(
                    Y, E, signals, signal_clocks)

            print(f'  done: {scn["name"]} seed {seed}')

    # Save
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(out_dir,
                            f'wp3_ablation_delay_convention_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        local_estimators=np.array(list(LOCAL_ESTIMATORS.keys())),
        delay_modes=np.array(DELAY_MODES),
        baselines=np.array(list(BASELINES.keys())),
        local_mse=local_mse, local_collapse_index=local_ci,
        local_structure_corr=local_sc,
        baseline_mse=base_mse, baseline_collapse_index=base_ci,
        baseline_structure_corr=base_sc,
    )
    print(f'\nSaved: {out_path}')

    # Print summary -- mean over seeds, per scenario / estimator / mode
    print('\nMean MSE over 10 seeds:')
    print(f'{"":>4s} ' + ' '.join(f'{e[:12]:>14s}' for e in
                                    list(LOCAL_ESTIMATORS) + list(BASELINES)))
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(DELAY_MODES):
            cells = [f'{np.mean(local_mse[si, :, ei, mi]):>14.4f}'
                     for ei in range(n_local)]
            if mode == 'drop':
                cells += [f'{np.mean(base_mse[si, :, bi]):>14.4f}'
                          for bi in range(n_base)]
            else:
                cells += [' ' * 14] * n_base
            print(f'{scn["name"]:>4s} {mode:>5s} ' + ' '.join(cells))

    print('\nMean structure correlation over 10 seeds:')
    print(f'{"":>4s} ' + ' '.join(f'{e[:12]:>14s}' for e in
                                    list(LOCAL_ESTIMATORS) + list(BASELINES)))
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(DELAY_MODES):
            cells = [f'{np.nanmean(local_sc[si, :, ei, mi]):>14.4f}'
                     for ei in range(n_local)]
            if mode == 'drop':
                cells += [f'{np.nanmean(base_sc[si, :, bi]):>14.4f}'
                          for bi in range(n_base)]
            else:
                cells += [' ' * 14] * n_base
            print(f'{scn["name"]:>4s} {mode:>5s} ' + ' '.join(cells))


if __name__ == '__main__':
    run()

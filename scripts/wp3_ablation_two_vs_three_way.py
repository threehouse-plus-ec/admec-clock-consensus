"""WP3 ablation 4 -- two-way vs three-way classification (DG-3 sub-criterion).

Tests whether the STRUCTURED / UNSTRUCTURED split adds anything over a
plain ANOMALOUS class. Three-way (default) splits flagged readings on
the temporal-statistic gate; two-way collapses both classes into a
single excluded-from-consensus category.

Hypothesis (entry 010): the two modes produce identical consensus-level
estimates because both STRUCTURED and UNSTRUCTURED are excluded equally
from the STABLE-only weighted mean. The split affects bookkeeping
(STRUCTURED count is recorded separately) but not the consensus.

Harness: 3 scenarios x 10 seeds x 2 delay modes x 2 classifier variants
on the three ADMEC estimators plus mode-count diagnostics. RNG order
matched to scripts/wp2_campaign.py for byte-exact reproducibility of
the WP2 baseline.
"""

import os
import sys
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks, signal_sinusoidal)
from network import make_network
from estimators import (admec_unconstrained, admec_delay, admec_full,
                        _classify_network_full)
from classify import Mode
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

ESTIMATORS = {
    'admec_unconstrained': admec_unconstrained,
    'admec_delay': admec_delay,
    'admec_full': admec_full,
}
MODES = ['drop', 'stale']
CLASSIFIER = ['three_way', 'two_way']


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
    n_scn, n_seed = len(SCENARIOS), len(SEEDS)
    n_est, n_mode, n_cls = len(ESTIMATORS), len(MODES), len(CLASSIFIER)

    # Estimator metrics: (scenario, seed, estimator, mode, classifier)
    arr_mse = np.zeros((n_scn, n_seed, n_est, n_mode, n_cls))
    arr_ci = np.zeros_like(arr_mse)
    arr_sc = np.zeros_like(arr_mse)

    # Mode counts per (scenario, seed, classifier): UNDEFINED, STABLE,
    # STRUCTURED, UNSTRUCTURED. In two-way the STRUCTURED count is 0
    # because the temporal split is bypassed.
    counts = np.zeros((n_scn, n_seed, n_cls, 4), dtype=np.int64)

    for si, scn in enumerate(SCENARIOS):
        for ki, seed in enumerate(SEEDS):
            rng = np.random.default_rng(seed)
            params = build_scenario_clocks(
                n=scn['n'], n_signal=scn['n_signal'],
                signal_factory=scn['factory'],
                n_degraded=1, degradation_factor=3.0,
                base=ClockParams(sigma_white=1.0))
            Y, Sigmas = simulate_network_clocks(params, scn['T'],
                                                 dt=1.0, rng=rng)
            adj, delays = make_network(scn['n'], scn['topology'],
                                        scn['delay_mean'], rng=rng)
            signals, signal_clocks = _ground_truth_signals(params, scn['T'])

            for ci, classifier in enumerate(CLASSIFIER):
                two_way = (classifier == 'two_way')
                # Bookkeeping: classifier mode counts
                modes_grid = _classify_network_full(
                    Y, Sigmas, window=20,
                    threshold=2.976,
                    delta_min_var=0.2105,
                    delta_min_acf=0.8703,
                    two_way=two_way)
                for mi_mode, m in enumerate(
                        [Mode.UNDEFINED, Mode.STABLE,
                         Mode.STRUCTURED, Mode.UNSTRUCTURED]):
                    counts[si, ki, ci, mi_mode] = int(
                        np.sum(modes_grid == int(m)))

                for ei, (name, fn) in enumerate(ESTIMATORS.items()):
                    for mi, mode in enumerate(MODES):
                        if name == 'admec_unconstrained':
                            E = fn(Y, Sigmas, two_way=two_way)
                        else:
                            E = fn(Y, Sigmas, adj, delays,
                                    delay_mode=mode,
                                    two_way=two_way)
                        arr_mse[si, ki, ei, mi, ci] = mse(E)
                        arr_ci[si, ki, ei, mi, ci] = collapse_index(
                            E, Sigmas)
                        arr_sc[si, ki, ei, mi, ci] = structure_correlation(
                            Y, E, signals, signal_clocks)

            print(f'  done: {scn["name"]} seed {seed}')

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(
        out_dir, f'wp3_ablation_two_vs_three_way_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        estimators=np.array(list(ESTIMATORS.keys())),
        delay_modes=np.array(MODES),
        classifiers=np.array(CLASSIFIER),
        mode_labels=np.array(['UNDEFINED', 'STABLE',
                               'STRUCTURED', 'UNSTRUCTURED']),
        mse=arr_mse, collapse_index=arr_ci, structure_corr=arr_sc,
        mode_counts=counts,
    )
    print(f'\nSaved: {out_path}')

    # Summary
    print('\nMSE: max abs(two_way - three_way) over all '
          '(scenario, seed, estimator, mode):')
    delta_mse = arr_mse[..., 1] - arr_mse[..., 0]
    print(f'  max abs delta = {float(np.max(np.abs(delta_mse))):.4e}')
    print(f'  any non-zero  = {bool(np.any(delta_mse != 0.0))}')
    print('\nStructure correlation: max abs delta:')
    delta_sc = arr_sc[..., 1] - arr_sc[..., 0]
    print(f'  max abs delta = '
          f'{float(np.nanmax(np.abs(delta_sc))):.4e}')

    print('\nClassification mode counts (mean over 10 seeds), '
          'three-way vs two-way:')
    print(f'{"":>4s}  {"classifier":>10s}  {"UND":>6s}  {"STA":>6s}  '
          f'{"STR":>6s}  {"UNS":>6s}')
    for si, scn in enumerate(SCENARIOS):
        for ci, cls in enumerate(CLASSIFIER):
            row = counts[si, :, ci, :].mean(axis=0)
            print(f'{scn["name"]:>4s}  {cls:>10s}  '
                  f'{row[0]:>6.0f}  {row[1]:>6.0f}  '
                  f'{row[2]:>6.0f}  {row[3]:>6.0f}')

    # Cross-mode summary table for the entry
    print('\nadmec_full MSE (three-way == two-way?):')
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(MODES):
            af_three = float(np.mean(arr_mse[si, :, 2, mi, 0]))
            af_two = float(np.mean(arr_mse[si, :, 2, mi, 1]))
            print(f'  {scn["name"]} {mode:>5s}: three-way {af_three:.4f}  '
                  f'two-way {af_two:.4f}  '
                  f'delta {af_two - af_three:+.2e}')


if __name__ == '__main__':
    run()

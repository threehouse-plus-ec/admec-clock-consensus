"""WP3 ablation 2 -- classification threshold sweep.

Tests how sensitive admec_full and freq_exclude are to the per-reading
IC threshold. The WP2/WP3 baseline value 2.976 bit was calibrated in
entry 006 as the worst-case-sigma 95th percentile of per-reading I_k
across ten null noise models. Entry 006 also documented that the
threshold sits in a narrow "active region" -- coherent processes
broaden the mixture density along with the readings, so most signal-
bearing readings stay below it. This ablation sweeps the threshold to
verify that the WP2 conclusion is not sitting on a cliff edge.

Sweep: 7 thresholds spanning ~1.5 -- 6.0 bit, bracketing the baseline
2.976 with explicit +-30 % points and a couple of further-from-baseline
extreme values for context. The harness records the STABLE count for
each (scenario, seed, mode, threshold) cell so that the sensitivity of
the consensus mask itself can be inspected independently of the
metrics.

Output: data/wp3_ablation_threshold_sweep_YYYYMMDD.npz.
"""

import os
import sys
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks, signal_sinusoidal)
from network import make_network
from estimators import admec_full, freq_exclude, _classify_network_full
from classify import Mode, THRESHOLD_95
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

# Bracket baseline THRESHOLD_95 = 2.976 with +-30% points and broader
# extremes. The narrow set tests sensitivity at the operating point;
# the broader extremes show the asymptotic behaviour as everything is
# flagged (low threshold) or nothing is flagged (high threshold).
THRESHOLDS = [1.5, 2.0, 2.5, 2.976, 3.5, 4.5, 6.0]
MODES = ['drop', 'stale']


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
    n_thr, n_mode = len(THRESHOLDS), len(MODES)

    # admec_full results: (scenario, seed, mode, threshold)
    af_mse = np.zeros((n_scn, n_seed, n_mode, n_thr))
    af_ci = np.zeros_like(af_mse)
    af_sc = np.zeros_like(af_mse)

    # freq_exclude (centralised, no delay mode dimension): (scn, seed, threshold)
    fe_mse = np.zeros((n_scn, n_seed, n_thr))
    fe_ci = np.zeros_like(fe_mse)
    fe_sc = np.zeros_like(fe_mse)

    # STABLE-mask sizes per (scn, seed, threshold) -- mean fraction of
    # cells classified STABLE; reveals the active region of the threshold.
    stable_frac = np.zeros((n_scn, n_seed, n_thr))

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

            for ti, thr in enumerate(THRESHOLDS):
                modes_grid = _classify_network_full(
                    Y, Sigmas, window=20,
                    threshold=thr,
                    delta_min_var=0.2105,
                    delta_min_acf=0.8703)
                stable_frac[si, ki, ti] = float(
                    np.mean(modes_grid == int(Mode.STABLE)))

                # freq_exclude
                E_fe = freq_exclude(Y, Sigmas, threshold=thr)
                fe_mse[si, ki, ti] = mse(E_fe)
                fe_ci[si, ki, ti] = collapse_index(E_fe, Sigmas)
                fe_sc[si, ki, ti] = structure_correlation(
                    Y, E_fe, signals, signal_clocks)

                for mi, mode in enumerate(MODES):
                    E = admec_full(Y, Sigmas, adj, delays,
                                    threshold=thr,
                                    delay_mode=mode)
                    af_mse[si, ki, mi, ti] = mse(E)
                    af_ci[si, ki, mi, ti] = collapse_index(E, Sigmas)
                    af_sc[si, ki, mi, ti] = structure_correlation(
                        Y, E, signals, signal_clocks)

            print(f'  done: {scn["name"]} seed {seed}')

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(
        out_dir, f'wp3_ablation_threshold_sweep_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        modes=np.array(MODES),
        thresholds=np.array(THRESHOLDS),
        admec_full_mse=af_mse, admec_full_collapse_index=af_ci,
        admec_full_structure_corr=af_sc,
        freq_exclude_mse=fe_mse, freq_exclude_collapse_index=fe_ci,
        freq_exclude_structure_corr=fe_sc,
        stable_fraction=stable_frac,
        baseline_threshold=THRESHOLD_95,
    )
    print(f'\nSaved: {out_path}')

    # Summary -- STABLE fraction first (the active-region check)
    print('\nMean STABLE fraction over 10 seeds (per scenario, threshold):')
    print(f'{"":>4s}  ' + ' '.join(f'{t:>8.3f}' for t in THRESHOLDS))
    for si, scn in enumerate(SCENARIOS):
        cells = ' '.join(f'{np.mean(stable_frac[si, :, ti]):>8.4f}'
                          for ti in range(n_thr))
        print(f'{scn["name"]:>4s}  {cells}')

    print('\nadmec_full mean MSE per (scenario, mode, threshold):')
    print(f'{"":>4s}  {"":>5s}  ' + ' '.join(f'{t:>8.3f}' for t in THRESHOLDS))
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(MODES):
            cells = ' '.join(f'{np.mean(af_mse[si, :, mi, ti]):>8.4f}'
                              for ti in range(n_thr))
            print(f'{scn["name"]:>4s}  {mode:>5s}  {cells}')

    print('\nfreq_exclude mean MSE per (scenario, threshold):')
    print(f'{"":>4s}  ' + ' '.join(f'{t:>8.3f}' for t in THRESHOLDS))
    for si, scn in enumerate(SCENARIOS):
        cells = ' '.join(f'{np.mean(fe_mse[si, :, ti]):>8.4f}'
                          for ti in range(n_thr))
        print(f'{scn["name"]:>4s}  {cells}')


if __name__ == '__main__':
    run()

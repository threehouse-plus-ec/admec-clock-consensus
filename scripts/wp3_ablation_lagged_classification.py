"""WP3 ablation 5 -- ADMEC-full-lagged (classification uses IC(t-lag)).

Tests for "simultaneity bias" in the WP2 architecture: each clock's IC
at time t is computed against the cross-sectional ensemble at time t,
which includes the clock's own reading. This is fine in the
Gaussian-mixture sense (the integral is well-defined and the
self-contribution is one of N components), but the proposal flagged it
as a configuration to ablate.

The lagged variant classifies reading[t, i] using IC[t - lag, i]
instead of IC[t, i]. With lag = 1, the classifier sees only the
previous-step ensemble, breaking any direct coupling between the IC
and the reading being classified.

Predicted outcome (entry 008 / 010 prediction list): approximately
null delta, on the grounds that consecutive IC values are highly
correlated under reasonable temporal coherence.

Harness: 3 scenarios x 10 seeds x 2 delay modes x 2 lag values
({0, 1}). Output: data/wp3_ablation_lagged_classification_YYYYMMDD.npz.
"""

import os
import sys
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks, signal_sinusoidal)
from network import make_network
from estimators import admec_full
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
MODES = ['drop', 'stale']
LAGS = [0, 1]


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
    n_mode, n_lag = len(MODES), len(LAGS)

    arr_mse = np.zeros((n_scn, n_seed, n_mode, n_lag))
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
            Y, Sigmas = simulate_network_clocks(params, scn['T'],
                                                 dt=1.0, rng=rng)
            adj, delays = make_network(scn['n'], scn['topology'],
                                        scn['delay_mean'], rng=rng)
            signals, signal_clocks = _ground_truth_signals(params, scn['T'])

            for mi, mode in enumerate(MODES):
                for li, lag in enumerate(LAGS):
                    E = admec_full(Y, Sigmas, adj, delays,
                                    delay_mode=mode,
                                    classification_lag=lag)
                    arr_mse[si, ki, mi, li] = mse(E)
                    arr_ci[si, ki, mi, li] = collapse_index(E, Sigmas)
                    arr_sc[si, ki, mi, li] = structure_correlation(
                        Y, E, signals, signal_clocks)
            print(f'  done: {scn["name"]} seed {seed}')

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(
        out_dir, f'wp3_ablation_lagged_classification_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        modes=np.array(MODES),
        lags=np.array(LAGS),
        mse=arr_mse, collapse_index=arr_ci, structure_corr=arr_sc,
    )
    print(f'\nSaved: {out_path}')

    # Summary
    print('\nadmec_full mean MSE (lag=0 vs lag=1):')
    print(f'{"":>4s}  {"":>5s}  {"lag=0":>10s}  {"lag=1":>10s}  '
          f'{"delta":>10s}  {"%":>7s}')
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(MODES):
            m0 = float(np.mean(arr_mse[si, :, mi, 0]))
            m1 = float(np.mean(arr_mse[si, :, mi, 1]))
            pct = (m1 - m0) / m0 * 100 if m0 > 0 else 0.0
            print(f'{scn["name"]:>4s}  {mode:>5s}  {m0:>10.4f}  '
                  f'{m1:>10.4f}  {m1 - m0:>+10.4f}  {pct:>+6.1f}%')

    print('\nadmec_full mean structure correlation (lag=0 vs lag=1):')
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(MODES):
            s0 = float(np.nanmean(arr_sc[si, :, mi, 0]))
            s1 = float(np.nanmean(arr_sc[si, :, mi, 1]))
            print(f'{scn["name"]:>4s}  {mode:>5s}  {s0:>10.4f}  '
                  f'{s1:>10.4f}  delta {s1 - s0:+.4f}')


if __name__ == '__main__':
    run()

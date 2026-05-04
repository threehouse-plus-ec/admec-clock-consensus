"""WP3 ablation 3 -- update-size constraint sensitivity (+/-30 %).

Tests the hypothesis (raised by ablation 1 / entry 008) that the
variance-ratio constraint mis-fires when the proposed update vector
gets noisier under stale-reading mode, causing admec_delay to beat
admec_full on S3 stale (0.340 vs 0.461 mean MSE).

Three constraint axes per the project proposal:
  max_step_factor    (3.0)        per-node 3-sigma box bound
  energy_factor      (1.0)        total N*sigma^2 energy ball
  var_ratio_min/max  (0.5, 1.5)   variance-ratio post-check

Seven configurations (baseline plus +/-30 % on each axis):
  baseline       : (3.0, 1.0, 0.5,  1.5)
  step_loose     : (3.9, 1.0, 0.5,  1.5)
  step_tight     : (2.1, 1.0, 0.5,  1.5)
  energy_loose   : (3.0, 1.3, 0.5,  1.5)
  energy_tight   : (3.0, 0.7, 0.5,  1.5)
  var_loose      : (3.0, 1.0, 0.35, 1.65)
  var_tight      : (3.0, 1.0, 0.65, 1.35)

Scenarios: S1, S2, S3 (the WP2 + ablation-1 set).
Delay modes: drop (WP2 baseline), stale (WP3 ablation 1).
Seeds: 10 (matched RNG order with WP2 campaign for byte-exact
reproducibility of the baseline numbers).
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
from estimators import admec_delay, admec_full
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

VARIANTS = [
    ('baseline',     ConstraintParams(3.0, 1.0, 0.5,  1.5)),
    ('step_loose',   ConstraintParams(3.9, 1.0, 0.5,  1.5)),
    ('step_tight',   ConstraintParams(2.1, 1.0, 0.5,  1.5)),
    ('energy_loose', ConstraintParams(3.0, 1.3, 0.5,  1.5)),
    ('energy_tight', ConstraintParams(3.0, 0.7, 0.5,  1.5)),
    ('var_loose',    ConstraintParams(3.0, 1.0, 0.35, 1.65)),
    ('var_tight',    ConstraintParams(3.0, 1.0, 0.65, 1.35)),
]
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
    n_mode, n_var = len(MODES), len(VARIANTS)

    # admec_full results: (scenario, seed, mode, variant)
    af_mse = np.zeros((n_scn, n_seed, n_mode, n_var))
    af_ci = np.zeros_like(af_mse)
    af_sc = np.zeros_like(af_mse)

    # admec_delay results: (scenario, seed, mode) -- comparator
    ad_mse = np.zeros((n_scn, n_seed, n_mode))
    ad_ci = np.zeros_like(ad_mse)
    ad_sc = np.zeros_like(ad_mse)

    for si, scn in enumerate(SCENARIOS):
        for ki, seed in enumerate(SEEDS):
            rng = np.random.default_rng(seed)
            params = build_scenario_clocks(
                n=scn['n'], n_signal=scn['n_signal'],
                signal_factory=scn['factory'],
                n_degraded=1, degradation_factor=3.0,
                base=ClockParams(sigma_white=1.0))
            # Match scripts/wp2_campaign.py RNG order:
            # simulate_network_clocks first, then make_network.
            Y, Sigmas = simulate_network_clocks(params, scn['T'],
                                                 dt=1.0, rng=rng)
            adj, delays = make_network(scn['n'], scn['topology'],
                                        scn['delay_mean'], rng=rng)
            signals, signal_clocks = _ground_truth_signals(params, scn['T'])

            for mi, mode in enumerate(MODES):
                # admec_delay (one run per mode -- no constraint params)
                E_d = admec_delay(Y, Sigmas, adj, delays, delay_mode=mode)
                ad_mse[si, ki, mi] = mse(E_d)
                ad_ci[si, ki, mi] = collapse_index(E_d, Sigmas)
                ad_sc[si, ki, mi] = structure_correlation(
                    Y, E_d, signals, signal_clocks)

                for vi, (_, cp) in enumerate(VARIANTS):
                    E_f = admec_full(Y, Sigmas, adj, delays,
                                      constraint_params=cp,
                                      delay_mode=mode)
                    af_mse[si, ki, mi, vi] = mse(E_f)
                    af_ci[si, ki, mi, vi] = collapse_index(E_f, Sigmas)
                    af_sc[si, ki, mi, vi] = structure_correlation(
                        Y, E_f, signals, signal_clocks)

            print(f'  done: {scn["name"]} seed {seed}')

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    stamp = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(
        out_dir, f'wp3_ablation_constraint_sensitivity_{stamp}.npz')
    np.savez_compressed(
        out_path,
        scenarios=np.array([s['name'] for s in SCENARIOS]),
        seeds=np.array(SEEDS),
        modes=np.array(MODES),
        variants=np.array([v[0] for v in VARIANTS]),
        variant_params=np.array([
            (cp.max_step_factor, cp.energy_factor,
             cp.var_ratio_min, cp.var_ratio_max)
            for _, cp in VARIANTS]),
        admec_full_mse=af_mse, admec_full_collapse_index=af_ci,
        admec_full_structure_corr=af_sc,
        admec_delay_mse=ad_mse, admec_delay_collapse_index=ad_ci,
        admec_delay_structure_corr=ad_sc,
    )
    print(f'\nSaved: {out_path}')

    # Summary -- focus on S3 stale (the diagnostic case)
    print('\nadmec_full mean MSE per (scenario, mode, variant):')
    print(f'{"scn":>4s} {"mode":>5s}  ' +
          ' '.join(f'{v[0][:11]:>11s}' for v in VARIANTS) +
          f'  | admec_delay')
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(MODES):
            cells = ' '.join(f'{np.mean(af_mse[si, :, mi, vi]):>11.4f}'
                              for vi in range(n_var))
            print(f'{scn["name"]:>4s} {mode:>5s}  {cells}'
                  f'  | {np.mean(ad_mse[si, :, mi]):>11.4f}')

    print('\nadmec_full mean structure correlation per (scenario, mode, variant):')
    print(f'{"scn":>4s} {"mode":>5s}  ' +
          ' '.join(f'{v[0][:11]:>11s}' for v in VARIANTS) +
          f'  | admec_delay')
    for si, scn in enumerate(SCENARIOS):
        for mi, mode in enumerate(MODES):
            cells = ' '.join(
                f'{np.nanmean(af_sc[si, :, mi, vi]):>11.4f}'
                for vi in range(n_var))
            print(f'{scn["name"]:>4s} {mode:>5s}  {cells}'
                  f'  | {np.nanmean(ad_sc[si, :, mi]):>11.4f}')


if __name__ == '__main__':
    run()

"""Reproducible recomputation of DG-2b classification metrics.

Mirrors the (scenario, seed) loop in scripts/wp2_campaign.py but
records, per scenario, the (T, N) classifier exclusion mask and the
designer-injected ground-truth anomaly mask, then aggregates
TPR / FPR / precision / F1 with classification_metrics.

Two reports:
  * "all":    counts every (t, i) cell in every scenario (including
              the null scenarios S4 and S5 where there is no
              ground-truth anomaly anywhere -- which inflates TN
              and depresses FPR).
  * "signal": signal-bearing scenarios only (S1, S2, S3, S6, S7, S8).

Either is defensible; we report both so the precision / F1 values
quoted in entry 007 and wp2-summary.md can be reproduced exactly.
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (ClockParams, build_scenario_clocks,
                    simulate_network_clocks,
                    signal_sinusoidal, signal_step,
                    signal_linear_drift, signal_fold_bifurcation)
from network import make_network
from ic import compute_ic
from temporal import compute_temporal_structure
from classify import classify_array, Mode, THRESHOLD_95, DELTA_MIN_VAR, DELTA_MIN_ACF
from metrics import classification_metrics


def _sin_factory(amplitude, period, onset=0.0):
    def factory(i):
        phase = i * np.pi / 3.0
        return signal_sinusoidal(amplitude=amplitude, period=period,
                                 phase=phase, onset=onset)
    return factory


def _drift_factory(rate, onset):
    def factory(i): return signal_linear_drift(rate=rate, onset=onset)
    return factory


def _step_factory(magnitude, onset):
    def factory(i): return signal_step(magnitude=magnitude, onset=onset)
    return factory


def _fold_factory(epsilon, r0, x0, onset):
    def factory(i): return signal_fold_bifurcation(epsilon=epsilon, r0=r0,
                                                    x0=x0, onset=onset)
    return factory


SCENARIOS = [
    dict(name='S1', n=15, topology='ring', delay_mean=2.0,
         T=200, n_signal=3, factory=_sin_factory(5.0, 50.0, 0.0),
         onset=0, has_signal=True),
    dict(name='S2', n=15, topology='fully_connected', delay_mean=0.3,
         T=200, n_signal=3, factory=_sin_factory(5.0, 50.0, 0.0),
         onset=0, has_signal=True),
    dict(name='S3', n=50, topology='random_sparse', delay_mean=4.0,
         T=200, n_signal=3, factory=_sin_factory(5.0, 50.0, 0.0),
         onset=0, has_signal=True),
    dict(name='S4', n=15, topology='ring', delay_mean=2.0,
         T=200, n_signal=0, factory=None, onset=0, has_signal=False),
    dict(name='S5', n=50, topology='random_sparse', delay_mean=4.0,
         T=200, n_signal=0, factory=None, onset=0, has_signal=False),
    dict(name='S6', n=15, topology='ring', delay_mean=2.0,
         T=200, n_signal=2, factory=_drift_factory(0.01, 0),
         onset=0, has_signal=True),
    dict(name='S7', n=30, topology='ring', delay_mean=2.0,
         T=200, n_signal=3, factory=_step_factory(5.0, 100),
         onset=100, has_signal=True),
    dict(name='S8', n=15, topology='ring', delay_mean=2.0,
         T=200, n_signal=2, factory=_fold_factory(0.005, -1.0, 0.0, 0),
         onset=0, has_signal=True),
]
SEEDS = list(range(2026, 2036))


def _classify(Y, Sigmas, window=20):
    T, N = Y.shape
    IC = np.zeros_like(Y)
    for t in range(T):
        IC[t, :] = compute_ic(Y[t, :], Sigmas[t, :])
    var_slopes = np.full((T, N), np.nan)
    acfs = np.full((T, N), np.nan)
    for j in range(N):
        var_slopes[:, j], acfs[:, j] = compute_temporal_structure(
            Y[:, j], window=window)
    return classify_array(IC, var_slopes, acfs,
                          threshold=THRESHOLD_95,
                          delta_min_var=DELTA_MIN_VAR,
                          delta_min_acf=DELTA_MIN_ACF)


def run():
    aggregates = {
        'all':    dict(tp=0, fp=0, fn=0, tn=0,
                       tp_struct=0, fn_struct=0),
        'signal': dict(tp=0, fp=0, fn=0, tn=0,
                       tp_struct=0, fn_struct=0),
    }
    per_scn = {scn['name']: dict(tp=0, fp=0, fn=0, tn=0,
                                  tp_struct=0, fn_struct=0)
               for scn in SCENARIOS if scn['has_signal']}
    for scn in SCENARIOS:
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            params = build_scenario_clocks(
                n=scn['n'], n_signal=scn['n_signal'],
                signal_factory=scn['factory'],
                n_degraded=1, degradation_factor=3.0,
                base=ClockParams(sigma_white=1.0))
            # RNG ORDER: simulate clocks BEFORE sampling network to
            # match scripts/wp2_campaign.py byte-for-byte. Reverse
            # order produces different (Y, adj, delays) realisations
            # for the same seed and so different classification stats.
            Y, Sigmas = simulate_network_clocks(params, scn['T'],
                                                 dt=1.0, rng=rng)
            adj, delays = make_network(scn['n'], scn['topology'],
                                        scn['delay_mean'], rng=rng)
            modes = _classify(Y, Sigmas, window=20)

            T, N = Y.shape
            true_anom = np.zeros_like(Y, dtype=bool)
            for i in range(N):
                if i < scn['n_signal']:
                    true_anom[scn['onset']:, i] = True
            excluded = (modes == int(Mode.STRUCTURED)) | \
                       (modes == int(Mode.UNSTRUCTURED))
            structured = modes == int(Mode.STRUCTURED)

            tags = ('all',) + (('signal',) if scn['has_signal'] else ())
            for tag in tags:
                a = aggregates[tag]
                a['tp'] += int(np.sum(excluded & true_anom))
                a['fp'] += int(np.sum(excluded & ~true_anom))
                a['fn'] += int(np.sum(~excluded & true_anom))
                a['tn'] += int(np.sum(~excluded & ~true_anom))
                a['tp_struct'] += int(np.sum(structured & true_anom))
                a['fn_struct'] += int(np.sum(~structured & true_anom))
            if scn['has_signal']:
                a = per_scn[scn['name']]
                a['tp'] += int(np.sum(excluded & true_anom))
                a['fp'] += int(np.sum(excluded & ~true_anom))
                a['fn'] += int(np.sum(~excluded & true_anom))
                a['tn'] += int(np.sum(~excluded & ~true_anom))
                a['tp_struct'] += int(np.sum(structured & true_anom))
                a['fn_struct'] += int(np.sum(~structured & true_anom))

    def _summarise(label, a):
        tp, fp, fn, tn = a['tp'], a['fp'], a['fn'], a['tn']
        tpr = tp / (tp + fn) if tp + fn else 0.0
        fpr = fp / (fp + tn) if fp + tn else 0.0
        prec = tp / (tp + fp) if tp + fp else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        struct_tpr = (a['tp_struct'] / (a['tp_struct'] + a['fn_struct'])
                      if (a['tp_struct'] + a['fn_struct']) else 0.0)
        print(f'  [{label:>22s}] TPR={tpr:.4f}  FPR={fpr:.4f}  '
              f'precision={prec:.4f}  F1={f1:.4f}  '
              f'struct-TPR={struct_tpr:.4f}')

    print('\n=== Aggregate ===')
    for tag, a in aggregates.items():
        _summarise(f'{tag} scenarios', a)

    print('\n=== Per-scenario (signal scenarios only) ===')
    for name, a in per_scn.items():
        _summarise(name, a)


if __name__ == '__main__':
    run()

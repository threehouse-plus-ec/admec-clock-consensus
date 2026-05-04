"""
WP2 simulation campaign: 8 scenarios × 10 seeds × 9 estimators.

Runs the full benchmark suite defined in the project proposal (sec. WP2)
and saves metrics to ``data/wp2_campaign_YYYYMMDD.npz``.

Scenarios
---------
S1  15 nodes, ring, Poisson(2.0), sinusoidal on 3 clocks
S2  15 nodes, fully connected, Poisson(0.3), sinusoidal on 3 clocks
S3  50 nodes, random-sparse, Poisson(4.0), sinusoidal on 3 clocks
S4  15 nodes, ring, Poisson(2.0), null
S5  50 nodes, random-sparse, Poisson(4.0), null at scale
S6  15 nodes, ring, Poisson(2.0), linear drift on 2 clocks
S7  30 nodes, ring, Poisson(2.0), step on 3 clocks at T/2
S8  15 nodes, ring, Poisson(2.0), fold bifurcation on 2 clocks

Metrics
-------
mse            — mean squared error vs reference 0
collapse_index — time-averaged estimate spread / mean sigma
structure_corr — Pearson r(residual, signal) post-onset

Usage
-----
    python scripts/wp2_campaign.py
    python scripts/wp2_campaign.py --smoke   # 2 scenarios, 2 seeds, quick
    python scripts/wp2_campaign.py --seeds 5 --T 100
"""

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clocks import (
    ClockParams,
    build_scenario_clocks,
    simulate_network_clocks,
    signal_sinusoidal,
    signal_linear_drift,
    signal_step,
    signal_fold_bifurcation,
)
from network import make_network
from estimators import ESTIMATORS
from metrics import mse, collapse_index, structure_correlation


# ------------------------------------------------------------------
# Scenario definitions
# ------------------------------------------------------------------


@dataclass
class Scenario:
    name: str
    n: int
    topology: str
    delay_mean: float
    T: int
    dt: float
    n_signal: int
    signal_factory: Optional[Callable[[int], Callable]]
    n_degraded: int
    degradation_factor: float
    description: str
    onset_idx: int = 0


def _sinusoidal_factory(amplitude: float, period: float, onset: float = 0.0):
    """Return a signal factory that gives each signal clock a different phase."""

    def factory(i: int):
        phase = i * np.pi / 3.0
        return signal_sinusoidal(amplitude, period, phase=phase, onset=onset)

    return factory


def make_scenarios(T: int = 200, dt: float = 1.0) -> List[Scenario]:
    """Return the 8 WP2 scenarios from the proposal."""
    sigma = 1.0  # unit scale for simulation (sigma_white = 1.0)

    scenarios = [
        # S1: structure preservation, moderate delay
        Scenario(
            name="S1",
            n=15,
            topology="ring",
            delay_mean=2.0,
            T=T,
            dt=dt,
            n_signal=3,
            signal_factory=_sinusoidal_factory(
                amplitude=5.0 * sigma, period=50.0
            ),
            n_degraded=1,
            degradation_factor=3.0,
            description="Sinusoidal on 3 clocks, ring, Poisson(2.0)",
            onset_idx=0,
        ),
        # S2: control, negligible delay
        Scenario(
            name="S2",
            n=15,
            topology="fully_connected",
            delay_mean=0.3,
            T=T,
            dt=dt,
            n_signal=3,
            signal_factory=_sinusoidal_factory(
                amplitude=5.0 * sigma, period=50.0
            ),
            n_degraded=1,
            degradation_factor=3.0,
            description="Sinusoidal on 3 clocks, fully connected, Poisson(0.3)",
            onset_idx=0,
        ),
        # S3: scaling
        Scenario(
            name="S3",
            n=50,
            topology="random_sparse",
            delay_mean=4.0,
            T=T,
            dt=dt,
            n_signal=3,
            signal_factory=_sinusoidal_factory(
                amplitude=5.0 * sigma, period=50.0
            ),
            n_degraded=1,
            degradation_factor=3.0,
            description="Sinusoidal on 3 clocks, random-sparse, Poisson(4.0)",
            onset_idx=0,
        ),
        # S4: null
        Scenario(
            name="S4",
            n=15,
            topology="ring",
            delay_mean=2.0,
            T=T,
            dt=dt,
            n_signal=0,
            signal_factory=None,
            n_degraded=1,
            degradation_factor=3.0,
            description="Null, ring, Poisson(2.0)",
            onset_idx=0,
        ),
        # S5: null at scale
        Scenario(
            name="S5",
            n=50,
            topology="random_sparse",
            delay_mean=4.0,
            T=T,
            dt=dt,
            n_signal=0,
            signal_factory=None,
            n_degraded=1,
            degradation_factor=3.0,
            description="Null at scale, random-sparse, Poisson(4.0)",
            onset_idx=0,
        ),
        # S6: linear drift (not near-critical)
        Scenario(
            name="S6",
            n=15,
            topology="ring",
            delay_mean=2.0,
            T=T,
            dt=dt,
            n_signal=2,
            signal_factory=lambda i: signal_linear_drift(
                rate=0.01 * sigma, onset=0.0
            ),
            n_degraded=1,
            degradation_factor=3.0,
            description="Linear drift on 2 clocks, ring, Poisson(2.0)",
            onset_idx=0,
        ),
        # S7: step change
        Scenario(
            name="S7",
            n=30,
            topology="ring",
            delay_mean=2.0,
            T=T,
            dt=dt,
            n_signal=3,
            signal_factory=lambda i: signal_step(
                magnitude=5.0 * sigma, onset=T * dt / 2.0
            ),
            n_degraded=1,
            degradation_factor=3.0,
            description="Step on 3 clocks at T/2, ring, Poisson(2.0)",
            onset_idx=T // 2,
        ),
        # S8: fold bifurcation (near-critical)
        Scenario(
            name="S8",
            n=15,
            topology="ring",
            delay_mean=2.0,
            T=T,
            dt=dt,
            n_signal=2,
            signal_factory=lambda i: signal_fold_bifurcation(
                epsilon=0.005, r0=-1.0, onset=0.0
            ),
            n_degraded=1,
            degradation_factor=3.0,
            description="Fold bifurcation on 2 clocks, ring, Poisson(2.0)",
            onset_idx=0,
        ),
    ]
    return scenarios


# ------------------------------------------------------------------
# Single scenario / seed execution
# ------------------------------------------------------------------


def run_scenario_seed(
    scenario: Scenario, seed: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate data for one scenario and seed.

    Returns
    -------
    Y : array (T, N)
        Fractional-frequency readings.
    Sigmas : array (T, N)
        Declared uncertainties.
    signals : array (T, N)
        Injected signal ground truth.
    adj : array (N, N) bool
    delays : array (N, N) int
    """
    rng = np.random.default_rng(seed)

    params_list = build_scenario_clocks(
        n=scenario.n,
        n_signal=scenario.n_signal,
        signal_factory=scenario.signal_factory,
        n_degraded=scenario.n_degraded,
        degradation_factor=scenario.degradation_factor,
        base=ClockParams(sigma_white=1.0, sigma_flicker=0.0, sigma_rw=0.0),
    )

    Y, Sigmas = simulate_network_clocks(params_list, scenario.T, scenario.dt, rng)

    # Ground-truth signals for metric evaluation
    t = np.arange(scenario.T, dtype=float) * scenario.dt
    signals = np.zeros((scenario.T, scenario.n))
    for i, p in enumerate(params_list):
        if p.signal is not None:
            signals[:, i] = p.signal(t)

    adj, delays = make_network(
        scenario.n,
        scenario.topology,
        delay_mean=scenario.delay_mean,
        rng=rng,
    )

    return Y, Sigmas, signals, adj, delays


def run_estimator(
    name: str,
    estimator_fn: Callable,
    Y: np.ndarray,
    Sigmas: np.ndarray,
    adj: np.ndarray,
    delays: np.ndarray,
) -> np.ndarray:
    """Run one estimator, returning estimates or NaN on failure."""
    try:
        # All estimators accept adj/delays as kwargs;
        # local ones require them, centralised ones ignore them.
        estimates = estimator_fn(Y, Sigmas, adj=adj, delays=delays)
        return np.asarray(estimates, dtype=np.float64)
    except Exception as exc:
        print(f"  ERROR in {name}: {exc}")
        return np.full_like(Y, np.nan)


def compute_metrics(
    estimates: np.ndarray,
    Y: np.ndarray,
    Sigmas: np.ndarray,
    signals: np.ndarray,
    scenario: Scenario,
) -> dict:
    """Compute the three primary metrics for one estimator run."""
    metrics = {
        "mse": mse(estimates),
        "collapse_index": collapse_index(estimates, Sigmas),
    }

    if scenario.n_signal > 0:
        signal_clocks = np.arange(scenario.n_signal)
        metrics["structure_corr"] = structure_correlation(
            Y, estimates, signals, signal_clocks, scenario.onset_idx
        )
    else:
        metrics["structure_corr"] = np.nan

    return metrics


# ------------------------------------------------------------------
# Campaign loop
# ------------------------------------------------------------------


def run_campaign(
    scenarios: List[Scenario],
    seeds: List[int],
    estimators: Dict[str, Callable],
    verbose: bool = True,
) -> dict:
    """Run the full campaign and return a results dictionary.

    Metric arrays have shape (n_scenarios, n_seeds, n_estimators).
    """
    n_scen = len(scenarios)
    n_seed = len(seeds)
    n_est = len(estimators)

    mse_arr = np.full((n_scen, n_seed, n_est), np.nan)
    ci_arr = np.full((n_scen, n_seed, n_est), np.nan)
    sc_arr = np.full((n_scen, n_seed, n_est), np.nan)

    for si, scen in enumerate(scenarios):
        if verbose:
            print(f"\nScenario {scen.name}: {scen.description}")
        for ri, seed in enumerate(seeds):
            if verbose:
                print(f"  Seed {seed}")

            Y, Sigmas, signals, adj, delays = run_scenario_seed(scen, seed)

            for ei, (ename, efn) in enumerate(estimators.items()):
                if verbose:
                    print(f"    {ename} ...", end="", flush=True)

                estimates = run_estimator(ename, efn, Y, Sigmas, adj, delays)
                met = compute_metrics(estimates, Y, Sigmas, signals, scen)

                mse_arr[si, ri, ei] = met["mse"]
                ci_arr[si, ri, ei] = met["collapse_index"]
                sc_arr[si, ri, ei] = met["structure_corr"]

                if verbose:
                    print(
                        f" MSE={met['mse']:.4e} "
                        f"CI={met['collapse_index']:.4f} "
                        f"SC={met['structure_corr']:.3f}"
                    )

    return {
        "mse": mse_arr,
        "collapse_index": ci_arr,
        "structure_corr": sc_arr,
        "scenarios": np.array([s.name for s in scenarios]),
        "seeds": np.array(seeds),
        "estimators": np.array(list(estimators.keys())),
    }


def print_summary(results: dict) -> None:
    """Print a concise summary table of mean metrics per scenario × estimator."""
    scenarios = results["scenarios"]
    estimators = results["estimators"]
    mse_arr = results["mse"]
    ci_arr = results["collapse_index"]
    sc_arr = results["structure_corr"]

    print("\n" + "=" * 70)
    print("CAMPAIGN SUMMARY (mean over seeds)")
    print("=" * 70)
    print(f"{'Scenario':<8} {'Estimator':<20} {'MSE':>12} {'CI':>8} {'SC':>8}")
    print("-" * 70)

    for si, sname in enumerate(scenarios):
        for ei, ename in enumerate(estimators):
            m = np.nanmean(mse_arr[si, :, ei])
            c = np.nanmean(ci_arr[si, :, ei])
            r = np.nanmean(sc_arr[si, :, ei])
            print(
                f"{sname:<8} {ename:<20} {m:12.4e} {c:8.4f} {r:8.3f}"
            )


def main():
    parser = argparse.ArgumentParser(description="WP2 simulation campaign")
    parser.add_argument(
        "--smoke", action="store_true",
        help="Run smoke test: 2 scenarios, 2 seeds, quick validation"
    )
    parser.add_argument(
        "--seeds", type=int, default=10,
        help="Number of seeds (default 10)"
    )
    parser.add_argument(
        "--T", type=int, default=200,
        help="Time steps per scenario (default 200)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output file path (default data/wp2_campaign_YYYYMMDD.npz)"
    )
    args = parser.parse_args()

    if args.smoke:
        scenarios = make_scenarios(T=args.T)[:2]
        seeds = [2026, 2027]
        print("SMOKE TEST: 2 scenarios, 2 seeds")
    else:
        scenarios = make_scenarios(T=args.T)
        seeds = list(range(2026, 2026 + args.seeds))

    print(
        f"Campaign: {len(scenarios)} scenarios × {len(seeds)} seeds "
        f"× {len(ESTIMATORS)} estimators"
    )
    print(f"T = {args.T}")

    results = run_campaign(scenarios, seeds, ESTIMATORS, verbose=True)
    print_summary(results)

    if args.output is None:
        today = datetime.now().strftime("%Y%m%d")
        suffix = "_smoke" if args.smoke else ""
        args.output = f"data/wp2_campaign_{today}{suffix}.npz"

    np.savez_compressed(args.output, **results)
    size_mb = os.path.getsize(args.output) / (1024 * 1024)
    print(f"\nSaved results to {args.output}")
    print(f"Size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()

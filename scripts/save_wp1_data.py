"""
Retroactively save WP1 data as .npz files for entries 001-004.

This script re-runs the same computations from the figure scripts
using the same seed (2026) and saves the raw arrays.

Saves:
    data/001_aipp_convergence.npz
    data/002_sigma_sensitivity.npz
    data/003_powerlaw_thresholds.npz
    data/004_delta_min.npz
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic, compute_aipp, aipp_gaussian_limit, perturb_sigmas
from noise import (generate_pareto_symmetric, generate_flicker,
                   generate_random_walk, generate_ar1)
from temporal import compute_temporal_structure, calibrate_delta_min

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)


# ---------------------------------------------------------------
# Entry 001: AIPP convergence
# ---------------------------------------------------------------
print("Generating 001_aipp_convergence.npz ...")

Ns = [5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
n_real = 200
rng = np.random.default_rng(2026)

# Store AIPP per N per realisation
aipp_per_N = {}
for n in Ns:
    aipps = []
    for _ in range(n_real):
        values = rng.normal(0, 1, n)
        sigmas = np.ones(n)
        ic = compute_ic(values, sigmas)
        aipps.append(compute_aipp(ic))
    aipp_per_N[n] = np.array(aipps)

# Threshold values per noise model (5 original models, N=50)
rng_thresh = np.random.default_rng(2026)
N_thresh = 50
threshold_models = ["Gaussian", "Heteroscedastic", "Student-t(3)",
                    "Student-t(5)", "AR(1) rho=0.7"]
thresholds = {}
for model in threshold_models:
    aipps = []
    for _ in range(200):
        if model == "Gaussian":
            v = rng_thresh.normal(0, 1, N_thresh)
            s = np.ones(N_thresh)
        elif model == "Heteroscedastic":
            s = np.exp(rng_thresh.normal(0, 0.5, N_thresh))
            v = rng_thresh.normal(0, s)
        elif model == "Student-t(3)":
            v = rng_thresh.standard_t(3, N_thresh)
            s = np.ones(N_thresh) * np.sqrt(3)
        elif model == "Student-t(5)":
            v = rng_thresh.standard_t(5, N_thresh)
            s = np.ones(N_thresh) * np.sqrt(5 / 3)
        elif model == "AR(1) rho=0.7":
            v = generate_ar1(N_thresh, rho=0.7, rng=rng_thresh)
            s = np.ones(N_thresh)
        ic = compute_ic(v, s)
        aipps.append(compute_aipp(ic))
    thresholds[model] = np.percentile(aipps, 95)

np.savez_compressed(
    os.path.join(data_dir, '001_aipp_convergence.npz'),
    sample_sizes=np.array(Ns),
    n_realisations=n_real,
    **{f'aipp_N{n}': aipp_per_N[n] for n in Ns},
    threshold_models=np.array(threshold_models),
    threshold_values=np.array([thresholds[m] for m in threshold_models]),
    seed=2026,
)
print("  done.")


# ---------------------------------------------------------------
# Entry 002: sigma sensitivity
# ---------------------------------------------------------------
print("Generating 002_sigma_sensitivity.npz ...")

N_sens = 200
N_REAL_sens = 300
MAGNITUDE = 0.2

conditions = {
    'unperturbed': None,
    'random': 'random',
    'systematic_plus': 'systematic+',
    'systematic_minus': 'systematic-',
}

rng = np.random.default_rng(2026)
sens_results = {}
for key, mode in conditions.items():
    aipps = []
    for _ in range(N_REAL_sens):
        values = rng.normal(0, 1, N_sens)
        sigmas_true = np.ones(N_sens)
        if mode is None:
            sigmas_used = sigmas_true
        else:
            sigmas_used = perturb_sigmas(sigmas_true, mode=mode,
                                         magnitude=MAGNITUDE, rng=rng)
        ic = compute_ic(values, sigmas_used)
        aipps.append(compute_aipp(ic))
    sens_results[key] = np.array(aipps)

# Also at N=50
rng = np.random.default_rng(2026)
sens_results_N50 = {}
for key, mode in conditions.items():
    aipps = []
    for _ in range(N_REAL_sens):
        values = rng.normal(0, 1, 50)
        sigmas_true = np.ones(50)
        if mode is None:
            sigmas_used = sigmas_true
        else:
            sigmas_used = perturb_sigmas(sigmas_true, mode=mode,
                                         magnitude=MAGNITUDE, rng=rng)
        ic = compute_ic(values, sigmas_used)
        aipps.append(compute_aipp(ic))
    sens_results_N50[key] = np.array(aipps)

np.savez_compressed(
    os.path.join(data_dir, '002_sigma_sensitivity.npz'),
    **{f'aipp_N200_{k}': v for k, v in sens_results.items()},
    **{f'aipp_N50_{k}': v for k, v in sens_results_N50.items()},
    magnitude=MAGNITUDE,
    n_realisations=N_REAL_sens,
    seed=2026,
)
print("  done.")


# ---------------------------------------------------------------
# Entry 003: power-law thresholds
# ---------------------------------------------------------------
print("Generating 003_powerlaw_thresholds.npz ...")

N_pw = 50
N_REAL_pw = 300
rng = np.random.default_rng(2026)

model_names = [
    "gaussian", "heteroscedastic", "student_t_3", "student_t_5",
    "ar1_07", "pareto_25", "pareto_30", "fgn_09", "ar1_09",
    "random_walk"
]


def gen_model(name, N, rng):
    if name == "gaussian":
        v = rng.normal(0, 1, N)
        return v, np.ones(N)
    elif name == "heteroscedastic":
        s = np.exp(rng.normal(0, 0.5, N))
        return rng.normal(0, s), s
    elif name == "student_t_3":
        v = rng.standard_t(3, N)
        return v, np.ones(N) * np.sqrt(3)
    elif name == "student_t_5":
        v = rng.standard_t(5, N)
        return v, np.ones(N) * np.sqrt(5 / 3)
    elif name == "ar1_07":
        v = generate_ar1(N, rho=0.7, rng=rng)
        return v, np.ones(N)
    elif name == "pareto_25":
        v = generate_pareto_symmetric(N, alpha=2.5, rng=rng)
        return v, np.ones(N) * np.std(v)
    elif name == "pareto_30":
        v = generate_pareto_symmetric(N, alpha=3.0, rng=rng)
        return v, np.ones(N) * np.std(v)
    elif name == "fgn_09":
        v = generate_flicker(N, H=0.9, rng=rng)
        return v, np.ones(N) * max(np.std(v), 1e-6)
    elif name == "ar1_09":
        v = generate_ar1(N, rho=0.9, rng=rng)
        return v, np.ones(N)
    elif name == "random_walk":
        v = generate_random_walk(N, rng=rng)
        s = np.maximum(np.sqrt(np.arange(1, N + 1, dtype=float)), 1.0)
        return v, s


pw_results = {}
for name in model_names:
    aipps = []
    for _ in range(N_REAL_pw):
        v, s = gen_model(name, N_pw, rng)
        ic = compute_ic(v, s)
        aipps.append(compute_aipp(ic))
    pw_results[name] = np.array(aipps)

# Finite-N bias: AIPP vs N for Gaussian
bias_Ns = [5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500]
rng_bias = np.random.default_rng(2026)
bias_means = []
for n in bias_Ns:
    aipps = []
    for _ in range(200):
        v = rng_bias.normal(0, 1, n)
        s = np.ones(n)
        ic = compute_ic(v, s)
        aipps.append(compute_aipp(ic))
    bias_means.append(np.mean(aipps))
bias_means = np.array(bias_means)

# Fit a + b/N + AIPP_inf
from scipy.optimize import curve_fit

def bias_model(N, a, b, aipp_inf):
    return a / N + b / N**2 + aipp_inf

bias_Ns_arr = np.array(bias_Ns, dtype=float)
popt, _ = curve_fit(bias_model, bias_Ns_arr, bias_means, p0=[1.0, 1.0, 1.25])

np.savez_compressed(
    os.path.join(data_dir, '003_powerlaw_thresholds.npz'),
    model_names=np.array(model_names),
    **{f'aipp_{name}': pw_results[name] for name in model_names},
    bias_sample_sizes=np.array(bias_Ns),
    bias_means=bias_means,
    bias_fit_a=popt[0],
    bias_fit_b=popt[1],
    bias_fit_aipp_inf=popt[2],
    n_realisations=N_REAL_pw,
    seed=2026,
)
print("  done.")


# ---------------------------------------------------------------
# Entry 004: delta_min calibration
# ---------------------------------------------------------------
print("Generating 004_delta_min.npz ...")

WINDOW = 20
T_dm = 200
N_REAL_dm = 300
MULTIPLIER = 3.0
ACF_PERCENTILE = 95.0

rng = np.random.default_rng(2026)

dm_models = [
    "Gaussian", "Heteroscedastic", "Student-t(3)", "Student-t(5)",
    "AR(1) rho=0.7", "Pareto alpha=2.5", "Pareto alpha=3.0",
    "fGn H=0.9", "AR(1) rho=0.9", "Random walk"
]


def gen_dm(model, T, rng):
    if model == "Gaussian":
        return rng.normal(0, 1, T)
    elif model == "Heteroscedastic":
        s = np.exp(rng.normal(0, 0.5, T))
        return rng.normal(0, s)
    elif model == "Student-t(3)":
        return rng.standard_t(3, T)
    elif model == "Student-t(5)":
        return rng.standard_t(5, T)
    elif model == "AR(1) rho=0.7":
        return generate_ar1(T, rho=0.7, rng=rng)
    elif model == "Pareto alpha=2.5":
        return generate_pareto_symmetric(T, alpha=2.5, rng=rng)
    elif model == "Pareto alpha=3.0":
        return generate_pareto_symmetric(T, alpha=3.0, rng=rng)
    elif model == "fGn H=0.9":
        return generate_flicker(T, H=0.9, rng=rng)
    elif model == "AR(1) rho=0.9":
        return generate_ar1(T, rho=0.9, rng=rng)
    elif model == "Random walk":
        return generate_random_walk(T, rng=rng)


per_model_var = {}
per_model_acf = {}
for model in dm_models:
    var_slopes = []
    autocorrs = []
    for _ in range(N_REAL_dm):
        series = gen_dm(model, T_dm, rng)
        vs, ac = compute_temporal_structure(series, window=WINDOW)
        var_slopes.append(vs[~np.isnan(vs)])
        autocorrs.append(ac[~np.isnan(ac)])
    per_model_var[model] = np.concatenate(var_slopes)
    per_model_acf[model] = np.concatenate(autocorrs)

# Find hardest nulls and compute delta_min
hardest_var_model = max(dm_models, key=lambda m: np.median(np.abs(per_model_var[m])))
hardest_acf_model = max(dm_models, key=lambda m: np.median(np.abs(per_model_acf[m])))

delta_var = MULTIPLIER * np.median(np.abs(per_model_var[hardest_var_model]))
delta_acf = np.percentile(np.abs(per_model_acf[hardest_acf_model]), ACF_PERCENTILE)

# Sanity check signals
rng_san = np.random.default_rng(2026)
t = np.arange(T_dm, dtype=float)
# Sinusoidal drift
signal_sin = 2.0 * np.sin(2 * np.pi * t / 50) + rng_san.normal(0, 1, T_dm)
vs_sin, ac_sin = compute_temporal_structure(signal_sin, window=WINDOW)
# Growing variance
signal_var = rng_san.normal(0, 1, T_dm) * (1 + 0.03 * t)
vs_var, ac_var = compute_temporal_structure(signal_var, window=WINDOW)

np.savez_compressed(
    os.path.join(data_dir, '004_delta_min.npz'),
    model_names=np.array(dm_models),
    **{f'null_var_{m.replace(" ", "_").replace("=", "")}': per_model_var[m]
       for m in dm_models},
    **{f'null_acf_{m.replace(" ", "_").replace("=", "")}': per_model_acf[m]
       for m in dm_models},
    delta_min_var=delta_var,
    delta_min_acf=delta_acf,
    hardest_var_model=hardest_var_model,
    hardest_acf_model=hardest_acf_model,
    var_multiplier=MULTIPLIER,
    acf_percentile=ACF_PERCENTILE,
    sanity_sinusoidal=signal_sin,
    sanity_growing_var=signal_var,
    sanity_sin_var_slopes=vs_sin,
    sanity_sin_autocorrs=ac_sin,
    sanity_var_var_slopes=vs_var,
    sanity_var_autocorrs=ac_var,
    window=WINDOW,
    n_realisations=N_REAL_dm,
    seed=2026,
)
print("  done.")

# Summary
for f in ['001_aipp_convergence.npz', '002_sigma_sensitivity.npz',
          '003_powerlaw_thresholds.npz', '004_delta_min.npz']:
    path = os.path.join(data_dir, f)
    size_kb = os.path.getsize(path) / 1024
    print(f"  {f}: {size_kb:.1f} KB")

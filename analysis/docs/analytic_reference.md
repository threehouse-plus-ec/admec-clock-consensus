# Analytic Reference Pipeline v0.2

Endorsement Marker: Local candidate framework (no parity implied with externally
validated laws). The analytic reference model is an architectural lens, not a
physical law. External constraints (e.g. Cramer-Rao bounds) are referenced as
established coastlines, not replicated.

## Scope

ARP v0.2 defines a controlled analytic reference for interpreting exported ADMEC
campaign data. It is not a universal bound and does not import or execute the
simulation layer.

The load-bearing null assumption is `s_j(t)=0`. Under independent Gaussian
readings with known positive standard deviations,

```text
Var(x_cent) = 1 / sum_j sigma_j^-2
Var(x_i)    = 1 / sum_{j in A_i} sigma_j^-2
```

For homogeneous sigmas, the local-to-central reference ratio reduces to

```text
MSE_local / MSE_cent ~= N / k_bar
```

where `k_bar = E[k_i(t)] + 1` is the arithmetic mean of accessible-set sizes
(including self).  Exported neighbour counts that exclude self are converted
with `k_bar = E[counts] + 1`.

**Note on naming:** `k_bar` is the *arithmetic* mean accessible-set size, not a
harmonic effective-k.  It is the appropriate average for the homogeneous
reference ratio used in the Jensen-gap decomposition.

## Jensen Gap

The mandatory topology-heterogeneity term is

```text
Delta_J = E[N / k_i] - N / k_bar
```

It is non-negative by convexity for positive `k_i`, modulo numerical roundoff.
It quantifies the error introduced by replacing heterogeneous local topology
with a single averaged `k_bar`.

## Deviation Decomposition

ARP reports

```text
Delta_total = MSE_local / MSE_cent - N / k_bar
Delta_res   = Delta_total - Delta_J
```

Sign interpretation is fixed:

```text
Delta_res < 0: helpful violation; temporal pooling/correlations increase
               effective information beyond the static independent-reading
               assumption
Delta_res > 0: unmodelled degradation; staleness bias or adversarial topology
```

Current data may be expected to show negative residuals, but the implementation
does not enforce that sign.

## ADMEC vs Ideal-Local

ARP reports

```text
Delta_ADMEC = MSE_ADMEC - MSE_ideal_local
```

No sign assumption is permitted:

```text
Delta_ADMEC > 0: information loss dominates
Delta_ADMEC < 0: bias reduction dominates
```

## Data Boundary

The analytic pipeline consumes exported data only. Accepted interfaces are
numeric CSV matrices, optional HDF5 records if `h5py` is installed, and existing
local `.npz` archive exports. ARP modules do not import clocks, network,
estimator, or campaign harness code.

Required export fields for a single comparison are:

```text
k_i or neighbour-count matrix
local_mse
central_mse
topology_id
delay_parameters
seed
assumption_flags
```

`admec_mse` and `ideal_local_mse` are optional and enable the ADMEC-vs-ideal-local
delta.

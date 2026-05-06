# Notebooks

The three tutorials track the three completed work packages of the project. Each loads the canonical archives in `data/` rather than re-running simulations from scratch, so they execute in a few minutes on a laptop.

| Tutorial | Topic | Runtime | Mirrored markdown |
|----------|-------|---------|-------------------|
| [`wp1_tutorial.ipynb`](wp1_tutorial.ipynb) | WP1: IC definition, null calibration, σ-sensitivity, temporal-structure gates, classification rule, positioning against χ² / Huber / Allan deviation. Closing pointer to where the WP1 calibration lands in WP2/WP3. | ~30 s | [`docs/wp1_tutorial.md`](../docs/wp1_tutorial.md) |
| [`wp2_tutorial.ipynb`](wp2_tutorial.ipynb) | WP2: 15-clock ring scenario built from scratch, 8 estimators run on the same simulation, three IC-independent metrics, the canonical 8 × 10 × 9 archive loaded, and the **DG-2 NOT MET** verdict reproduced. Closing pointer to the WP3 ablations. | ~3 min | [`docs/wp2_tutorial.md`](../docs/wp2_tutorial.md) |
| [`wp3_tutorial.ipynb`](wp3_tutorial.ipynb) | WP3: five ablation archives walked through (delay convention, constraint sensitivity, two-vs-three-way, threshold sweep, lagged classification), the integrated combined-tuning archive, and an inline reproduction of the manuscript's topology pooling-reference figure. Closing pointer to the manuscript and the redesign options. | ~3 min | [`docs/wp3_tutorial.md`](../docs/wp3_tutorial.md) |

For the canonical writeup that synthesises the three work packages, see [`docs/manuscript.md`](../docs/manuscript.md).

For reproducibility:

- Sources of every number in `docs/manuscript.md` are mapped to a (script, archive) pair in § 7 of that document.
- Every `data/*.npz` archive in this repository was produced by a `scripts/*.py` script that uses the same RNG ordering as `scripts/wp2_campaign.py`. The default seeds 2026–2035 reproduce the canonical archives byte-for-byte.

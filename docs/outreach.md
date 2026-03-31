# When Clocks Disagree: Noise, Signal, and the Value of Anomalies

Modern timekeeping no longer relies on a single clock. Instead, time is defined by networks of clocks — devices distributed across laboratories and continents that continuously compare their readings and agree on a shared timescale. These clocks are extraordinarily precise. The best optical clocks now reach fractional uncertainties below 10⁻¹⁸, sensitive enough to detect height differences of a few centimetres through gravitational time dilation.

But precision brings a new problem: clocks do not always agree.

Some disagreements are expected. Every clock has noise — small, random fluctuations in its frequency or phase. The standard response is to combine many clocks and reduce the influence of outliers, so that the average remains stable even if individual clocks occasionally misbehave. This approach works well when deviations are truly random.

The question explored in this project is simple:

**What if some disagreements are not just noise, but carry information — and by suppressing them, we throw that information away?**

---

## Measuring "surprise"

To explore this, we start by asking how unusual a clock's reading is compared to what it claims about its own uncertainty.

If a clock reports a value that should occur about once in a hundred independent measurements, that corresponds to about 6.6 bits of "surprise". More extreme deviations correspond to higher surprise.

We quantify this using a simple measure: for each clock reading, we compute how unlikely it is given the clock's reported uncertainty. The result is a number that increases as the reading becomes more unexpected.

This gives us a way to compare clocks on a common, uncertainty-normalised scale: not by how far they deviate in absolute terms, but by how inconsistent they are with their own stated noise.

IC is model-free at the signal level, but relies on the clock's own uncertainty estimate as a reference.

---

## Two kinds of bad behaviour

Not all surprising behaviour is the same.

- **Random surprises** occur when noise occasionally produces an unusually large deviation. These events are isolated and do not persist over time.
- **Structured surprises** occur when deviations follow a pattern: a drift, a correlation, or a sequence of changes that cannot be explained by independent random fluctuations alone.

For example, a clock whose frequency drifts steadily over several hours produces a sequence of correlated surprises — a structured deviation — whereas isolated large deviations with no persistence are consistent with random noise.

The distinction matters. Random surprises are precisely what robust averaging methods are designed to suppress. Structured surprises, however, may indicate something systematic — either in the clock itself or in the environment.

In this project, we explicitly separate these two cases. Instead of discarding all surprising data, we ask whether the surprise shows temporal structure. If it does, the corresponding clock is tracked separately rather than simply downweighted.

---

## What we have done so far

The first step is to ensure that the "surprise" measure behaves sensibly.

We tested it across ten different noise models, including Gaussian noise, heavy-tailed distributions, and temporally correlated processes. The goal was to verify that the measure is stable under a range of realistic conditions.

Under correctly specified uncertainties, the measure is consistent across these scenarios, with sample-size effects becoming negligible above roughly 75 data points.

However, one important limitation emerged. If all clocks systematically underestimate their own uncertainty — for example, by 20% — the measured surprise increases significantly (by about 19%). In other words, the method is sensitive to how well clocks report their own noise. This indicates sensitivity to the fidelity of declared uncertainties; the mitigation is procedural (conservative threshold calibration) rather than intrinsic.

This does not invalidate the approach, but it means that calibration matters. In practice, this sensitivity can be managed by adjusting thresholds conservatively, but it remains an important caveat.

---

## What comes next

So far, we have defined and tested the observable. The next step is to evaluate its usefulness at the network level.

We will simulate networks of clocks with realistic noise and failure modes, and compare two strategies:

- **Standard robust averaging**, which suppresses all outliers.
- **A classification-based approach**, which separates random from structured deviations and retains the latter as a distinct signal channel.

The key question is whether this second strategy improves the stability or interpretability of the resulting timescale.

---

## Why this matters now

For decades, treating anomalies as noise has been a successful strategy. But as clock precision improves, the nature of deviations changes.

At the level of 10⁻¹⁸, effects that were previously negligible — environmental influences, relativistic corrections, subtle correlations — become detectable. In this regime, not all deviations are equally uninformative.

Distinguishing between noise and structure is therefore no longer just a matter of robustness, but of information.

Whether this distinction can be used to improve timekeeping remains an open question. This project does not assume that it can. It aims to test the idea under controlled conditions, with explicit criteria for success and failure.

---

## Summary

Clock networks rely on agreement, but disagreement is unavoidable. The standard approach reduces the influence of anomalies to protect the average.

This project asks whether some anomalies should instead be preserved and interpreted. By measuring how surprising each clock's behaviour is — and whether that surprise has structure — we aim to distinguish noise from potentially informative deviations.

The observable is now defined and calibrated. Its limitations are known. The next step is to test whether it leads to better decisions at the level of the network.

---

*Part of the [ADM-EC Clock Consensus](https://threehouse-plus-ec.github.io/admec-clock-consensus/) project.*
*Author: Ulrich Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg.*

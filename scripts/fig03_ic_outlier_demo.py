"""
Generate fig03: IC outlier detection demo.

Panel (a): 40 Gaussian points with two injected outliers (6.0 and -5.5).
Panel (b): IC per point — outliers have the highest IC values.
           95th percentile threshold shown as dashed line.

Saves: logbook/figures/fig03_ic_outlier_demo.png
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ic import compute_ic

# Generate data
rng = np.random.default_rng(2026)
n = 40
values = rng.normal(0, 1, n)

# Inject two outliers
outlier_indices = [35, 37]
values[35] = 6.0
values[37] = -5.5
sigmas = np.ones(n)

# Compute IC
ic = compute_ic(values, sigmas)
threshold_95 = np.percentile(ic, 95)

# --- Figure ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# Panel (a): Data
markerline, stemlines, baseline = ax1.stem(range(n), values, linefmt='b-',
                                            markerfmt='bo', basefmt='gray')
plt.setp(stemlines, linewidth=1)
plt.setp(markerline, markersize=5)
# Annotate outliers
for idx in outlier_indices:
    ax1.annotate('outlier', xy=(idx, values[idx]),
                 xytext=(idx + 0.5, values[idx] + (0.5 if values[idx] > 0 else -0.5)),
                 fontsize=9, color='red', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='red', lw=1))
ax1.set_ylabel('Value')
ax1.set_title('(a)  Data with two outliers')
ax1.axhline(0, color='gray', linewidth=0.5)

# Panel (b): IC per point
markerline, stemlines, baseline = ax2.stem(range(n), ic, linefmt='-',
                                            markerfmt='o', basefmt='gray')
plt.setp(stemlines, color='darkorange', linewidth=1)
plt.setp(markerline, color='darkorange', markersize=5)
ax2.axhline(threshold_95, color='gray', linestyle='--', linewidth=1,
            label='95th percentile')
ax2.set_xlabel('Point index')
ax2.set_ylabel('IC (bits)')
ax2.set_title('(b)  Information Content per point')
ax2.legend(fontsize=8)

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), '..', 'logbook', 'figures',
                         'fig03_ic_outlier_demo.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

"""Manuscript figure: pre-registered decision-gate structure and verdicts.

Compact at-a-glance legend for the four pre-registered gates (DG-1, DG-2,
DG-2b, DG-3) and their verdicts in the present technical report. Intended
as a reading aid so the DG-* labels in the manuscript can be parsed
without flipping back to docs/projektantrag.md.

Saves docs/manuscript_files/fig_gate_verdicts.png.
"""

import os
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


GATES = [
    {
        "id": "DG-1",
        "title": "IC observable calibration",
        "criterion": ("Per-reading IC threshold passes null-FPR + cross-N + "
                      "worst-case-σ checks."),
        "verdict": "CLOSED\n(mitigated)",
        "verdict_color": "#f0c040",
        "verdict_text_color": "#222",
        "note": ("Threshold 2.976 bit; one sub-criterion mitigated by "
                 "worst-case recalibration (logbook entries 002, 006)."),
    },
    {
        "id": "DG-2",
        "title": "ADMEC vs non-ADMEC baselines (S1, S3)",
        "criterion": ("admec_full beats best non-ADMEC baseline on ≥ 2 of 3 "
                      "metrics on both S1 and S3, and beats admec_delay."),
        "verdict": "NOT MET",
        "verdict_color": "#d04040",
        "verdict_text_color": "white",
        "note": ("0/3 on S1 and 0/3 on S3 at the pre-registered threshold "
                 "(§ 3.2). Wins only on the dense control S2."),
    },
    {
        "id": "DG-2b",
        "title": "Strict-STRUCTURED true-positive rate",
        "criterion": ("Strict-STRUCTURED TPR ≥ 70 % against designer-injected "
                      "ground truth."),
        "verdict": "NOT MET",
        "verdict_color": "#d04040",
        "verdict_text_color": "white",
        "note": ("Aggregate strict TPR ≈ 0.7 %; S8 (fold bifurcation) "
                 "registers exactly 0.0 % across every (seed, post-onset) "
                 "cell (§ 3.3)."),
    },
    {
        "id": "DG-3",
        "title": "Constraint stack + three-way classifier",
        "criterion": ("Each constraint layer adds ≥ 10 % on at least one "
                      "metric, AND three-way > two-way."),
        "verdict": "NOT MET\n(structurally\nunreachable)",
        "verdict_color": "#a01818",
        "verdict_text_color": "white",
        "note": ("Three-way / two-way produces zero delta across 360 cells: "
                 "the consensus rule reads only the binary STABLE mask "
                 "(§ 4.3, § 5.3)."),
    },
]


def _wrap(text, width):
    return "\n".join(textwrap.wrap(text, width=width))


def main():
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97, "Pre-registered decision gates and verdicts",
            ha="center", va="top", fontsize=14, fontweight="bold")
    ax.text(50, 92.5,
            "Pre-registration in docs/projektantrag.md; verdicts reported "
            "in §§ 3, 4 of the manuscript.",
            ha="center", va="top", fontsize=9.5, style="italic", color="#444")

    # Layout columns:
    #   ID box      x in [1.5, 12]
    #   Centre col  x in [14, 73]
    #   Verdict box x in [76, 98]
    row_top = 86
    row_height = 20
    centre_wrap_width = 72  # characters
    note_wrap_width = 78

    for i, gate in enumerate(GATES):
        y_top = row_top - i * row_height
        y_bot = y_top - row_height + 2

        # Gate ID box (left)
        ax.add_patch(FancyBboxPatch(
            (1.5, y_bot), 10.5, row_height - 2,
            boxstyle="round,pad=0.4",
            linewidth=1.0,
            edgecolor="#333",
            facecolor="#f4f4f4",
        ))
        ax.text(6.75, (y_top + y_bot) / 2, gate["id"],
                ha="center", va="center",
                fontsize=14, fontweight="bold")

        # Title (centre, top)
        ax.text(14, y_top - 2.3, gate["title"],
                ha="left", va="top",
                fontsize=11, fontweight="bold")

        # Criterion (centre, middle), wrapped
        criterion_wrapped = _wrap("Criterion: " + gate["criterion"],
                                  centre_wrap_width)
        ax.text(14, y_top - 6.6, criterion_wrapped,
                ha="left", va="top", fontsize=9.3, color="#222")

        # Note (centre, bottom), wrapped
        note_wrapped = _wrap(gate["note"], note_wrap_width)
        ax.text(14, y_top - 13.5, note_wrapped,
                ha="left", va="top", fontsize=8.6,
                color="#555", style="italic")

        # Verdict box (right)
        vbx, vby = 76, y_bot + (row_height - 2) / 2 - 5
        ax.add_patch(FancyBboxPatch(
            (vbx, vby), 22, 10,
            boxstyle="round,pad=0.5",
            linewidth=1.2,
            edgecolor="#222",
            facecolor=gate["verdict_color"],
            alpha=0.92,
        ))
        ax.text(vbx + 11, vby + 5, gate["verdict"],
                ha="center", va="center",
                fontsize=10.5, fontweight="bold",
                color=gate["verdict_text_color"])

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "manuscript_files")
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig_gate_verdicts.png")
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

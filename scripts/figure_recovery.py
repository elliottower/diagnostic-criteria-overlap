"""Figure 1: the numbers a report prints, and the table that follows from them.

The delirium comparison of DSM-IV against a strict reading of DSM-5. The article
prints five figures and no cross-classification, and exactly one integer table is
consistent with all five. Cells are shaded as in the same-kappa figure, so the two
share one colour code: patients both readings identify, each reading alone, and
neither.

Writes results/figure_recovery.json.
"""
from __future__ import annotations

import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from enum2x2 import recover

ROOT = pathlib.Path(__file__).resolve().parent.parent
INK, RULE, BOX = "#1b2a41", "#8c93a8", "#eef1f6"
BOTH, A_ONLY, B_ONLY, NEITHER = "#2f4b7c", "#f95d6a", "#ffa600", "#dfe4ec"
N, N_A, N_B, KAPPA, AGREE = 768, 158, 466, "0.29", "60"

# Four figures suffice: the sample size and both counts leave one degree of
# freedom, and one agreement statistic closes it. The article also prints a raw
# agreement, which is a consistency check rather than a further constraint.
PRINTED = [("Patients", f"{N}"), ("strict DSM-5 identifies", f"{N_A}"),
           ("permissive DSM-5 identifies", f"{N_B}"), ("Cohen's $\\kappa$", KAPPA)]


def main() -> None:
    got = [t.as_dict() for t in recover(n=N, n_a=N_A, n_b=N_B, kappa=KAPPA)]
    assert len(got) == 1, f"expected one table, got {len(got)}"
    t = got[0]

    fig = plt.figure(figsize=(7.2, 2.9))
    ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    ax.text(2, 92, "What the report prints", fontsize=10.5, color=INK, fontweight="bold")
    bh, gap = 14.0, 3.0
    for i, (label, value) in enumerate(PRINTED):
        y = 70 - i * (bh + gap)
        ax.add_patch(Rectangle((2, y), 33, bh, facecolor=BOX, edgecolor="none"))
        ax.text(4, y + bh / 2, label, fontsize=8.5, color="#40506b", va="center")
        ax.text(33, y + bh / 2, value, fontsize=10.5, color=INK, ha="right",
                va="center", fontweight="bold")

    ax.add_patch(FancyArrowPatch((37.5, 40), (49, 46), color=RULE, arrowstyle="-|>",
                                 mutation_scale=13, linewidth=1.5,
                                 connectionstyle="arc3,rad=-0.18"))

    ax.text(53, 92, "The table they determine", fontsize=10.5, color=INK, fontweight="bold")
    cx, cy, w, h = 66, 14, 16, 24
    ax.text(cx + w / 2, cy + 2 * h + 4, "permissive +", fontsize=8.5, ha="center", color="#555555")
    ax.text(cx + 1.5 * w, cy + 2 * h + 4, "permissive $-$", fontsize=8.5, ha="center", color="#555555")
    ax.text(cx - 2, cy + 1.5 * h, "strict +", fontsize=8.5, ha="right", va="center", color="#555555")
    ax.text(cx - 2, cy + 0.5 * h, "strict $-$", fontsize=8.5, ha="right", va="center", color="#555555")

    grid = [((0, 1), t["n11"], BOTH, "white"), ((1, 1), t["n10"], A_ONLY, "white"),
            ((0, 0), t["n01"], B_ONLY, "white"), ((1, 0), t["n00"], NEITHER, INK)]
    for (col, row), val, face, fg in grid:
        ax.add_patch(Rectangle((cx + col * w, cy + row * h), w, h,
                               facecolor=face, edgecolor="white", linewidth=1.6))
        ax.text(cx + (col + 0.5) * w, cy + (row + 0.5) * h, f"{val:,}",
                ha="center", va="center", fontsize=15, color=fg, fontweight="bold")


    for ext in ("pdf", "png"):
        fig.savefig(ROOT / f"figures/recovery.{ext}", dpi=200, bbox_inches="tight", pad_inches=0.03)
    json.dump({"published": {"N": N, "n_A": N_A, "n_B": N_B, "kappa": KAPPA,
                             "agreement_percent": AGREE}, "recovered": t, "tables": len(got)},
              open(ROOT / "results/figure_recovery.json", "w"), indent=2)
    print(f"  five printed figures -> {len(got)} table: {t}")


if __name__ == "__main__":
    main()

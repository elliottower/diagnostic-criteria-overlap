"""Figure 2: one table, four published readings.

Every value is computed from the cells in results/recovery.json, so the figure cannot
disagree with the recovered table. Writes results/figure_one_table.json.
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = pathlib.Path(__file__).resolve().parent.parent
INK, RULE, BOX = "#1b2a41", "#8c93a8", "#eef1f6"


def readings(n11: int, n10: int, n01: int, n00: int) -> list[tuple[str, str, str]]:
    n = n11 + n10 + n01 + n00
    po = Fraction(n11 + n00, n)
    pe = Fraction((n11 + n10) * (n11 + n01) + (n01 + n00) * (n10 + n00), n * n)
    kappa = (po - pe) / (1 - pe)
    return [
        ("Overall accuracy", f"{100 * float(po):.1f}%", True,
         "counts every patient the two rules place alike,\nincluding the ones neither identifies"),
        ("Sensitivity", f"{100 * n11 / (n11 + n10):.1f}%", True,
         "treats the neurologist as the standard and\ncharges the shortfall to the protocol"),
        ("Cohen's $\\kappa$", f"{float(kappa):.2f}", False,
         "treats neither rule as correct and corrects\nfor agreement expected by chance"),
        ("Jaccard similarity", f"{100 * n11 / (n11 + n10 + n01):.1f}%", False,
         "counts only the patients at least one rule\nidentifies, and asks how far the two overlap"),
    ]


def main() -> None:
    recs = {r["key"]: r for r in json.load(open(ROOT / "results/recovery.json"))["results"]}
    rec = recs["guerra2026"]
    c = rec["self_test"]["published_cells"]
    n11, n10, n01, n00 = c["n11"], c["n10"], c["n01"], c["n00"]
    rows = readings(n11, n10, n01, n00)

    fig = plt.figure(figsize=(7.2, 3.7))
    ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    # The table.
    ax.text(4, 92, "One table", fontsize=11, color=INK, fontweight="bold")
    ax.text(4, 86.5, f"N = {rec['N']:,}", fontsize=8.5, color="#555555")
    cx, cy, w, h = 15, 50, 9, 11
    ax.text(cx + w, cy + 2 * h + 3, "Protocol +", fontsize=8, ha="center", color="#555555")
    ax.text(cx + 2 * w, cy + 2 * h + 3, "Protocol $-$", fontsize=8, ha="center", color="#555555")
    ax.text(cx - 1.0, cy + h + h / 2, "Neurologist +", fontsize=8, ha="right", va="center", color="#555555")
    ax.text(cx - 1.0, cy + h / 2, "Neurologist $-$", fontsize=8, ha="right", va="center", color="#555555")
    for j, (col, val) in enumerate([(0, n11), (1, n10)]):
        ax.add_patch(Rectangle((cx + w / 2 + col * w, cy + h), w, h, facecolor="white", edgecolor=RULE))
        ax.text(cx + w + col * w, cy + h + h / 2, f"{val:,}", ha="center", va="center", fontsize=10, color=INK)
    for j, (col, val) in enumerate([(0, n01), (1, n00)]):
        ax.add_patch(Rectangle((cx + w / 2 + col * w, cy), w, h, facecolor="white", edgecolor=RULE))
        ax.text(cx + w + col * w, cy + h / 2, f"{val:,}", ha="center", va="center", fontsize=10, color=INK)

    # The readings.
    ax.text(46, 92, "Four readings", fontsize=11, color=INK, fontweight="bold")
    top, gap, bh = 82, 1.5, 17.5
    for i, (name, value, printed, note) in enumerate(rows):
        y = top - i * (bh + gap) - bh
        ax.add_patch(Rectangle((46, y), 51, bh, facecolor=BOX, edgecolor="none"))
        ax.text(48, y + bh - 5.5, name, fontsize=9, color=INK, fontweight="bold")
        ax.text(95, y + bh - 5.5, value, fontsize=11, color=INK, ha="right", fontweight="bold")
        ax.text(48, y + 4.5, note, fontsize=7.4, color="#40506b", va="center", linespacing=1.35)
        ax.add_patch(FancyArrowPatch((39, 56), (45.4, y + bh / 2), color=RULE,
                                     arrowstyle="-|>", mutation_scale=9,
                                     connectionstyle="arc3,rad=0.16", linewidth=0.8))

    ax.text(4, 42, "The source prints the four cells and\nthe first two readings. It prints no\n"
                   "agreement coefficient, but $\\kappa$ and\nthe Jaccard similarity can be computed\n"
                   "from those cells.",
            fontsize=7.4, color="#40506b", linespacing=1.6, va="top")

    for ext in ("pdf", "png"):
        fig.savefig(ROOT / f"figures/one_table.{ext}", dpi=200,
                    bbox_inches="tight", pad_inches=0.02)
    json.dump({"cells": c, "N": rec["N"],
               "readings": [{"name": n.replace("$\\kappa$", "kappa"), "value": v, "printed_by_source": pr}
                            for n, v, pr, _ in rows]},
              open(ROOT / "results/figure_one_table.json", "w"), indent=2)
    print(json.dumps([(n, v, pr) for n, v, pr, _ in rows], indent=2))


if __name__ == "__main__":
    main()

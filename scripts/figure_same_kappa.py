"""Figure 1: two comparisons at kappa = 0.22 with opposite structure.

Cells and kappa/kappa_max are read from results/recovery.json, never retyped, so the
figure cannot drift from the recovered tables. Writes the numbers it drew to
results/figure_same_kappa.json alongside the image.
"""
from __future__ import annotations

import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
PANELS = [
    ("meagher2014_strict", "Delirium", "DSM-IV", "strict DSM-5"),
    ("guerra2026", "Multiple sclerosis", "Neurologist", "Trial protocol"),
]
BOTH, A_ONLY, B_ONLY = "#2f4b7c", "#f95d6a", "#ffa600"


def cells_of(rec: dict) -> dict[str, int]:
    """Point cells where the recovery is unique, published cells where it is a set."""
    if rec["status"] == "unique":
        return {k: v["min"] for k, v in rec["cell_ranges"].items()}
    return rec["self_test"]["published_cells"]


def main() -> None:
    recs = {r["key"]: r for r in json.load(open(ROOT / "results/recovery.json"))["results"]}
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 3.9))
    drawn = {}

    for ax, (key, condition, name_a, name_b) in zip(axes, PANELS):
        rec = recs[key]
        c = cells_of(rec)
        union = c["n11"] + c["n10"] + c["n01"]
        seg = [(c["n10"], A_ONLY, f"{name_a} only"),
               (c["n11"], BOTH, "both"),
               (c["n01"], B_ONLY, f"{name_b} only")]
        left = 0.0
        for count, colour, label in seg:
            frac = 100 * count / union
            ax.barh(0, frac, left=left, height=0.5, color=colour, edgecolor="white", linewidth=1.2)
            if frac > 6:
                ax.text(left + frac / 2, 0, f"{count:,}\n{frac:.1f}%", ha="center", va="center",
                        color="white", fontsize=8.5, linespacing=1.25)
            else:
                # A segment too thin to label is the one the reader most needs named.
                ax.annotate(f"{count:,}  ({frac:.1f}%)", xy=(left + frac / 2, 0.25),
                            xytext=(left + frac / 2, 0.62), ha="center", fontsize=8.5,
                            color=colour, fontweight="bold",
                            arrowprops=dict(arrowstyle="-", color=colour, linewidth=1))
            left += frac

        kkm = rec["kappa_over_kappa_max"]["min"]
        ax.set_xlim(0, 100); ax.set_ylim(-0.6, 0.95); ax.axis("off")
        ax.set_title(
            f"{condition}   {name_a} vs {name_b}\n"
            f"$\\kappa$ = 0.22    $\\kappa/\\kappa_{{max}}$ = {kkm:.2f}    "
            f"union = {union:,} of N = {rec['N']:,}",
            fontsize=9.5, loc="left", pad=6)
        ax.text(0, -0.45, "   ".join(f"{k} = {v:,}" for k, v in c.items()),
                fontsize=8, color="#444444", family="monospace")
        drawn[key] = {"cells": c, "union": union, "kappa_over_kappa_max": kkm,
                      "status": rec["status"], "N": rec["N"]}

    handles = [plt.Rectangle((0, 0), 1, 1, color=col) for col in (A_ONLY, BOTH, B_ONLY)]
    fig.legend(handles, ["identified by the first rule alone", "identified by both",
                         "identified by the second rule alone"],
               loc="lower center", ncol=3, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.08, 1, 0.99), h_pad=2.2)

    (ROOT / "figures").mkdir(exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(ROOT / f"figures/same_kappa.{ext}", dpi=200,
                    bbox_inches="tight", pad_inches=0.02)
    json.dump(drawn, open(ROOT / "results/figure_same_kappa.json", "w"), indent=2)
    print(json.dumps(drawn, indent=2))


if __name__ == "__main__":
    main()

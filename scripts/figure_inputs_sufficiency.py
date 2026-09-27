"""Do the figures a display shows determine the table the display draws?

Each figure in the paper prints a short list of published quantities on the left
and one integer table on the right. The caption asserts that the list determines
the table, so the assertion has to be checked against the same enumeration the
corpus analysis runs, using only the quantities the figure actually displays.
A source may publish more than a figure shows; a figure claiming determination
from four numbers is wrong if the fourth is doing no work and the fifth is.

Inputs: the displayed quantities, transcribed here from the figure sources in
figures/, together with the corpus row each comes from.
Output: results/figure_inputs_sufficiency.json
"""
from __future__ import annotations

import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS = PROJECT_ROOT / "results" / "figure_inputs_sufficiency.json"

_SIBLING = PROJECT_ROOT.parent / "enum2x2" / "src"
if _SIBLING.is_dir():
    sys.path.insert(0, str(_SIBLING))
from enum2x2 import recover  # noqa: E402

# Quantities each figure displays, and the cells it draws. Transcribed from the
# TikZ sources so that a change to a figure that is not carried through here
# shows up as a mismatch rather than passing silently.
DISPLAYS = [
    {
        "figure": "figures/fig_recovery.tex",
        "corpus_row": "meagher2014_reading",
        "source": "meagher2014",
        "displayed": {"n": 768, "n_a": 158, "n_b": 466, "kappa": "0.29"},
        "also_published": {"agreement": "60", "agreement_as_percent": True},
        "drawn_cells": {"n11": 158, "n10": 0, "n01": 308, "n00": 302},
    },
    {
        "figure": "figures/fig_two_cases.tex (upper)",
        "corpus_row": "goyal2025 CDA 2013 / JSOG 1984",
        "source": "goyal2025",
        "displayed": {"n": 353, "n_a": 62, "n_b": 28, "kappa": "0.576"},
        "also_published": {},
        "drawn_cells": {"n11": 28, "n10": 34, "n01": 0, "n00": 291},
    },
    {
        "figure": "figures/fig_two_cases.tex (lower)",
        "corpus_row": "goyal2025 IADPSG 2010 / NICE 2015",
        "source": "goyal2025",
        "displayed": {"n": 353, "n_a": 84, "n_b": 76, "kappa": "0.580"},
        "also_published": {},
        "drawn_cells": {"n11": 54, "n10": 30, "n01": 22, "n00": 247},
    },
]


def candidates(call: dict) -> list[dict]:
    return [t.as_dict() for t in recover(**call)]


def main() -> int:
    rows = []
    for d in DISPLAYS:
        shown = candidates(d["displayed"])
        full = candidates({**d["displayed"], **d["also_published"]})
        rows.append({
            "figure": d["figure"],
            "corpus_row": d["corpus_row"],
            "source": d["source"],
            "displayed": d["displayed"],
            "n_displayed_quantities": len(d["displayed"]),
            "candidates_from_displayed": len(shown),
            "candidates_from_everything_published": len(full),
            "drawn_cells": d["drawn_cells"],
            "drawn_cells_are_the_unique_candidate":
                len(shown) == 1 and shown[0] == d["drawn_cells"],
            "unpublished_quantities_change_nothing": len(shown) == len(full),
        })

    report = {
        "question": ("does the list of quantities each figure displays determine "
                     "the table that figure draws?"),
        "enumeration": "enum2x2.recover, the same routine scripts/recover_tables.py calls",
        "displays": rows,
        "all_displays_determine_their_table":
            all(r["drawn_cells_are_the_unique_candidate"] for r in rows),
    }
    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps(report, indent=2) + "\n")

    for r in rows:
        print(f"  {r['figure']:40s} {r['n_displayed_quantities']} shown -> "
              f"{r['candidates_from_displayed']} candidate(s), "
              f"drawn table unique: {r['drawn_cells_are_the_unique_candidate']}")
    print(f"  written to {RESULTS.relative_to(PROJECT_ROOT)}")
    return 0 if report["all_displays_determine_their_table"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

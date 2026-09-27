"""Do the numbers drawn in each figure sum to the marginals their labels claim?

A transposed panel passes every check that compares a set of four cell values,
because the values are right and only their positions are wrong. This reads the
TikZ sources, works out which cell each number is drawn in from its coordinates,
reads the row and column labels off the header nodes, and adds them up.

Output: results/figure_margins_check.json
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "figure_margins_check.json"

# figure -> {node prefix: (row label -> expected positive count, col label -> count)}
EXPECTED = {
    "fig_recovery.tex": [
        {"cells": "c", "row_positive": ("strict", 158), "col_positive": ("relaxed", 466),
         "n": 768, "source": "meagher2014_reading"},
    ],
    "fig_two_cases.tex": [
        {"cells": "a", "row_positive": ("CDA", 62), "col_positive": ("JSOG", 28),
         "n": 353, "source": "goyal2025 CDA 2013 / JSOG 1984"},
        {"cells": "b", "row_positive": ("IADPSG", 84), "col_positive": ("NICE", 76),
         "n": 353, "source": "goyal2025 IADPSG 2010 / NICE 2015"},
    ],
    "fig_four_readings.tex": [
        {"cells": "c", "row_positive": ("neurologist", 866), "col_positive": ("protocol", 1603),
         "n": 20306, "source": "guerra2026"},
    ],
}

NODE = re.compile(r"\\node\[(?:key)?cell\]\s*\((\w+)\)\s*at\s*\(([-\d.]+),([-\d.]+)\)\s*\{(.+?)\};")


def grid(tex: str, prefix: str) -> dict:
    """Map each drawn number to its (row, column) by coordinate, not by node name."""
    found = [(n, float(x), float(y), v) for n, x, y, v in NODE.findall(tex)
             if n.startswith(prefix)]
    if len(found) != 4:
        return {}
    xs = sorted({x for _, x, _, _ in found})
    ys = sorted({y for _, _, y, _ in found}, reverse=True)   # top row first
    cell = {}
    for name, x, y, v in found:
        val = int(v.replace("{,}", "").replace(",", ""))
        cell[(ys.index(y), xs.index(x))] = {"node": name, "value": val}
    return cell


def main() -> int:
    rows, ok = [], True
    for fname, panels in EXPECTED.items():
        tex = (ROOT / "figures" / fname).read_text()
        for spec in panels:
            g = grid(tex, spec["cells"])
            if len(g) != 4:
                rows.append({"figure": fname, "panel": spec["cells"],
                             "error": "did not find four cell nodes"})
                ok = False
                continue
            row_pos = g[(0, 0)]["value"] + g[(0, 1)]["value"]   # top row
            col_pos = g[(0, 0)]["value"] + g[(1, 0)]["value"]   # left column
            total = sum(c["value"] for c in g.values())
            rlab, rexp = spec["row_positive"]
            clab, cexp = spec["col_positive"]
            entry = {
                "figure": fname, "panel": spec["cells"], "source": spec["source"],
                "drawn": {f"{k}": v["value"] for k, v in sorted(g.items())},
                "top_row_sum": row_pos, f"{rlab}_positive_published": rexp,
                "left_column_sum": col_pos, f"{clab}_positive_published": cexp,
                "total": total, "n_published": spec["n"],
                "row_marginal_ok": row_pos == rexp,
                "column_marginal_ok": col_pos == cexp,
                "total_ok": total == spec["n"],
            }
            entry["ok"] = all((entry["row_marginal_ok"], entry["column_marginal_ok"],
                               entry["total_ok"]))
            ok = ok and entry["ok"]
            rows.append(entry)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"panels": rows, "all_panels_consistent": ok}, indent=2) + "\n")
    for r in rows:
        if "error" in r:
            print(f"  FAIL {r['figure']:24s} panel {r['panel']}  {r['error']}")
            continue
        rlab = [k for k in r if k.endswith("_positive_published")][0]
        clab = [k for k in r if k.endswith("_positive_published")][1]
        print(f"  {'ok  ' if r['ok'] else 'FAIL'} {r['figure']:22s} panel {r['panel']}: "
              f"{rlab.split('_')[0]} row {r['top_row_sum']} vs {r[rlab]} published, "
              f"{clab.split('_')[0]} col {r['left_column_sum']} vs {r[clab]} published, "
              f"total {r['total']}/{r['n_published']}")
    print(f"  all panels consistent: {ok}")
    print(f"  written to {OUT.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

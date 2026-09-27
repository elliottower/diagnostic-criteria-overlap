"""What kappa/kappa_max measures, in cells.

For a 2x2 table with positive counts n_A and n_B, the published counts fix the
difference between the two disagreement cells, n_10 - n_01 = n_A - n_B. What a
recovered table adds is the smaller of the two cells. This checks, on every
recovered table, that kappa/kappa_max equals one minus that smaller cell divided by
the value chance alone would put in it, so the ratio is 1 exactly when the smaller
cell is empty and 0 when it is as full as independence predicts.

Output: results/kappa_max_smaller_cell.json
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "kappa_max_smaller_cell.json"


def analyse(label: str, a: int, b: int, c: int, d: int) -> dict:
    n = a + b + c + d
    n_a, n_b = a + b, a + c
    po = Fraction(a + d, n)
    pa, pb = Fraction(n_a, n), Fraction(n_b, n)
    pe = pa * pb + (1 - pa) * (1 - pb)
    pom = min(pa, pb) + min(1 - pa, 1 - pb)
    ratio = (po - pe) / (pom - pe)
    if n_a >= n_b:
        smaller, expected = c, Fraction((n - n_a) * n_b, n)
    else:
        smaller, expected = b, Fraction(n_a * (n - n_b), n)
    identity = 1 - Fraction(smaller, 1) / expected
    return {"comparison": label, "cells": [a, b, c, d],
            "difference_fixed_by_printed_counts": n_a - n_b,
            "smaller_disagreement_cell": smaller,
            "chance_expectation_for_that_cell": float(expected),
            "kappa_over_kappa_max": float(ratio),
            "one_minus_smaller_over_expected": float(identity),
            "identity_holds_exactly": ratio == identity}


def main() -> None:
    rows = []
    rec = json.loads((ROOT / "results/recovery.json").read_text())["results"]
    for r in rec:
        c = r.get("table") or (r.get("self_test") or {}).get("published_cells")
        if c:
            rows.append(analyse(r["key"], c["n11"], c["n10"], c["n01"], c["n00"]))
    goyal = json.loads((ROOT / "results/goyal_all_pairs.json").read_text())
    for r in goyal["rows"]:
        c = r["cells"]
        rows.append(analyse(f"goyal2025 {r['a']} / {r['b']}", c["n11"], c["n10"], c["n01"], c["n00"]))
    report = {"identity": "kappa/kappa_max = 1 - smaller disagreement cell / its expectation under independence",
              "tables_checked": len(rows),
              "identity_holds_exactly_in": sum(x["identity_holds_exactly"] for x in rows),
              "rows": rows}
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"  identity holds exactly in {report['identity_holds_exactly_in']} of {len(rows)} tables")
    for x in rows[:9]:
        print(f"  {x['comparison']:24s} smaller cell {x['smaller_disagreement_cell']:>5}  "
              f"chance {x['chance_expectation_for_that_cell']:8.1f}  ratio {x['kappa_over_kappa_max']:.3f}  "
              f"difference fixed by counts {x['difference_fixed_by_printed_counts']:+d}")
    print(f"  written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

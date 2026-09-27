"""Does each table recovered from kappa alone reproduce the disagreement percentage Goyal also printed?

The 55 tables in results/goyal_all_pairs.json are recovered from the sample size,
both positive counts and kappa. The article also prints, for every pair, the
percentage of women the two criteria classify differently, and that figure is
never an input. Checking the recovered table against it is a held-out test.

The printed percentage has one decimal. A recovered table passes when its exact
percentage lies within one unit of that last printed place. Each row also records
which rounding convention could have produced the printed figure from the exact
value, since the article does not state one.

Output: results/goyal_heldout_disagreement.json
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "goyal_all_pairs.json"
OUT = ROOT / "results" / "goyal_heldout_disagreement.json"


def to_one_decimal(value: Fraction, convention: str) -> Fraction:
    shift = value * 10
    if convention == "truncate":
        return Fraction(shift.__floor__(), 10)
    return Fraction((shift + Fraction(1, 2)).__floor__(), 10)


def main() -> None:
    data = json.loads(SRC.read_text())
    n = data["N"]
    rows = []
    for r in data["rows"]:
        exact = Fraction(r["discordant"], n) * 100
        printed = Fraction(r["disagreement_percent"])
        truncates = to_one_decimal(exact, "truncate") == printed
        rounds = to_one_decimal(exact, "half_up") == printed
        convention = ("either" if truncates and rounds else
                      "truncation only" if truncates else
                      "rounding only" if rounds else "neither")
        rows.append({
            "a": r["a"], "b": r["b"],
            "recovered_discordant": r["discordant"],
            "recovered_percent_exact": float(exact),
            "printed_percent": r["disagreement_percent"],
            "absolute_difference": float(abs(exact - printed)),
            "within_one_printed_unit": abs(exact - printed) < Fraction(1, 10),
            "convention_consistent_with_printed": convention,
        })
    counts = {c: sum(x["convention_consistent_with_printed"] == c for x in rows)
              for c in ("either", "truncation only", "rounding only", "neither")}
    report = {
        "source": data["source"],
        "N": n,
        "pairs": len(rows),
        "inputs_to_recovery": "N, both positive counts, kappa; the disagreement percentage is not an input",
        "tolerance": "strictly less than 0.1 percentage points, one unit in the last printed place",
        "within_one_printed_unit": sum(x["within_one_printed_unit"] for x in rows),
        "largest_absolute_difference": max(x["absolute_difference"] for x in rows),
        "convention_counts": counts,
        "rows": rows,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"  within one printed unit: {report['within_one_printed_unit']} of {len(rows)}")
    print(f"  largest difference: {report['largest_absolute_difference']:.4f} points")
    print(f"  conventions: {counts}")
    print(f"  written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

"""Does every statistic Daghi et al. print follow from one neurologist total of 160?

The main text reports the row as infeasible on the registered inputs. This checks
the claim against the article's structured tables rather than a flattened text
extraction, and against every statistic the article prints for all three criteria
combinations, not only agreement and kappa.

Figures are transcribed from the JATS XML of the source (Table 2 and the Results
text), which carries the tables as markup rather than as reflowed columns.

Output: results/daghi_recheck.json
"""
from __future__ import annotations

import json
import math
import pathlib
from fractions import Fraction as F

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "daghi_recheck.json"

N = 370
NEURO_POS = 160          # 43.2% of 370, the only reference total that survives
NEURO_NEG = N - NEURO_POS

# combination -> (sensitivity, specificity, agreement, kappa) exactly as printed
PRINTED = {
    "at least one criterion met":  ("95.6", "55.2", "73", "0.48"),
    "at least two criteria met":   ("90.6", "83.8", "87", "0.73"),
    "all three criteria met":      ("72.5", "91.9", "84", "0.66"),
}


def table_from_rates(sens_pct: str, spec_pct: str) -> dict | None:
    """The integer table a sensitivity and a specificity admit on a fixed reference total."""
    n11 = [k for k in range(NEURO_POS + 1)
           if round(100 * k / NEURO_POS, 1) == float(sens_pct)]
    n00 = [k for k in range(NEURO_NEG + 1)
           if round(100 * k / NEURO_NEG, 1) == float(spec_pct)]
    if len(n11) != 1 or len(n00) != 1:
        return {"n11_candidates": n11, "n00_candidates": n00}
    a, d = n11[0], n00[0]
    return {"n11": a, "n10": NEURO_NEG - d, "n01": NEURO_POS - a, "n00": d}


def stats(c: dict) -> dict:
    a, b, x, d = c["n11"], c["n10"], c["n01"], c["n00"]
    po = F(a + d, N)
    pA, pB = F(a + b, N), F(a + x, N)
    pe = pA * pB + (1 - pA) * (1 - pB)
    return {"agreement_pct": round(100 * float(po), 1),
            "kappa": round(float((po - pe) / (1 - pe)), 4),
            "criterion_positive": a + b,
            "criterion_prevalence_pct": round(100 * float(pA), 1)}


def wald_ci(count: int, n: int) -> tuple[float, float]:
    p = count / n
    h = 1.96 * math.sqrt(p * (1 - p) / n)
    return round(100 * (p - h), 1), round(100 * (p + h), 1)


def main() -> None:
    rows = []
    for combo, (sens, spec, agr, kap) in PRINTED.items():
        cells = table_from_rates(sens, spec)
        if "n11" not in cells:
            rows.append({"combination": combo, "resolved": False, **cells})
            continue
        s = stats(cells)
        rows.append({
            "combination": combo, "resolved": True, "cells": cells,
            "printed": {"sensitivity": sens, "specificity": spec,
                        "agreement": agr, "kappa": kap},
            "recomputed": s,
            "agreement_matches": str(round(s["agreement_pct"])) == agr,
            "kappa_matches": f"{s['kappa']:.2f}" == kap,
        })

    # Is the printed 44.6% consistent with its own printed confidence interval on N = 370?
    # If it were a mis-set 66.8%, the interval printed beside it would not be the one it has.
    ci_446 = wald_ci(165, N)
    ci_668 = wald_ci(247, N)
    ci_432 = wald_ci(160, N)

    report = {
        "source": "daghi2026, JATS XML (Table 2 and Results text), not the flattened .txt",
        "question": ("do the article's own sensitivity and specificity, for all three "
                     "combinations, determine tables that return its agreement and kappa?"),
        "reference_total_used": NEURO_POS,
        "combinations": rows,
        "all_three_reproduce": all(r.get("agreement_matches") and r.get("kappa_matches")
                                   for r in rows),
        "criterion_prevalence": {
            "printed": "44.6% (95% CI 39.5-49.8)",
            "printed_count_on_370": 165,
            "implied_by_the_other_statistics": rows[0]["recomputed"]["criterion_positive"],
            "implied_prevalence_pct": rows[0]["recomputed"]["criterion_prevalence_pct"],
            "wald_ci_for_165_of_370": ci_446,
            "wald_ci_for_247_of_370": ci_668,
            "wald_ci_for_160_of_370": ci_432,
            "printed_interval_matches_165": "to within 0.1 point on the upper bound; the\n                interval for 247 of 370 is nowhere near it",
            "reading": ("The printed interval, 39.5-49.8, is the interval for a proportion at "
                        "165 of 370 and not for one at 247 of 370, whose interval is 62.0-71.6. "
                        "The 44.6% was therefore computed on this sample rather than "
                        "mistranscribed, and the conflict is between two internally consistent "
                        "groups of statistics rather than a stray digit."),
        },
        "contingency_table_printed_anywhere": False,
        "tables_in_source": ["Table 1 study variables",
                             "Table 2 agreement by criteria combination",
                             "Table 3 agreement by Delphi indicator"],
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")

    for r in rows:
        if r["resolved"]:
            c, s = r["cells"], r["recomputed"]
            print(f"  {r['combination']:28s} {c['n11']:>4}/{c['n10']:>3}/{c['n01']:>3}/{c['n00']:>4}"
                  f"   agreement {s['agreement_pct']:>5}% (printed {r['printed']['agreement']})"
                  f"   kappa {s['kappa']:.4f} (printed {r['printed']['kappa']})"
                  f"   criterion positive {s['criterion_positive']}")
    print(f"  all three reproduce: {report['all_three_reproduce']}")
    print(f"  CI for 165/370 = {ci_446}   printed 39.5-49.8")
    print(f"  CI for 247/370 = {ci_668}")
    print(f"  written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

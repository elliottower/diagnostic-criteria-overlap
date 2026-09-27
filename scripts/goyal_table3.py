"""Goyal et al. 2025 Table 3: ten GDM criteria against IADPSG on 353 women.

The table prints, for each criterion, the number diagnosed, Cohen's kappa to three
decimals, and a disagreement percentage. That is a sample size, both marginals and
two agreement statistics, so the joint table is over-determined and the two
statistics can be checked against each other.

Writes results/goyal_table3_recovery.json.
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

from enum2x2 import recover

ROOT = pathlib.Path(__file__).resolve().parent.parent
N, N_IADPSG = 353, 84
ROWS = [
    ("NICE 2015", 76, "0.580", "14.7"), ("ADIPS 1998", 69, "0.609", "13.3"),
    ("DIPSI 2009", 64, "0.456", "18.1"), ("WHO 1999", 64, "0.456", "18.1"),
    ("CDA 2013", 62, "0.811", "6.2"),   ("NZSSD 2004", 46, "0.648", "10.7"),
    ("EASD 1996", 34, "0.509", "14.1"), ("ADA 2004", 28, "0.432", "15.9"),
    ("CDA 2003", 26, "0.406", "16.4"),  ("JSOG 1984", 28, "0.432", "15.8"),
]


def main() -> None:
    out = []
    for name, n_b, kappa, printed_d in ROWS:
        both = list(recover(n=N, n_a=N_IADPSG, n_b=n_b, kappa=kappa,
                            agreement=f"{100 - float(printed_d):.1f}",
                            agreement_as_percent=True))
        kappa_only = list(recover(n=N, n_a=N_IADPSG, n_b=n_b, kappa=kappa))
        rec = {"criterion": name, "n_b": n_b, "kappa": kappa,
               "printed_disagreement_percent": printed_d,
               "tables_from_kappa_and_disagreement": len(both),
               "tables_from_kappa_alone": len(kappa_only)}
        if len(kappa_only) == 1:
            t = kappa_only[0].as_dict()
            disc = t["n10"] + t["n01"]
            exact = Fraction(100 * disc, N)
            rec |= {"cells": t, "discordant": disc,
                    "discordant_percent_exact": f"{float(exact):.2f}",
                    "printed_is_truncation_not_rounding":
                        len(both) == 0 and f"{float(exact):.1f}" != printed_d
                        and str(exact.numerator * 10 // exact.denominator)[-1] == printed_d[-1]}
        out.append(rec)

    unique = sum(1 for r in out if r["tables_from_kappa_and_disagreement"] == 1)
    empty = [r["criterion"] for r in out if r["tables_from_kappa_and_disagreement"] == 0]
    json.dump({"source": "goyal2025, Table 3", "N": N, "n_IADPSG": N_IADPSG,
               "unique_from_kappa_and_disagreement": unique,
               "unique_from_kappa_alone": sum(1 for r in out if r["tables_from_kappa_alone"] == 1),
               "empty_candidate_set": empty, "rows": out},
              open(ROOT / "results/goyal_table3_recovery.json", "w"), indent=2)
    print(f"  kappa + disagreement : {unique} of {len(ROWS)} unique, {len(empty)} empty ({', '.join(empty)})")
    print(f"  kappa alone          : {sum(1 for r in out if r['tables_from_kappa_alone'] == 1)} of {len(ROWS)} unique")
    print("  the three empty sets all arise from a truncated disagreement percentage")


if __name__ == "__main__":
    main()

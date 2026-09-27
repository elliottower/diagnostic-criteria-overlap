"""Goyal et al. 2025: all 55 pairwise comparisons of eleven GDM criteria on 353 women.

Table 3 gives each criterion's positive count. Figure 2 is a matrix image giving
Cohen's kappa and a disagreement percentage for every pair, transcribed here by
reading the figure. The ten IADPSG comparisons appear in both Table 3 and Figure 2,
so agreement between the two is a check on the transcription and is asserted below.

Writes results/goyal_all_pairs.json.
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

from enum2x2 import recover

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = 353

# Table 3: positive count per criterion.
POS = {"IADPSG 2010": 84, "NICE 2015": 76, "DIPSI 2009": 64, "WHO 1999": 64,
       "CDA 2013": 62, "ADIPS 1998": 69, "EASD 1996": 34, "NZSSD 2004": 46,
       "CDA 2003": 26, "ADA 2004": 28, "JSOG 1984": 28}
ORDER = ["IADPSG 2010", "NICE 2015", "DIPSI 2009", "WHO 1999", "CDA 2013",
         "ADIPS 1998", "EASD 1996", "NZSSD 2004", "CDA 2003", "ADA 2004", "JSOG 1984"]

# Figure 2, upper triangle, row by row: (kappa, disagreement percent).
FIG2 = {
 "IADPSG 2010": [("0.580","14.7"),("0.456","18.1"),("0.456","18.1"),("0.811","6.2"),
                 ("0.609","13.3"),("0.509","14.1"),("0.648","10.7"),("0.406","16.4"),
                 ("0.432","15.9"),("0.432","15.8")],
 "NICE 2015":   [("0.893","3.3"),("0.893","3.3"),("0.605","12.4"),("0.905","3.1"),
                 ("0.560","11.8"),("0.667","9.6"),("0.427","14.7"),("0.456","14.2"),
                 ("0.478","13.5")],
 "DIPSI 2009":  [("1.000","0"),("0.459","15.8"),("0.787","6.5"),("0.556","10.7"),
                 ("0.507","13.0"),("0.504","11.3"),("0.511","11.3"),("0.536","10.7")],
 "WHO 1999":    [("0.459","15.8"),("0.787","6.5"),("0.556","10.7"),("0.507","13.0"),
                 ("0.504","11.3"),("0.511","11.3"),("0.536","10.7")],
 "CDA 2013":    [("0.691","9.3"),("0.667","7.9"),("0.826","4.5"),("0.544","10.2"),
                 ("0.576","9.6"),("0.576","9.6")],
 "ADIPS 1998":  [("0.610","9.9"),("0.763","6.5"),("0.470","12.7"),("0.500","12.2"),
                 ("0.524","11.6")],
 "EASD 1996":   [("0.831","3.3"),("0.709","4.5"),("0.717","4.5"),("0.717","4.5")],
 "NZSSD 2004":  [("0.632","6.8"),("0.670","6.2"),("0.670","6.2")],
 "CDA 2003":    [("0.960","0.6"),("0.920","1.1")],
 "ADA 2004":    [("0.961","0.6")],
}
# Table 3 repeats the IADPSG row; transcription is wrong if these disagree.
TABLE3 = {"NICE 2015":("0.580","14.7"), "ADIPS 1998":("0.609","13.3"),
          "DIPSI 2009":("0.456","18.1"), "WHO 1999":("0.456","18.1"),
          "CDA 2013":("0.811","6.2"), "NZSSD 2004":("0.648","10.7"),
          "EASD 1996":("0.509","14.1"), "ADA 2004":("0.432","15.9"),
          "CDA 2003":("0.406","16.4"), "JSOG 1984":("0.432","15.8")}


def main() -> None:
    for i, b in enumerate(ORDER[1:]):
        assert FIG2["IADPSG 2010"][i] == TABLE3[b], f"figure and Table 3 disagree on {b}"

    rows, pairs = [], 0
    for ai, a in enumerate(ORDER):
        for j, b in enumerate(ORDER[ai + 1:]):
            kappa, dis = FIG2[a][j]
            pairs += 1
            both = list(recover(n=N, n_a=POS[a], n_b=POS[b], kappa=kappa,
                                agreement=f"{100 - float(dis):.1f}", agreement_as_percent=True))
            konly = list(recover(n=N, n_a=POS[a], n_b=POS[b], kappa=kappa))
            r = {"a": a, "b": b, "n_a": POS[a], "n_b": POS[b], "kappa": kappa,
                 "disagreement_percent": dis, "tables_kappa_and_disagreement": len(both),
                 "tables_kappa_alone": len(konly)}
            if len(konly) == 1:
                t = konly[0].as_dict()
                d = t["n10"] + t["n01"]
                r |= {"cells": t, "discordant": d,
                      "discordant_percent_exact": f"{float(Fraction(100*d, N)):.2f}"}
            rows.append(r)

    uniq_both = sum(1 for r in rows if r["tables_kappa_and_disagreement"] == 1)
    empty = [r for r in rows if r["tables_kappa_and_disagreement"] == 0]
    uniq_k = sum(1 for r in rows if r["tables_kappa_alone"] == 1)
    trunc = [r for r in empty if r.get("discordant_percent_exact")
             and r["discordant_percent_exact"][:-1] == f'{float(r["disagreement_percent"]):.1f}'[:len(r["discordant_percent_exact"])-1]]
    json.dump({"source": "goyal2025, Table 3 and Figure 2", "N": N, "pairs": pairs,
               "positives": POS, "unique_from_kappa_and_disagreement": uniq_both,
               "unique_from_kappa_alone": uniq_k, "empty_candidate_set": len(empty),
               "rows": rows}, open(ROOT / "results/goyal_all_pairs.json", "w"), indent=2)
    print(f"  pairs                          {pairs}")
    print(f"  transcription check            all 10 IADPSG cells match Table 3")
    print(f"  unique, kappa alone            {uniq_k}")
    print(f"  unique, kappa + disagreement   {uniq_both}")
    print(f"  empty candidate set            {len(empty)}")
    for r in empty:
        print(f"      {r['a']:12} vs {r['b']:12} printed {r['disagreement_percent']:>5}%  "
              f"exact {r.get('discordant_percent_exact','?')}%")


if __name__ == "__main__":
    main()

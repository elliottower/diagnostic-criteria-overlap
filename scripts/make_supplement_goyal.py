"""Table S7: the 55 tables recovered from Goyal et al.

Reads results/goyal_all_pairs.json and results/goyal_figure2_ocr.json, so the table
and the transcription check cannot drift apart. Writes paper/supplement_goyal.tex.
"""
from __future__ import annotations

import json
import math
import pathlib
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHORT = {"IADPSG 2010": "IADPSG", "NICE 2015": "NICE", "DIPSI 2009": "DIPSI",
         "WHO 1999": "WHO", "CDA 2013": "CDA13", "ADIPS 1998": "ADIPS",
         "EASD 1996": "EASD", "NZSSD 2004": "NZSSD", "CDA 2003": "CDA03",
         "ADA 2004": "ADA", "JSOG 1984": "JSOG"}


def convention(exact: Fraction, printed: str) -> str:
    r = f"{float(exact):.1f}" == f"{float(printed):.1f}"
    tr = f"{math.floor(float(exact) * 10) / 10:.1f}" == f"{float(printed):.1f}"
    return "either" if r and tr else "truncated" if tr else "rounded" if r else "neither"


def main() -> None:
    d = json.load(open(ROOT / "results/goyal_all_pairs.json"))
    ocr = json.load(open(ROOT / "results/goyal_figure2_ocr.json"))
    N = d["N"]
    L = [r"\begin{table}[htbp]", r"\centering\scriptsize\setlength{\tabcolsep}{3.5pt}",
         r"\begin{tabular}{@{}llrrrrlcll@{}}", r"\toprule",
         r"A & B & $n_A$ & $n_B$ & $\kappa$ & $d$ (\%) & "
         r"$n_{11}/n_{10}/n_{01}/n_{00}$ & Tables & Structure & Convention \\",
         r"\midrule"]
    nested_n = not_nested_n = 0
    for r in d["rows"]:
        t = r.get("cells")
        if not t:
            continue
        disc = t["n10"] + t["n01"]
        struct = "nested" if (t["n10"] == 0 or t["n01"] == 0) else "not nested"
        nested_n += struct == "nested"
        not_nested_n += struct == "not nested"
        conv = convention(Fraction(100 * disc, N), r["disagreement_percent"])
        L.append(f"{SHORT[r['a']]} & {SHORT[r['b']]} & {r['n_a']} & {r['n_b']} & "
                 f"{r['kappa']} & {r['disagreement_percent']} & "
                 f"{t['n11']}/{t['n10']}/{t['n01']}/{t['n00']} & "
                 f"{r['tables_kappa_alone']} & {struct} & {conv} \\\\")
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Table S7.} Every pairwise comparison reported by "
          rf"\citet{{goyal2025}}, with the figures the article prints and the table those "
          rf"figures admit. $N = {N}$ throughout. $n_A$ and $n_B$ are the positive counts from "
          r"its Table~3; $\kappa$ and $d$ are from its Figure~2. \emph{Tables} is the number of "
          r"integer tables compatible with $N$, both counts and $\kappa$. \emph{Structure} is "
          rf"nested where one positive class lies inside the other in this cohort ({nested_n} "
          rf"pairs) and not nested where each criterion identifies women the other excludes "
          rf"({not_nested_n} pairs). "
          r"\emph{Convention} names the rounding rule under which the recovered discordant total "
          r"reproduces the printed $d$; where the two rules give the same string it reads "
          r"\emph{either}. The article states no convention and the two are mixed across the "
          r"figure. Provenance: the ten comparisons against IADPSG appear both in Table~3 and in "
          r"Figure~2 and agree; all 55 cells of Figure~2 were also read independently with "
          rf"optical character recognition, which agreed with the manual transcription on "
          rf"{ocr['agree']} of {ocr['cells_hand']} cells with no disagreement. Generated from "
          r"\texttt{results/goyal\_all\_pairs.json}.}",
          r"\label{tab:s7}", r"\end{table}"]
    (ROOT / "paper" / "supplement_goyal.tex").write_text("\n".join(L) + "\n")
    print(f"  Table S7: {nested_n + not_nested_n} rows, {nested_n} nested, {not_nested_n} not nested")
    print(f"  OCR check: {ocr['agree']}/{ocr['cells_hand']} agree, {len(ocr['differ'])} differ")


if __name__ == "__main__":
    main()

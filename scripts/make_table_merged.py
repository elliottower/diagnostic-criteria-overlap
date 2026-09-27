"""One recovery table: S2's figures, grouped the way the corpus groups a status table.

The per-row outcome prose in the main-text table repeated four times over, which
reads as a wall. Here the outcome is a \\multicolumn group header over the rows it
covers, and the per-row verdict is a symbol, following the Survives column in
causal-geometry-neuro. The Tables count is dropped: a cell range already shows
where more than one table survived.

Writes paper/table_merged.tex and a standalone preview at paper/table_merged_preview.tex
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

COND = {
    "meagher2014_strict": ("Delirium", r"DSM-IV (A) against DSM-5 read strictly (B)"),
    "meagher2014_permissive": ("Delirium", r"DSM-IV (A) against DSM-5 read relaxed (B)"),
    "meagher2014_reading": ("Delirium", r"DSM-5 strict (A) against relaxed (B)"),
    "inoue2012_fpg": ("Diabetes", r"JDS (A) against ADA fasting glucose (B)"),
    "inoue2012_hba1c": ("Diabetes", r"JDS (A) against ADA HbA1c (B)"),
    "inoue2012_ada": ("Diabetes", r"ADA fasting glucose (A) against ADA HbA1c (B)"),
    "westbury2023": ("Sarcopenia", r"EWGSOP2 (A) against SDOC (B)"),
    "guerra2026": ("Multiple sclerosis", r"Neurologist label (A) against trial definition (B)"),
    "daghi2026": ("Parkinson's disease", r"5-2-1 criteria (A) against neurologist judgment (B)"),
}

GROUPS = [
    ("Table already printed", lambda r: bool(r.get("self_test")), ""),
    ("Table not printed", lambda r: not r.get("self_test"), ""),
]


def fmt(n): return f"{n:,}".replace(",", "{,}")


def row(key, rec, mark):
    cond, crit = COND[key]
    pub, cr = rec["published"], rec.get("cell_ranges")
    na = fmt(pub["n_A"]) if pub.get("n_A") is not None else f"{pub.get('p_A','---')}\\%"
    nb = fmt(pub["n_B"]) if pub.get("n_B") is not None else f"{pub.get('p_B','---')}\\%"
    if not cr:
        cells = "none"
    else:
        cells = "/".join(fmt(cr[k]["min"]) if cr[k]["min"] == cr[k]["max"]
                         else f"{fmt(cr[k]['min'])}--{fmt(cr[k]['max'])}"
                         for k in ("n11", "n10", "n01", "n00"))
    kkm = rec.get("kappa_over_kappa_max")
    kk = "---" if not kkm else (f"{kkm['min']:.2f}" if abs(kkm['max'] - kkm['min']) < 5e-3
                                else f"{kkm['min']:.2f}--{kkm['max']:.2f}")
    return (f"{cond} & {crit} & {fmt(rec['N'])} & {na} & {nb} & {pub['kappa']} & "
            f"{cells} & {rec['candidate_count']} & {kk} \\\\")


def build(recs):
    L = [r"\begin{table}[htbp]", r"\centering\footnotesize\setlength{\tabcolsep}{3pt}",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{1.75cm}"
         r">{\raggedright\arraybackslash}p{3.6cm}rrrl"
         r">{\raggedright\arraybackslash}p{2.7cm}rr@{}}",
         r"\toprule",
         r"Condition & Criteria compared & $N$ & $n_A$ & $n_B$ & $\kappa$ & "
         r"Cells $n_{11}/n_{10}/n_{01}/n_{00}$ & Tables & $\kappa/\kappa_{\max}$ \\"]
    for head, pred, mark in GROUPS:
        keys = [k for k in COND if k in recs and pred(recs[k])]
        if not keys:
            continue
        L += [r"\midrule", rf"\multicolumn{{9}}{{@{{}}l}}{{\emph{{{head}}}}} \\[2pt]"]
        L += [row(k, recs[k], mark) for k in keys]
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{Every eligible comparison, the figures its source "
          r"printed, and the integer table those figures admit. $n_A$ and $n_B$ are the two "
          r"positive marginals, given as the source gave them; $\kappa$ is reproduced at the "
          r"precision the source printed, since the digits are the constraint. A range in the "
          r"cells column gives the smallest and largest value that cell takes across the "
          r"surviving tables, so a range is a comparison the printed figures do not pin down. "
          r"$\kappa/\kappa_{\max}$ is agreement attained against agreement the two marginals "
          r"permit. The multiple sclerosis round trip is circular: the source prints no "
          r"coefficient, so the $\kappa$ enumerated from was computed here from the very cells "
          r"being recovered, and the check shows only that the enumeration returns a superset of "
          r"what it was given. Generated from \texttt{results/recovery.json}.}",
          r"\label{tab:recovery}", r"\end{table}"]
    return "\n".join(L) + "\n"


def main():
    recs = {r["key"]: r for r in json.load(open(ROOT / "results/recovery.json"))["results"]}
    missing = set(recs) - set(COND)
    assert not missing, f"eligible comparisons with no label: {sorted(missing)}"
    body = build(recs)
    (ROOT / "paper" / "table_merged.tex").write_text(body)
    (ROOT / "paper" / "table_merged_preview.tex").write_text(
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage{booktabs,array,amssymb,amsmath}\n"
        "\\pagestyle{empty}\n\\begin{document}\n" + body + "\\end{document}\n")
    print(f"  {len(recs)} rows in {len(GROUPS)} groups -> paper/table_merged.tex")


if __name__ == "__main__":
    main()

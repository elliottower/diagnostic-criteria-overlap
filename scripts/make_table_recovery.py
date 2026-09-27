"""Main-text recovery table, generated from results/recovery.json.

One row per eligible comparison: the number of integer tables the printed figures
admit, the cells, and the role the comparison plays. Four roles occur. Validation:
the source prints its own cells and coefficient, so the recovered cells can be
checked. Recovery: the source prints no cells, so the enumeration is the only route
to them. Precision: the source prints cells but no coefficient, so the coefficient
was computed here and the candidate count shows what its printed precision leaves
open. Consistency: no integer table reproduces every printed figure.

Writes paper/table_recovery.tex.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

NAME = {
    "meagher2014_strict": ("Delirium", "DSM-IV against DSM-5 read strictly"),
    "meagher2014_permissive": ("Delirium", "DSM-IV against DSM-5 read as relaxed"),
    "inoue2012_fpg": ("Diabetes", "JDS against ADA fasting glucose"),
    "inoue2012_hba1c": ("Diabetes", "JDS against ADA HbA\\textsubscript{1c}"),
    "westbury2023": ("Sarcopenia", "EWGSOP2 against SDOC"),
    "meagher2014_reading": ("Delirium", "DSM-5 read strictly against read as relaxed"),
    "inoue2012_ada": ("Diabetes", "ADA fasting glucose against ADA HbA\\textsubscript{1c}"),
    "guerra2026": ("Multiple sclerosis", "neurologist label against trial definition"),
    "daghi2026": ("Parkinson's disease", "5-2-1 against neurologist judgment"),
}

ROLES = ("Validation", "Recovery", "Precision", "Consistency")


def role(r: dict) -> str:
    """Decided from the record, so a row cannot be listed under a role it does not have."""
    if r["candidate_count"] == 0:
        return "Consistency"
    if r["candidate_count"] > 1:
        return "Precision"
    return "Validation" if r.get("self_test") else "Recovery"


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "{,}")


def cells(r: dict) -> str:
    cr = r.get("cell_ranges")
    if not cr:
        return "---"
    parts = []
    for k in ("n11", "n10", "n01", "n00"):
        lo, hi = cr[k]["min"], cr[k]["max"]
        parts.append(fmt(lo) if lo == hi else f"{fmt(lo)}--{fmt(hi)}")
    return "/".join(parts)


def main() -> None:
    recs = {r["key"]: r for r in json.load(open(ROOT / "results/recovery.json"))["results"]}
    missing = set(recs) - set(NAME)
    assert not missing, f"eligible comparisons with no label: {sorted(missing)}"

    L = [r"\begin{table}[htbp]", r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.1cm}"
         r">{\raggedright\arraybackslash}p{4.6cm}r"
         r">{\raggedright\arraybackslash}p{3.9cm}l@{}}",
         r"\toprule",
         r"Condition & Comparison & Candidates & Cells $n_{11}/n_{10}/n_{01}/n_{00}$ & Role \\",
         r"\midrule"]
    order = sorted(recs, key=lambda k: (ROLES.index(role(recs[k])), list(NAME).index(k)))
    counts = {x: 0 for x in ROLES}
    for key in order:
        r = recs[key]
        cond, comparison = NAME[key]
        counts[role(r)] += 1
        L.append(f"{cond} & {comparison} & {r['candidate_count']} & {cells(r)} & "
                 f"{role(r)} \\\\[2pt]")
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{Every eligible comparison and what the enumeration returns for it. "
          r"Candidates is the number of integer tables compatible with every printed figure; "
          r"cells are given as ranges where more than one table survives. Validation rows print "
          r"their own cells and coefficient, and the recovered cells match them. Recovery rows "
          r"print no cells. The precision row prints its cells but no coefficient, so its "
          r"$\kappa$ was computed here, and its eleven candidates show what two decimals leave "
          r"open at $N = 20{,}306$. The consistency row admits no table "
          r"(Section~\ref{sec:infeasible}). Generated from \texttt{results/recovery.json}.}",
          r"\label{tab:recovery}", r"\end{table}"]
    (ROOT / "paper" / "table_recovery.tex").write_text("\n".join(L) + "\n")
    print("  " + ", ".join(f"{n} {k.lower()}" for k, n in counts.items())
          + f" ({sum(counts.values())} rows)")


if __name__ == "__main__":
    main()

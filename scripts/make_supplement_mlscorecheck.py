"""Table S12: what one marginal admits against what both admit, and mlscorecheck's check.

mlscorecheck takes the exact positive and negative counts on one side and the printed
scores; it has no input for the second marginal. For each comparison this gives the
exact number of integer tables compatible with the sample size, one side's count,
kappa and (where printed) raw agreement, taking each criterion in turn as the known
side, beside the number the enumeration returns from both marginals, and whether
mlscorecheck accepts every table the enumeration returns. The 55 gestational diabetes
pairs are summarized in one row; Table S7 lists them.

Reads results/mlscorecheck_crosscheck.json. Writes paper/supplement_mlscorecheck.tex.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "mlscorecheck_crosscheck.json"
OUT = ROOT / "paper" / "supplement_mlscorecheck.tex"

NAME = {
    "meagher2014_strict": "Delirium: DSM-IV against DSM-5 read strictly",
    "meagher2014_permissive": "Delirium: DSM-IV against DSM-5 read as relaxed",
    "meagher2014_reading": "Delirium: DSM-5 read strictly against read as relaxed",
    "inoue2012_fpg": "Diabetes: JDS against ADA fasting glucose",
    "inoue2012_hba1c": "Diabetes: JDS against ADA HbA\\textsubscript{1c}",
    "inoue2012_ada": "Diabetes: ADA fasting glucose against ADA HbA\\textsubscript{1c}",
    "westbury2023": "Sarcopenia: EWGSOP2 against SDOC",
    "guerra2026": "Multiple sclerosis: neurologist label against trial definition",
    "daghi2026": "Parkinson's disease: 5-2-1 against neurologist judgment",
    "valencia2024": "Sarcopenia: EWGSOP1 against EWGSOP2",
}
ORDER = list(NAME)


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "{,}")


def span(values: list[int]) -> str:
    lo, hi = min(values), max(values)
    return fmt(lo) if lo == hi else f"{fmt(lo)}--{fmt(hi)}"


def main() -> None:
    d = json.loads(SRC.read_text())
    rows = {r["comparison"]: r for r in d["rows"]}
    missing = [k for k in rows if not k.startswith("goyal") and k not in NAME]
    assert not missing, f"comparisons with no label: {missing}"

    L = [r"\begin{table}[htbp]", r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.1cm}r"
         r">{\raggedleft\arraybackslash}p{1.9cm}>{\raggedleft\arraybackslash}p{1.9cm}"
         r">{\raggedleft\arraybackslash}p{1.5cm}>{\raggedright\arraybackslash}p{2.2cm}@{}}",
         r"\toprule",
         r"Comparison & $N$ & Tables, first count only & Tables, second count only & "
         r"Tables, both counts & Accepted by \texttt{mlscorecheck} \\",
         r"\midrule"]
    for key in ORDER:
        r = rows[key]
        m = r["mlscorecheck"]
        if isinstance(m, str):
            L.append(f"{NAME[key]} & {fmt(r['N'])} & --- & --- & {r['enumeration_tables']} & "
                     r"not run$^{a}$ \\[2pt]")
            continue
        acc = "yes" if all(s["mlscorecheck_accepts_every_enumeration_table"] for s in m.values()) else "no"
        L.append(f"{NAME[key]} & {fmt(r['N'])} & {fmt(m['A known']['one_marginal_tables_exact'])} & "
                 f"{fmt(m['B known']['one_marginal_tables_exact'])} & {r['enumeration_tables']} & {acc} \\\\[2pt]")

    g = [r for k, r in rows.items() if k.startswith("goyal")]
    first = [r["mlscorecheck"]["A known"]["one_marginal_tables_exact"] for r in g]
    second = [r["mlscorecheck"]["B known"]["one_marginal_tables_exact"] for r in g]
    both = [r["enumeration_tables"] for r in g]
    accepted = sum(all(s["mlscorecheck_accepts_every_enumeration_table"] for s in r["mlscorecheck"].values()) for r in g)
    unique_one = sum(r["one_marginal_fewest_tables"] == 1 for r in g)
    L.append(f"Gestational diabetes: all {len(g)} pairs of eleven criteria & {fmt(g[0]['N'])} & "
             f"{span(first)} & {span(second)} & {span(both)} & {accepted} of {len(g)} \\\\[2pt]")

    s = d["summary"]
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Table S12.} How many integer tables each comparison's printed figures "
          r"admit with one marginal and with both, and whether \texttt{mlscorecheck} "
          r"\citep{fazekas2024testing,kovacs2023mlscorecheck} accepts the recovered table. "
          r"\texttt{mlscorecheck} treats each printed score as the interval its rounding implies, "
          r"takes the exact positive and negative counts on one side, and has no input for the "
          r"second marginal. The two one-count columns give the exact number of integer tables "
          r"compatible with $N$, that criterion's count, $\kappa$ and, where the source prints it, "
          r"raw agreement; the both-counts column is the number the enumeration returns. With one "
          rf"count the figures fix a single table in {s['one_marginal_unique_either_side']} of the "
          rf"{s['mlscorecheck_run']} comparisons that can be run, taking whichever side admits fewer, "
          rf"{unique_one} of them gestational diabetes pairs; with both they fix one in "
          rf"{s['enumeration_unique']}. \emph{{Accepted}} means that \texttt{{mlscorecheck}}, given the "
          r"printed scores and restricted to a table the enumeration returned, reports no "
          r"inconsistency, taking each criterion in turn as the known side. Its own count of "
          r"compatible tables is an upper bound from interval arithmetic and is recorded in the "
          r"results file. $^{a}$The source prints both marginals as percentages, and "
          r"\texttt{mlscorecheck} needs exact counts. Generated from "
          r"\texttt{results/mlscorecheck\_crosscheck.json}.}",
          r"\label{tab:s12}", r"\end{table}"]
    OUT.write_text("\n".join(L) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(ORDER)} comparisons and a {len(g)}-pair summary row")
    print(f"  one count unique in {s['one_marginal_unique_either_side']} of {s['mlscorecheck_run']}; "
          f"both counts in {s['enumeration_unique']}; gestational diabetes accepted {accepted} of {len(g)}")


if __name__ == "__main__":
    main()

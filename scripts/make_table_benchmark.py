"""The five-row benchmark, and the consistency case kept separate from it.

Both procedures receive the same sample size, the same marginals and a coefficient
rounded to the same precision, on the five comparisons whose source printed its own
cells. Daghi is not in the benchmark: conv.2x2 does not accept the combination of
kappa, marginals and raw agreement, and deriving a coefficient it does accept would
mean solving the table first, which is what is being tested.

Writes paper/table_benchmark.tex, paper/table_consistency.tex and a preview.
"""
from __future__ import annotations

import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = {r["key"]: r for r in json.load(open(ROOT / "results/conv2x2_corpus.json"))["rows"]}
DAGHI = {r["key"]: r for r in
         json.load(open(ROOT / "results/recovery.json"))["results"]}["daghi2026"]

NAME = {
    "meagher2014_strict": "Delirium: DSM-IV vs strict DSM-5",
    "meagher2014_permissive": "Delirium: DSM-IV vs relaxed DSM-5",
    "inoue2012_fpg": "Diabetes: JDS vs ADA glucose",
    "inoue2012_hba1c": "Diabetes: JDS vs ADA HbA1c",
    "guerra2026": "Multiple sclerosis: neurologist vs protocol",
}


def main():
    ex = sum(D[k]["point_largest_cell_error"] == 0 for k in NAME)
    uniq = sum(D[k]["enumeration_candidates"] == 1 for k in NAME)
    L = [r"\begin{table}[htbp]", r"\centering\footnotesize",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.6cm}r"
         r">{\raggedleft\arraybackslash}p{3.1cm}>{\raggedleft\arraybackslash}p{3.6cm}@{}}",
         r"\toprule",
         r"Comparison & $N$ & Point reconstruction & \texttt{enum2x2} \\",
         r" & & \texttt{metafor::conv.2x2} & this work \\", r"\midrule"]
    for k, name in NAME.items():
        r = D[k]
        e = r["point_largest_cell_error"]
        pt = "exact" if e == 0 else f"largest cell error: {e}"
        c = r["enumeration_candidates"]
        en = f"{c} candidate{'s' if c > 1 else ''}; source retained"
        L.append(f"{name} & {r['N']:,} & {pt} & {en} \\\\".replace(",", "{,}"))
    L += [r"\midrule",
          rf"\textbf{{Overall}} & 5 & exact in {ex} of 5 & source retained in 5 of 5 \\",
          r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Point reconstruction against set identification on five "
          r"comparisons whose source printed its cells.} The source cells were withheld and "
          r"both procedures received the same sample size, the same marginals and a coefficient "
          r"rounded to the same precision: \texttt{conv.2x2} a phi coefficient at two decimals, "
          r"the enumeration Cohen's $\kappa$ as the source printed it. Point-reconstruction "
          r"error is the largest absolute difference between a returned cell and the source "
          rf"cell. \texttt{{enum2x2}} returns every compatible integer table; \emph{{source "
          rf"retained}} means the printed table is in that set, and {uniq} of the five sets "
          r"contain one table only. Exact inputs and arguments for each row are in Table~S4 and "
          r"\texttt{results/conv2x2\_corpus.json}.}",
          r"\label{tab:benchmark}", r"\end{table}"]
    bench = "\n".join(L) + "\n"

    C = [r"\begin{table}[htbp]", r"\centering\footnotesize",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.0cm}"
         r">{\raggedright\arraybackslash}p{5.6cm}r@{}}", r"\toprule",
         r"Consistency check & Published constraints & \texttt{enum2x2} \\", r"\midrule",
         r"Parkinson's disease: 5-2-1 criteria against neurologist judgment, $N = 370$ & "
         r"two marginals, raw agreement and $\kappa$ & 0 compatible tables \\",
         r"\bottomrule", r"\end{tabular}",
         r"\caption{A point reconstruction supplied with three independent constraints returns "
         r"a table by construction and cannot detect conflict with a fourth it was never given. "
         r"The enumeration accepts every printed constraint together and returns the empty set "
         r"when they cannot describe one table. This row is therefore not part of "
         r"Table~\ref{tab:benchmark}: \texttt{conv.2x2} does not accept this combination of "
         r"inputs, and supplying it a coefficient derived by first solving the table would "
         r"assume the answer.}",
         r"\label{tab:consistency}", r"\end{table}"]
    cons = "\n".join(C) + "\n"

    (ROOT / "paper" / "table_benchmark.tex").write_text(bench)
    (ROOT / "paper" / "table_consistency.tex").write_text(cons)
    (ROOT / "paper" / "table_benchmark_preview.tex").write_text(
        "\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage{booktabs,array,amssymb,amsmath,float}\n\\pagestyle{empty}\n"
        "\\begin{document}\n" + bench.replace("[htbp]", "[H]")
        + "\n\\bigskip\n" + cons.replace("[htbp]", "[H]") + "\\end{document}\n")
    print(f"  benchmark: exact in {ex} of 5, {uniq} of 5 uniquely identified; consistency row separate")


if __name__ == "__main__":
    main()

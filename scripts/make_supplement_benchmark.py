"""Table S11: point reconstruction and enumeration on the comparisons whose answer is known.

Five corpus comparisons print their own cells. Each procedure is given the same
sample size and marginals and a coefficient at two decimals: conv.2x2 a phi
coefficient, the enumeration kappa as the source printed it. The table records the
exact arguments each received beside what each returned, so a row can be rerun.

Reads results/conv2x2_corpus.json. Writes paper/supplement_benchmark.tex.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "conv2x2_corpus.json"
OUT = ROOT / "paper" / "supplement_benchmark.tex"

NAME = {
    "meagher2014_strict": "Delirium: DSM-IV against DSM-5 read strictly",
    "meagher2014_permissive": "Delirium: DSM-IV against DSM-5 read as relaxed",
    "inoue2012_fpg": "Diabetes: JDS against ADA fasting glucose",
    "inoue2012_hba1c": "Diabetes: JDS against ADA HbA\\textsubscript{1c}",
    "guerra2026": "Multiple sclerosis: neurologist label against trial definition",
}


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "{,}")


def four(v: list[int]) -> str:
    return "/".join(fmt(x) for x in v)


def main() -> None:
    rows = {r["key"]: r for r in json.loads(SRC.read_text())["rows"]}
    missing = set(rows) - set(NAME)
    assert not missing, f"comparisons with no label: {sorted(missing)}"
    L = [r"\begin{table}[htbp]", r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{3.0cm}"
         r">{\raggedright\arraybackslash}p{3.15cm}cc"
         r">{\raggedright\arraybackslash}p{3.2cm}rc@{}}",
         r"\toprule",
         r" & & \multicolumn{2}{c}{Given} & \texttt{conv.2x2} & \multicolumn{2}{c}{\texttt{enum2x2}} \\",
         r"\cmidrule(lr){3-4}\cmidrule(lr){5-5}\cmidrule(lr){6-7}",
         r"Comparison & Source cells & $\phi$ & $\kappa$ & Returned & Candidates & Source retained \\",
         r"\midrule"]
    exact = 0
    for key in NAME:
        r = rows[key]
        g = r["inputs_supplied"]
        err = r["point_largest_cell_error"]
        exact += err == 0
        returned = "exact" if err == 0 else f"{four(r['point_reconstruction'])} (largest cell off by {err})"
        L.append(f"{NAME[key]} & {four(r['true_cells'])} & {g['phi_rounded']} & "
                 f"{g['kappa_as_printed']} & {returned} & {r['enumeration_candidates']} & "
                 f"{'yes' if r['enumeration_contains_true'] else 'no'} \\\\[2pt]")
    L += [r"\bottomrule", r"\end{tabular}",
          rf"\caption{{\textbf{{Table S11.}} Point reconstruction and enumeration on the "
          rf"{len(NAME)} corpus comparisons whose sources print their own cells. The cells were "
          r"withheld, and both procedures received the same sample size and marginals. "
          r"\texttt{metafor::conv.2x2} was given the phi coefficient of the printed table rounded "
          r"to two decimals, which is the coefficient it accepts; the enumeration was given "
          r"$\kappa$ as the source printed it. \emph{Returned} is the single table "
          rf"\texttt{{conv.2x2}} reports, exact in {exact} of {len(NAME)}. \emph{{Candidates}} is "
          r"the number of integer tables the enumeration returns, and \emph{Source retained} "
          r"whether the printed table is among them. Cells are $n_{11}/n_{10}/n_{01}/n_{00}$. "
          r"Generated from \texttt{results/conv2x2\_corpus.json}, which records every argument "
          r"passed to either procedure.}",
          r"\label{tab:s11}", r"\end{table}"]
    OUT.write_text("\n".join(L) + "\n")
    print(f"  wrote {OUT.relative_to(ROOT)}: {len(NAME)} rows, conv.2x2 exact in {exact}")


if __name__ == "__main__":
    main()

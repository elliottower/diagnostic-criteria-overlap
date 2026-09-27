"""Tables S5 and S6: what each guidance document asks for, and the tools set aside.

Both tables are editorial mappings rather than computed results, so every cell
either quotes a source pinned in claims/ or names what the tool does. The GRRAS
and STARD term counts are read from results/table1_guideline_terms.json rather
than retyped, so the two cannot drift apart.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "supplement_guidance.tex"

GUIDANCE = [
    ("STARD 2015", r"\citet{bossuyt2015}",
     r"``Cross tabulation of the index test results (or their distribution) by the results of the reference standard'' (item 23)",
     "an index test against a reference standard",
     r"No. Item~11 asks for the ``Rationale for choosing the reference standard'', which presupposes one procedure has been nominated correct."),
    ("FDA 2007", r"\citet{fda2007diagnostic}",
     r"``the 2x2 table of results comparing the candidate test with the comparative method''",
     "a candidate test against a comparative method, whether or not that method is a reference standard",
     "Partly. The comparator need not qualify as a reference standard, but one side is still the candidate."),
    ("COSMIN 2021", r"\citet{cosmin2021ee}",
     r"``Results of all variance components, or contingency tables''; ``For kappa values, we recommend reporting contingency tables, in addition to the kappa value itself''",
     "measurement properties of patient-reported instruments",
     "No. The element that varies is the measurement occasion or the rater, not the criterion."),
    ("Doust 2017", r"\citet{doust2017}",
     r"``studies of prevalence need to cross-classify patients, showing where the definitions agree or are discordant''",
     "a disease definition that changes its measurement method",
     "Yes. The closest fit among the reporting guidance, and the only one whose varying element is the definition."),
    ("GRRAS", r"\citet{kottner2011}",
     "the rater population, the number of raters, replicate observations, and the raters' training",
     "reliability and agreement between raters",
     "No. Seven of the fifteen items presuppose that raters vary; in a criteria comparison each is inapplicable or has no determinate answer."),
    ("STROBE", r"\citet{vonelm2007}",
     r"``Give diagnostic criteria, if applicable''",
     "observational studies generally",
     "Reaches the case without describing it. Four words that do not ask which revision was applied."),
    ("RECORD", r"\citet{benchimol2015}",
     "the STROBE item, reproduced unchanged",
     "studies using routinely collected health data",
     "Reaches the case without describing it."),
    ("ACR 2026", r"\citet{johnson2026acr}",
     r"``Comparisons with previous criteria are recommended''; an ``Independent validation cohort to assess criteria performance and compare to older criteria/alternatives''",
     "the development of disease classification criteria",
     r"Yes, and it is written for this design. It routes the comparison through a third adjudicated standard, so it asks for the comparison without asking for the $2 \times 2$ table."),
]

TOOLS = [
    (r"\texttt{metafor}, \texttt{conv.2x2}", r"\citet{viechtbauer2010,metafor_conv2x2}",
     r"Reconstructs the cells of a $2\times2$ from a sample size, both marginals and one further statistic, by optimization.",
     r"Returns a nearest table. Its documentation states the calculations ``are exact only for unrounded values''."),
    ("Kaplan--Meier reconstruction", r"\citet{guyot2012}",
     "Recovers individual survival data from a published survival curve.",
     "A different object; no contingency table is at issue."),
    (r"$2\times2$ from odds ratios", r"\citet{veroniki2013}",
     "Reconstructs cells from a reported odds ratio.",
     "Point reconstruction, with the printed precision treated as noise."),
    ("Diagnostic-accuracy reconstruction", r"\citet{vogelgesang2024}",
     "Recovers contingency tables from published diagnostic-accuracy summaries.",
     "Presupposes a reference standard, so the object is the accuracy table rather than the criterion-by-criterion table."),
    ("GRIM, GRIMMER, SPRITE", r"\citet{brown2017grim,anaya2016grimmer,heathers2018sprite}",
     "Ask whether reported summary statistics could have arisen from any dataset of the stated size.",
     "Consistency checking rather than recovery; they return a verdict, not a set of tables."),
    (r"\texttt{statcheck}", r"\citet{nuijten2020statcheck}",
     "Recomputes reported test statistics and $p$ values from their printed components.",
     "Consistency checking, and the object is a test statistic rather than a table."),
    ("Bounds from conditional frequencies", r"\citet{wright2014,sage2016}",
     "Gives exact bounds on a two-way table from released conditional frequencies.",
     "The inputs are conditional frequencies in a disclosure-control setting, not two marginals and an agreement coefficient."),
    ("Algebraic statistics", r"\citet{slavkovic2015,dobra_algebraic}",
     "Treats the compatible tables as the fiber of a map under fixed constraints.",
     "Where software exists it samples from a fiber rather than enumerating it."),
    (r"\texttt{testCompareR}, \texttt{DTComPair}", r"\citet{wilson2024}",
     "Compares two binary diagnostic tests against a gold standard from paired patient-level results.",
     "Requires patient-level data and a gold standard, both of which are absent once a study is published as summaries."),
]


def rows(items, widths):
    out = []
    for r in items:
        out.append(" & ".join(str(c) for c in r) + r" \\")
        out.append(r"\addlinespace[2pt]")
    return out[:-1]


def main() -> None:
    counts = json.load(open(ROOT / "results/table1_guideline_terms.json"))["counts"]
    zero_one_side = sum(1 for v in counts.values() if v["grras"] == 0 or v["stard"] == 0)

    L = [r"\begin{table}[htbp]", r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.7cm}>{\raggedright\arraybackslash}p{3.9cm}>{\raggedright\arraybackslash}p{3.0cm}>{\raggedright\arraybackslash}p{5.0cm}@{}}",
         r"\toprule",
         r"Document & What it asks for & Under what framing & Does it reach a criteria-versus-criteria comparison? \\",
         r"\midrule"]
    for name, cite, asks, framing, reaches in GUIDANCE:
        L.append(f"{name}~{cite} & {asks} & {framing} & {reaches} \\\\")
        L.append(r"\addlinespace[3pt]")
    L = L[:-1]
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Table S5.} Every document named in the guidance section of the main text, "
          r"with the passage in which it asks for a cross-classification and the design that passage "
          rf"assumes. Of ten terms taken from the GRRAS and STARD checklists, {zero_one_side} are zero on one "
          r"side or the other, so the two vocabularies are disjoint over the terms examined "
          r"(\texttt{results/table1\_guideline\_terms.json}). Quotations are pinned in \texttt{claims/}.}",
          r"\label{tab:s5}", r"\end{table}", ""]

    L += [r"\begin{table}[htbp]", r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
          r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{3.2cm}>{\raggedright\arraybackslash}p{5.2cm}>{\raggedright\arraybackslash}p{6.2cm}@{}}",
          r"\toprule", r"Tool & What it does & Why it is set aside here \\", r"\midrule"]
    for name, cite, does, why in TOOLS:
        L.append(f"{name}~{cite} & {does} & {why} \\\\")
        L.append(r"\addlinespace[3pt]")
    L = L[:-1]
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Table S6.} Reconstruction and consistency-checking tools considered and "
          r"set aside, with the reason for each. None takes a sample size, two rounded binary marginals "
          r"and a rounded agreement coefficient, returns every compatible integer table, and reports that "
          r"none is compatible rather than selecting the nearest one.}",
          r"\label{tab:s6}", r"\end{table}", ""]

    OUT.write_text("\n".join(L) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(GUIDANCE)} guidance rows, {len(TOOLS)} tool rows, "
          f"{zero_one_side}/10 terms zero on one side")


if __name__ == "__main__":
    main()

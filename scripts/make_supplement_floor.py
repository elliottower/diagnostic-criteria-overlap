"""Table S10: the rater-level figures the record supplies, and why none matches.

Separating criterion divergence from inconsistent application needs a rater-level
figure and a criterion-level figure on the same target, population and criteria.
Three of the sixteen pairs carry any rater-level figure for the same condition and
none of the three matches, each failing differently. The table records the three
so the main text can state the count without listing them.

These are the source figures only. The correction that was once computed from them
is not reported: it is derived for the product-moment correlation under classical
test theory, and Cohen's kappa is chance-corrected and marginal-dependent.

Output: paper/supplement_floor.tex, results/rater_level_figures.json
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "supplement_floor.tex"
RESULTS = ROOT / "results" / "rater_level_figures.json"

ROWS = [
    {"condition": "Multiple sclerosis",
     "comparison": "neurologist-assigned label against the trial protocol definition",
     "comparison_cite": r"\citet{guerra2026}",
     "criterion_kappa": "0.22",
     "rater_figure": "0.52 to 0.57",
     "rater_measures": "four neurologists applying diagnostic criteria to 44 cases",
     "rater_cite": r"\citet{zipoli2003}",
     "why_unmatched": "A different target, and two decades earlier. The registry comparison "
                      "is algorithmic on recorded fields, so no rater intervenes on that side."},
    {"condition": "Multiple sclerosis",
     "comparison": "McDonald 2017 and McDonald 2024, each applied by three readers",
     "comparison_cite": r"\citet{mahmoudi2026}",
     "criterion_kappa": "---",
     "rater_figure": "0.61 to 0.67",
     "rater_measures": "three readers classifying under each revision",
     "rater_cite": r"\citet{mahmoudi2026}",
     "why_unmatched": "The rater-level figure is the matched one, and the criterion-level "
                      "figure is absent: the study scores each revision against the readers "
                      "and never compares the two revisions with each other."},
    {"condition": "Stroke",
     "comparison": "TOAST against CCS",
     "comparison_cite": r"\citet{mcardle2014}",
     "criterion_kappa": "0.59",
     "rater_figure": "0.857",
     "rater_measures": "inter-rater agreement on CISS",
     "rater_cite": r"\citet{zhang2019}",
     "why_unmatched": "CISS is on neither side of the comparison at issue, and no rater-level "
                      "figure is published for TOAST or for CCS."},
]


def main() -> None:
    L = [r"\begin{table}[htbp]",
         r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.4cm}"
         r">{\raggedright\arraybackslash}p{3.5cm}c"
         r">{\raggedright\arraybackslash}p{3.4cm}"
         r">{\raggedright\arraybackslash}p{4.4cm}@{}}",
         r"\toprule",
         r"Condition & Criterion-level comparison & $\kappa$ & Rater-level figure "
         r"& Why it does not match \\",
         r"\midrule"]
    for r in ROWS:
        L.append(f"{r['condition']} & {r['comparison']}~{r['comparison_cite']} & "
                 f"{r['criterion_kappa']} & {r['rater_figure']}, {r['rater_measures']}"
                 f"~{r['rater_cite']} & {r['why_unmatched']} \\\\")
        L.append(r"\addlinespace[3pt]")
    L = L[:-1]
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Table S10.} The three of sixteen comparisons that carry any "
          r"published rater-level agreement figure for the same condition, and the respect in "
          r"which each fails to match the criterion-level comparison. Separating divergence "
          r"between criteria from inconsistent application of either would need both figures on "
          r"the same target, population and criteria; no pair here supplies that, and no "
          r"published correction takes a criterion-level $\kappa$ to what it would be were both "
          r"criteria applied without error.}",
          r"\label{tab:s10}", r"\end{table}", ""]
    OUT.write_text("\n".join(L) + "\n")
    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps(
        {"question": "which comparisons carry a rater-level figure for the same condition, "
                     "and does any of them match?",
         "pairs_in_corpus": 16, "pairs_with_any_rater_level_figure": len(ROWS),
         "pairs_matching_on_target_population_and_criteria": 0,
         "rows": ROWS}, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} and {RESULTS.relative_to(ROOT)}: {len(ROWS)} rows")


if __name__ == "__main__":
    main()

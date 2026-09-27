"""Table S8: the registered predictions, their thresholds and their outcomes.

Read from results/hypothesis_outcomes.json so the table cannot drift from the run.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
d = json.load(open(ROOT / "results/hypothesis_outcomes.json"))

TEXT = {
 "H1": ("Eligible comparisons that recover, uniquely or as a set",
        r"$\ge 8$ of the nine eligible comparisons"),
 "H2": (r"Recovered comparisons whose discordance is directional, $|n_{10}-n_{01}|/(n_{10}+n_{01}) > 1/3$",
        r"$\ge 4$ of the eight recovered"),
 "H3": (r"Recovered comparisons whose marginals cap agreement, $\kappa_{\max} < 0.9$",
        r"$\ge 4$ of the eight recovered"),
}
L = [r"\begin{table}[htbp]", r"\centering\footnotesize",
     r"\begin{tabular}{@{}l>{\raggedright\arraybackslash}p{6.4cm}"
     r">{\raggedright\arraybackslash}p{3.4cm}ll@{}}",
     r"\toprule", r"& Prediction & Registered threshold & Outcome & Holds \\", r"\midrule"]
for h in ("H1", "H2", "H3"):
    r = d[h]
    got = f"{r['recovered']} of {r['eligible']}" if h == "H1" else f"{r['hits']} of {r['of']}"
    desc, thr = TEXT[h]
    L.append(f"{h} & {desc} & {thr} & {got} & {'yes' if r['holds'] else 'no'} \\\\")
L += [r"\bottomrule", r"\end{tabular}",
      r"\caption{\textbf{Table S8.} The three predictions frozen in the registration, their "
      r"thresholds and their outcomes. Two of the three clear their threshold by a single "
      r"comparison. No recovered table, validation or outcome classification is computed from a "
      r"threshold, so none depends on where these were set. Generated from "
      r"\texttt{results/hypothesis\_outcomes.json}; the plan and its deviation log are in "
      r"\texttt{experiments/table\_recovery/PREREG.md}.}",
      r"\label{tab:s8}", r"\end{table}"]
(ROOT / "paper" / "supplement_prereg.tex").write_text("\n".join(L) + "\n")
print("wrote paper/supplement_prereg.tex")

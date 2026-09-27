"""What each statistic identifies, enumerated exhaustively rather than sampled.

For a fixed N, every non-negative integer table summing to N is generated, each
statistic is computed and printed to two decimals, and the enumeration is run on
the sample size, both marginals and that printed value. The result is one of the
paper's four outcomes. The sweep is exhaustive, so the table is reproducible
exactly; an earlier version sampled random tables and did not reproduce between
runs.

The counts are properties of the table space at a given N, not estimates of how
often a statistic identifies tables in published research.

Writes results/statistic_identification.json and paper/supplement_stats.tex.
"""
from __future__ import annotations

import json
import pathlib

from enum2x2 import recover
from enum2x2 import UndefinedStatistic
from enum2x2._core import CLOSING_STATISTICS, kappa_from_cells

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIZES = (20, 40)

STATS = {
    "positive_agreement": (CLOSING_STATISTICS["positive_agreement"][0],
                           "Positive specific agreement",
                           r"$2n_{11}/(2n_{11}+n_{10}+n_{01})$", "no positives"),
    "negative_agreement": (CLOSING_STATISTICS["negative_agreement"][0],
                           "Negative specific agreement",
                           r"$2n_{00}/(2n_{00}+n_{10}+n_{01})$", "no negatives"),
    "jaccard": (CLOSING_STATISTICS["jaccard"][0], "Jaccard similarity",
                r"$n_{11}/(n_{11}+n_{10}+n_{01})$", "no positives either side"),
    "kappa": (kappa_from_cells, "Cohen's $\\kappa$",
              r"$(p_o-p_e)/(1-p_e)$", "$p_e=1$"),
    "pabak": (CLOSING_STATISTICS["pabak"][0], "PABAK", r"$2p_o-1$", "none"),
    "scott_pi": (CLOSING_STATISTICS["scott_pi"][0], "Scott's $\\pi$", r"$(p_o-p_e)/(1-p_e)$, $p_e$ pooled", "$p_e=1$"),
    "gwet_ac1": (CLOSING_STATISTICS["gwet_ac1"][0], "Gwet's AC1",
                 r"$(p_o-p_e)/(1-p_e)$, $p_e=2\bar p(1-\bar p)$", "$p_e=1$"),
    "prevalence_index": (CLOSING_STATISTICS["prevalence_index"][0], "Prevalence index", r"$(n_{11}-n_{00})/N$", "none"),
    "bias_index": (CLOSING_STATISTICS["bias_index"][0], "Bias index", r"$(n_{10}-n_{01})/N$", "none"),
    "odds_ratio": (CLOSING_STATISTICS["odds_ratio"][0], "Odds ratio", r"$n_{11}n_{00}/(n_{10}n_{01})$",
                   "an empty off-diagonal cell"),
    "mcnemar_odds_ratio": (CLOSING_STATISTICS["mcnemar_odds_ratio"][0], "Paired odds ratio", r"$n_{10}/n_{01}$", "$n_{01}=0$"),
    "phi_squared": (CLOSING_STATISTICS["phi_squared"][0], "$\\phi^2$",
                    r"$(n_{11}n_{00}-n_{10}n_{01})^2/\prod$ marginals", "a zero marginal"),
}


def tables(n: int):
    for a in range(n + 1):
        for b in range(n + 1 - a):
            for c in range(n + 1 - a - b):
                yield a, b, c, n - a - b - c


def main() -> None:
    per_size = {}
    for n in SIZES:
        all_tables = list(tables(n))
        rows = []
        for key, (fn, _, _, _) in STATS.items():
            counts = {"unique": 0, "set": 0, "insufficient": 0, "undefined": 0}
            for cells in all_tables:
                try:
                    v = fn(*cells)
                except UndefinedStatistic:
                    counts["undefined"] += 1
                    continue
                r = recover(n=n, n_a=cells[0] + cells[1], n_b=cells[0] + cells[2],
                            **{key: f"{float(v):.2f}"})
                counts[r.status if r.status in counts else "insufficient"] += 1
            rows.append({"statistic": key, "tables": len(all_tables), **counts})
        per_size[n] = rows
        print(f"  N={n:3}  {len(all_tables):6} tables swept")

    json.dump({"what_this_measures":
               "Exhaustive sweep of every non-negative integer table summing to N. For each, "
               "the statistic is printed to two decimals and the enumeration run on N, both "
               "marginals and that value. Counts are properties of the table space at a given "
               "N, not estimates of behaviour in published research.",
               "sizes": list(SIZES), "printed_precision": "two decimals",
               "by_size": {str(k): v for k, v in per_size.items()}},
              open(ROOT / "results/statistic_identification.json", "w"), indent=2)

    ref = {r["statistic"]: r for r in per_size[SIZES[-1]]}
    marginal_only = {"prevalence_index", "bias_index"}
    L = [r"\begin{table}[htbp]", r"\centering\footnotesize",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.5cm}"
         r">{\raggedright\arraybackslash}p{3.7cm}c rrr>{\raggedright\arraybackslash}p{2.6cm}@{}}",
         r"\toprule",
         r"& & Adds to the & \multicolumn{3}{c}{At $N=%d$} & \\" % SIZES[-1],
         r"\cmidrule(lr){4-6}",
         r"Statistic & Definition & marginals & Unique & Set & Insuff. & Undefined when \\",
         r"\midrule"]
    for key, (_, name, defn, undef) in STATS.items():
        r = ref[key]
        adds = "no" if key in marginal_only else "yes"
        L.append(f"{name} & {defn} & {adds} & {r['unique']:,} & {r['set']:,} & "
                 f"{r['insufficient']:,} & {undef} \\\\")
    L += [r"\bottomrule", r"\end{tabular}",
          r"\caption{\textbf{Table S1.} Whether each quantity the implementation accepts "
          r"constrains the $2 \times 2$ table beyond the two marginals, and what it identifies when "
          r"printed to two decimals beside the sample size and both marginals. The third column "
          r"is algebraic and holds at every $N$. The counts are an exhaustive sweep of all "
          rf"{ref['kappa']['tables']:,} non-negative integer tables summing to $N={SIZES[-1]}$: "
          r"they reproduce exactly, but they describe that table space and not the frequency with "
          r"which a statistic identifies tables in published research, which depends on $N$ and on "
          r"the precision a source prints. \emph{Insuff.} is the paper's fourth outcome, too many "
          r"tables remaining rather than none, and is the opposite of an empty candidate set. The "
          r"prevalence and bias indices are each a function of the marginals, so each is "
          r"insufficient at every table and closes nothing on its own. Counts at $N=20$ are in "
          r"\texttt{results/statistic\_identification.json}.}",
          r"\label{tab:s1}", r"\end{table}"]
    (ROOT / "paper" / "supplement_stats.tex").write_text("\n".join(L) + "\n")
    print(f"\n  wrote paper/supplement_stats.tex from the N={SIZES[-1]} sweep")
    for r in per_size[SIZES[-1]]:
        print(f"    {r['statistic']:20} unique {r['unique']:6}  set {r['set']:6}  "
              f"insufficient {r['insufficient']:6}  undefined {r['undefined']:5}")


if __name__ == "__main__":
    main()

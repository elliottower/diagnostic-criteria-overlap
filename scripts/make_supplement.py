"""Generate the supplement's data appendix from the stored results.

The main text reports what the reconstruction found. This writes what it was
given and what it returned, per comparison, so a reader can repeat the
arithmetic without rerunning anything:

    Table S2  every eligible comparison, its printed inputs, and the cells or
              cell ranges the enumeration returned
    Table S3  the seven comparisons not attempted, with the missing input named
    Table S4  the rounding-endpoint sensitivity check

Nothing here is retyped. Every figure is read from results/*.json, which the
analysis scripts write, so the appendix cannot drift from the run that produced
it.

    python3 scripts/make_supplement.py     -> paper/supplement_tables.tex
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = ROOT / "paper" / "supplement_tables.tex"


def esc(s: str) -> str:
    for a, b in [("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")]:
        s = s.replace(a, b)
    return s


def cells(r: dict) -> str:
    """Cells, or ranges where the rounding leaves a set."""
    cr = r.get("cell_ranges")
    if not cr:
        return "---"
    out = []
    for c in ("n11", "n10", "n01", "n00"):
        lo, hi = cr[c]["min"], cr[c]["max"]
        out.append(str(lo) if lo == hi else f"{lo}--{hi}")
    return "/".join(out)


def rng(d, fmt="{:.3f}") -> str:
    if d is None:
        return "---"
    lo, hi = d["min"], d["max"]
    return fmt.format(lo) if abs(hi - lo) < 5e-4 else f"{fmt.format(lo)}--{fmt.format(hi)}"


rec = json.loads((RES / "recovery.json").read_text())
sens = json.loads((RES / "rounding_sensitivity.json").read_text())
conv = json.loads((RES / "conv2x2_comparison.json").read_text())

L: list[str] = []
A = L.append

# ---------------------------------------------------------------- Table S2
A(r"\begin{table}[htbp]")
A(r"\centering\footnotesize\setlength{\tabcolsep}{4pt}")
A(r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.1cm}>{\raggedright\arraybackslash}p{3.4cm}rrrl>{\raggedright\arraybackslash}p{3.2cm}rr@{}}")
A(r"\toprule")
A(r"Source & Criteria compared & $N$ & $n_A$ & $n_B$ & $\kappa$ & "
  r"Cells $n_{11}/n_{10}/n_{01}/n_{00}$ & Tables & $\kappa/\kappa_{\max}$ \\")
A(r"\midrule")
for r in rec["results"]:
    p = r["published"]
    star = r"$^{*}$" if r.get("kappa_provenance", "").startswith("derived") else ""
    marg = lambda side: (str(p[f"n_{side}"]) if p.get(f"n_{side}") is not None
                         else f"{p[f'p_{side}']}\\%" if p.get(f"p_{side}") is not None else "---")
    A(f"\\citet{{{r['key'].split('_')[0]}}}{star} & {esc(r['criteria'])} & {r['N']:,} & "
      f"{marg('A')} & {marg('B')} & "
      f"{p.get('kappa','---')} & {cells(r)} & {r['candidate_count']} & "
      f"{rng(r.get('kappa_over_kappa_max'), '{:.2f}')} \\\\")
A(r"\bottomrule")
A(r"\end{tabular}")
A(r"\caption{\textbf{Table S2.} Every eligible comparison, with the figures its source printed "
  r"and the integer tables those figures admit. $n_A$ and $n_B$ are the two positive marginals, as counts or as the percentages the source printed; "
  r"$\kappa$ is reproduced at the precision the source printed. The criteria column names which pair the row reports, since one source can contribute several. A range in the cells column gives "
  r"the smallest and largest value that cell takes across the surviving tables. "
  r"$\kappa/\kappa_{\max}$ is the observed $\kappa$ against the largest value the two marginals "
  r"permit \citep{umesh1989,lantz1996}. It is the same quantity as Loevinger's $H$ "
  r"\citep{loevinger1948,warrens2008association}, and equals one exactly when one of the two disagreement "
  r"cells is empty. \emph{Tables} is "
  r"the number compatible with every printed figure, so one is a unique identification and zero "
  r"means the published figures admit no common table. An asterisk marks a row whose $\kappa$ was "
  r"computed here from the source's own cells rather than published, so its validation is "
  r"circular. Generated from \texttt{results/recovery.json}.}")
A(r"\label{tab:s2}")
A(r"\end{table}")
A("")

# ---------------------------------------------------------------- Table S3
A(r"\begin{table}[htbp]")
A(r"\centering\footnotesize")
A(r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.6cm}>{\raggedright\arraybackslash}p{2.6cm}>{\raggedright\arraybackslash}p{8.2cm}@{}}")
A(r"\toprule")
A(r"Source & Condition & Why the reconstruction was not attempted \\")
A(r"\midrule")
for r in rec["insufficient_inputs"]:
    A(f"\\citet{{{r['key'].split('_')[0]}}} & {esc(r['condition'])} & {esc(r['reason'])} \\\\[2pt]")
A(r"\bottomrule")
A(r"\end{tabular}")
A(r"\caption{\textbf{Table S3.} The seven comparisons the eligibility rule excluded, with the "
  r"missing input named. Rows failing the rule are reported rather than dropped, so the "
  r"denominator in the main text is the number of comparisons located and not the number that "
  r"happened to work. Generated from \texttt{results/recovery.json}.}")
A(r"\label{tab:s3}")
A(r"\end{table}")
A("")

# ---------------------------------------------------------------- Table S4
A(r"\begin{table}[htbp]")
A(r"\centering\footnotesize")
A(r"\begin{tabular}{@{}lrrr@{}}")
A(r"\toprule")
A(r"Endpoint rule & Comparisons & Candidate tables & Sets that differ \\")
A(r"\midrule")
rules = sens.get("rules", [])
counts = sens.get("candidate_counts", {})
for rule in rules:
    n = counts.get(rule) if isinstance(counts, dict) else None
    total = sum(n.values()) if isinstance(n, dict) else (n if n is not None else "---")
    A(f"{esc(str(rule))} & {sens.get('comparisons','---')} & {total} & "
      f"{len(sens.get('comparisons_whose_set_differs', []))} \\\\")
A(r"\bottomrule")
A(r"\end{tabular}")
A(r"\caption{\textbf{Table S4.} The enumeration repeated under three rules for an exact rounding "
  r"tie: interval closed at both ends, upper bound excluded, lower bound excluded. No source "
  r"states which convention it used, so the main text reports the closed interval, which is the "
  r"union of what the conventions admit. Generated from "
  r"\texttt{results/rounding\_sensitivity.json}.}")
A(r"\label{tab:s4}")
A(r"\end{table}")

OUT.write_text("\n".join(L) + "\n")
print(f"wrote {OUT.relative_to(ROOT)}")
print(f"  Table S2: {len(rec['results'])} eligible comparisons")
print(f"  Table S3: {len(rec['insufficient_inputs'])} excluded, each with a reason")
print(f"  Table S4: {len(rules)} endpoint rules, "
      f"{len(sens.get('comparisons_whose_set_differs', []))} sets differing")

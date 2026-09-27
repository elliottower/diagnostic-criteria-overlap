"""Point reconstruction against enumeration, on 1,200 tables whose cells are known.

The comparison is in results/conv2x2_comparison.json and reaches the manuscript only
as prose. It is the paper's one direct measurement of what treating rounding as a
constraint buys over treating it as noise, so it belongs in a display.

Writes paper/table_headtohead.tex and a standalone preview.
"""
from __future__ import annotations

import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
d = json.load(open(ROOT / "results/conv2x2_comparison.json"))
P, E = d["point_reconstruction"], d["enumeration"]

ROWS = [
    ("What it returns", "one nearest table", "every compatible table"),
    ("Treats the printed digits as", "noise to be minimized", "a constraint"),
    ("Returns the source's own table",
     f"{P['exact']} of {d['tables']} ({100*P['exact_fraction']:.1f}\\%)",
     f"{E['contains_true_table']} of {d['tables']} (100\\%)"),
    ("Largest cell off by more than 1",
     f"{100*(1 - P['within_1_count']):.1f}\\% of tables", "---"),
    ("Largest cell error, median / max",
     f"{P['largest_cell_error']['median']:.0f} / {P['largest_cell_error']['max']:.0f} patients",
     "---"),
    ("Uncertainty reported alongside", "none",
     f"$n_{{11}}$ range, median width {E['n11_range_width']['median']}"),
    ("Reports that no table is compatible", "no", "yes"),
    ("Identifies the table uniquely", "not applicable",
     f"{E['uniquely_identified']} of {d['tables']} at two decimals"),
]

def main():
    L = [r"\begin{table}[htbp]", r"\centering\footnotesize",
         r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.4cm}"
         r">{\raggedright\arraybackslash}p{4.2cm}>{\raggedright\arraybackslash}p{4.6cm}@{}}",
         r"\toprule",
         r" & Point reconstruction & Enumeration \\",
         r" & \texttt{metafor::conv.2x2} & this paper \\",
         r"\midrule"]
    L += [f"{a} & {b} & {c} \\\\" for a, b, c in ROWS]
    L += [r"\bottomrule", r"\end{tabular}",
          rf"\caption{{The two treatments of printed precision, on {d['tables']:,} integer "
          r"tables whose cells are known, drawn at the sample sizes and printed precision of "
          r"this corpus. A point reconstruction minimizes the discrepancy between the printed "
          r"statistic and the recovered one and returns a single close table, with no indication "
          r"of how close. The enumeration returns every table the printed digits admit, so the "
          r"source's table is in the answer by construction, and the width of the answer is the "
          r"ambiguity the source's own reporting left. Where the quantity at issue is how many "
          r"patients were classified differently, an unstated error of up to "
          rf"{P['largest_cell_error']['max']:.0f} patients is that quantity. Generated from "
          r"\texttt{results/conv2x2\_comparison.json}.}",
          r"\label{tab:headtohead}", r"\end{table}"]
    body = "\n".join(L) + "\n"
    (ROOT / "paper" / "table_headtohead.tex").write_text(body)
    (ROOT / "paper" / "table_headtohead_preview.tex").write_text(
        "\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage{booktabs,array,amssymb,amsmath,float}\n\\pagestyle{empty}\n"
        "\\begin{document}\n" + body.replace("[htbp]", "[H]") + "\\end{document}\n")
    print(f"  {len(ROWS)} rows -> paper/table_headtohead.tex")

if __name__ == "__main__":
    main()

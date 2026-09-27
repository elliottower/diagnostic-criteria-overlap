"""Point reconstruction against enumeration, on the corpus tables whose cells are known.

results/conv2x2_comparison.json draws tables at the corpus's three largest sample
sizes, where a coefficient printed to two decimals constrains very little. That
makes its unique-identification rate incomparable with the corpus, which also
contains N = 768 and N = 7,328. This runs the same protocol on the real tables
instead: every comparison whose source printed its own cells, so the answer is known.

Both methods get the same sample size, the same marginals and the same printed
precision. conv.2x2 is given phi rounded to two decimals, the enumeration is given
kappa rounded as the source printed it.

Output: results/conv2x2_corpus.json
"""
from __future__ import annotations

import csv, json, math, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from recover_tables import enumerate_tables  # noqa: E402

OUT = ROOT / "results" / "conv2x2_corpus.json"

R = """
suppressMessages(library(metafor))
d <- read.csv("%s")
out <- data.frame()
for (i in seq_len(nrow(d))) {
  r <- d[i,]
  res <- try(conv.2x2(ri=r$phi, ni=r$n, n1i=r$n1, n2i=r$n2), silent=TRUE)
  if (inherits(res,"try-error") || is.null(res$ai) || is.na(res$ai)) {
    out <- rbind(out, data.frame(key=r$key, ai=NA, bi=NA, ci=NA, di=NA))
  } else {
    out <- rbind(out, data.frame(key=r$key, ai=res$ai, bi=res$bi, ci=res$ci, di=res$di))
  }
}
write.csv(out, "%s", row.names=FALSE)
"""


def phi(a, b, c, d):
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return (a * d - b * c) / den if den else float("nan")


def main() -> int:
    given = {}
    recs = {r["key"]: r for r in json.load(open(ROOT / "results/recovery.json"))["results"]}
    known = {k: r for k, r in recs.items() if r.get("self_test")}
    rows = []
    with tempfile.TemporaryDirectory() as td:
        inp, outp = pathlib.Path(td) / "in.csv", pathlib.Path(td) / "out.csv"
        with inp.open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["key", "n", "n1", "n2", "phi"])
            for k, r in known.items():
                c = r["self_test"]["published_cells"]
                a, b, x, d = c["n11"], c["n10"], c["n01"], c["n00"]
                # n1i and n2i are both positive marginals, one per variable (see ?conv.2x2)
                w.writerow([k, r["N"], a + b, a + x, f"{phi(a, b, x, d):.2f}"])
                given[k] = {"statistic_to_conv2x2": "phi", "phi_rounded": f"{phi(a,b,x,d):.2f}",
                            "phi_exact": round(phi(a, b, x, d), 6), "decimals": 2,
                            "conv2x2_args": {"ri": f"{phi(a,b,x,d):.2f}", "ni": r["N"],
                                             "n1i": a + b, "n2i": a + x},
                            "statistic_to_enum2x2": "unweighted Cohen kappa",
                            "kappa_as_printed": r["published"]["kappa"],
                            "enum2x2_args": {"n": r["N"], "n_a": a + b, "n_b": a + x,
                                             "kappa": r["published"]["kappa"]}}
        sc = pathlib.Path(td) / "s.R"
        sc.write_text(R % (inp, outp))
        p = subprocess.run(["Rscript", str(sc)], capture_output=True, text=True)
        if p.returncode != 0:
            print(p.stderr[-800:]); return 1
        got = {r["key"]: r for r in csv.DictReader(outp.open())}

    for k, r in known.items():
        c = r["self_test"]["published_cells"]
        true = [c["n11"], c["n10"], c["n01"], c["n00"]]
        g = got[k]
        if g["ai"] in ("NA", ""):
            pt, err, exact = None, None, False
        else:
            pt = [int(round(float(g[x]))) for x in ("ai", "bi", "ci", "di")]
            err = max(abs(p - t) for p, t in zip(pt, true))
            exact = err == 0
        cr = r["cell_ranges"]
        rows.append({
            "key": k, "condition": r["condition"], "N": r["N"],
            "true_cells": true,
            "point_reconstruction": pt, "point_largest_cell_error": err,
            "point_exact": exact,
            "enumeration_candidates": r["candidate_count"],
            "enumeration_contains_true": r["self_test"]["in_candidate_set"],
            "enumeration_n11_range": [cr["n11"]["min"], cr["n11"]["max"]],
            "inputs_supplied": given[k],
        })

    rep = {
        "question": "on the corpus tables whose cells are known, what does each method return?",
        "tables": len(rows),
        "point_exact": sum(r["point_exact"] for r in rows),
        "point_largest_cell_error_max": max((r["point_largest_cell_error"] or 0) for r in rows),
        "enumeration_contains_true": sum(r["enumeration_contains_true"] for r in rows),
        "enumeration_unique": sum(r["enumeration_candidates"] == 1 for r in rows),
        "rows": rows,
    }
    OUT.write_text(json.dumps(rep, indent=2) + "\n")
    for r in rows:
        print(f"  {r['condition']:20s} N={r['N']:>6,}  truth {r['true_cells']}  "
              f"point {r['point_reconstruction']} err {r['point_largest_cell_error']}  "
              f"enum {r['enumeration_candidates']} table(s), contains truth: "
              f"{r['enumeration_contains_true']}")
    print(f"  point exact {rep['point_exact']}/{rep['tables']}, "
          f"enumeration contains truth {rep['enumeration_contains_true']}/{rep['tables']}")
    print(f"  written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

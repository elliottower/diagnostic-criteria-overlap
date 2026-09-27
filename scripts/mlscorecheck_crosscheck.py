"""Run mlscorecheck on every comparison the enumeration was run on.

mlscorecheck (Fazekas and Kovacs) tests whether reported classifier scores can come
from any integer confusion matrix, treating each printed score as the interval its
rounding implies. It takes the exact numbers of positive and negative cases on one
side and a set of scores, kappa and accuracy among them; it has no input for the
second marginal. This runs it on each comparison with each criterion in turn as the
known side, and records how many tables it admits against how many the enumeration
admits with both marginals.

mlscorecheck narrows the (tp, tn) pairs with outward-rounded interval arithmetic, so
that it never reports a consistent result as inconsistent; its count of compatible
pairs is therefore an upper bound rather than an enumeration. The exact number of
tables the same one-marginal inputs admit is counted here in rational arithmetic, and
each table the enumeration returns is put to mlscorecheck on its own (its initial
tp and tn bounds set to that one table) to confirm the tool accepts it.

    uv run --no-project --with mlscorecheck python scripts/mlscorecheck_crosscheck.py
Output: results/mlscorecheck_crosscheck.json
"""
from __future__ import annotations

import json
import logging
import pathlib
from fractions import Fraction

import numpy as np
from mlscorecheck.individual import check_scores_tptn_pairs
from mlscorecheck.individual._check_scores_tptn import _check_scores_tptn_pairs

from recover_tables import enumerate_tables

logging.disable(logging.CRITICAL)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "mlscorecheck_crosscheck.json"


def half_unit(printed: str) -> Fraction:
    decimals = len(printed.split(".")[1]) if "." in printed else 0
    return Fraction(1, 2 * 10 ** decimals)


def kappa_acc(tp: int, tn: int, p: int, n: int) -> tuple[Fraction, Fraction]:
    N = p + n
    fp = n - tn
    po = Fraction(tp + tn, N)
    pe = Fraction(p, N) * Fraction(tp + fp, N) + Fraction(n, N) * Fraction(N - tp - fp, N)
    return (po - pe) / (1 - pe) if pe != 1 else Fraction(0), po


def one_marginal_tables(p: int, n: int, kappa: str, acc: str | None) -> list[tuple[int, int]]:
    """Every (tp, tn) matching the printed kappa (and agreement), with only p and n fixed.

    A float pass over the whole grid keeps anything within a widened interval, and each
    survivor is then decided in exact rational arithmetic.
    """
    k0, kh = Fraction(kappa), half_unit(kappa)
    if acc is not None:
        a0, ah = Fraction(acc) / 100, half_unit(acc) / 100
    N = p + n
    tn = np.arange(n + 1, dtype=float)
    out = []
    for tp in range(p + 1):
        pred_pos = tp + n - tn
        po = (tp + tn) / N
        pe = (p / N) * (pred_pos / N) + (n / N) * ((N - pred_pos) / N)
        with np.errstate(divide="ignore", invalid="ignore"):
            k = np.where(pe != 1, (po - pe) / (1 - pe), 0.0)
        keep = np.abs(k - float(k0)) <= float(kh) + 1e-9
        if acc is not None:
            keep &= np.abs(po - float(a0)) <= float(ah) + 1e-9
        for t in np.nonzero(keep)[0]:
            ke, ae = kappa_acc(tp, int(t), p, n)
            if abs(ke - k0) <= kh and (acc is None or abs(ae - a0) <= ah):
                out.append((tp, int(t)))
    return out


def run(label: str, N: int, n_a: int | None, n_b: int | None, kappa: str, acc: str | None,
        ours: list[tuple[int, int, int, int]]) -> dict:
    row = {"comparison": label, "N": N, "n_A": n_a, "n_B": n_b, "kappa": kappa, "agreement": acc,
           "enumeration_tables": len(ours)}
    if n_a is None or n_b is None:
        row["mlscorecheck"] = "not run: the marginals are printed as percentages, and it needs exact counts"
        return row
    sides = {}
    for side, p in (("A known", n_a), ("B known", n_b)):
        n = N - p
        scores = {"kappa": float(kappa)} | ({"acc": float(acc) / 100} if acc else {})
        eps = {"kappa": float(half_unit(kappa))} | ({"acc": float(half_unit(acc)) / 100} if acc else {})
        r = check_scores_tptn_pairs(p=p, n=n, scores=scores, eps=eps)
        exact = one_marginal_tables(p, n, kappa, acc)
        # (tp, tn) is (n11, n00) whichever criterion is taken as the known side
        ours_here = [(a, d) for a, b, c, d in ours]
        accepted = [not _check_scores_tptn_pairs(
                        p=p, n=n, scores=scores, eps=eps,
                        init_tptn_intervals={"tp": (a, a), "tn": (d, d)})["inconsistency"]
                    for a, d in ours_here]
        sides[side] = {
            "one_marginal_tables_exact": len(exact),
            "mlscorecheck_reported_pairs": r["n_valid_tptn_pairs"],
            "mlscorecheck_inconsistency": r["inconsistency"],
            "mlscorecheck_count_at_least_exact": r["n_valid_tptn_pairs"] >= len(exact),
            "enumeration_tables_among_exact": all(t in exact for t in ours_here),
            "mlscorecheck_accepts_every_enumeration_table": all(accepted),
        }
    row["mlscorecheck"] = sides
    row["one_marginal_fewest_tables"] = min(s["one_marginal_tables_exact"] for s in sides.values())
    return row


def main() -> int:
    rows = []
    inputs = json.loads((ROOT / "experiments/table_recovery/inputs.json").read_text())
    for r in json.loads((ROOT / "results/recovery.json").read_text())["results"]:
        row = inputs[r["key"]]
        tabs = enumerate_tables(row)
        ours = [(t["cells"]["n11"], t["cells"]["n10"], t["cells"]["n01"], t["cells"]["n00"]) for t in tabs]
        rows.append(run(r["key"], row["N"], row.get("n_A"), row.get("n_B"), row["kappa"], row.get("p_o"), ours))

    v = json.loads((ROOT / "results/valencia_recovery.json").read_text())
    vi = v["published_inputs"]
    ours = [(c["cells"]["n11"], c["cells"]["n10"], c["cells"]["n01"], c["cells"]["n00"]) for c in v["candidates"]]
    rows.append(run("valencia2024", vi["N"], vi["n_A"], vi["n_B"], vi["kappa"], None, ours))

    g = json.loads((ROOT / "results/goyal_all_pairs.json").read_text())
    for r in g["rows"]:
        c = r["cells"]
        rows.append(run(f"goyal2025 {r['a']} / {r['b']}", g["N"], r["n_a"], r["n_b"], str(r["kappa"]), None,
                        [(c["n11"], c["n10"], c["n01"], c["n00"])]))

    ran = [x for x in rows if isinstance(x["mlscorecheck"], dict)]
    summary = {
        "comparisons": len(rows),
        "mlscorecheck_run": len(ran),
        "not_run_percent_marginals": [x["comparison"] for x in rows if not isinstance(x["mlscorecheck"], dict)],
        "mlscorecheck_count_never_below_exact": all(
            s["mlscorecheck_count_at_least_exact"] for x in ran for s in x["mlscorecheck"].values()),
        "mlscorecheck_accepts_every_enumeration_table": all(
            s["mlscorecheck_accepts_every_enumeration_table"] for x in ran for s in x["mlscorecheck"].values()),
        "enumeration_tables_always_among_one_marginal_tables": all(
            s["enumeration_tables_among_exact"] for x in ran for s in x["mlscorecheck"].values()),
        "one_marginal_unique_either_side": sum(x["one_marginal_fewest_tables"] == 1 for x in ran),
        "enumeration_unique": sum(x["enumeration_tables"] == 1 for x in ran),
    }
    OUT.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n")

    print(json.dumps(summary, indent=1))
    for x in rows[:10]:
        m = x["mlscorecheck"]
        tag = m if isinstance(m, str) else (f"one marginal: {m['A known']['one_marginal_tables_exact']} (A) / "
                                            f"{m['B known']['one_marginal_tables_exact']} (B)   mlscorecheck reports "
                                            f"{m['A known']['mlscorecheck_reported_pairs']} / {m['B known']['mlscorecheck_reported_pairs']}")
        print(f"  {x['comparison']:24s} enumeration {x['enumeration_tables']:>3}   {tag}")
    print(f"  written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""How many of Goyal's 55 comparisons survive under each rounding convention?

`goyal_all_pairs.py` reads every printed figure as round-half-up, which is what
enum2x2 assumes by default. Fifteen of the 55 comparisons then have no compatible
table: the disagreement percentage in Figure 2 lies outside the half-up interval
around the percentage the recovered table actually has, and is inside the interval
a truncating source would have printed.

This re-runs all 55 under each of the three conventions enum2x2 now takes. The
disagreement percentage is applied to the discordant proportion directly rather
than to its complement: under half-up the two are the same constraint, but a
truncated disagreement of "14.7" means [14.7, 14.8), whose complement is
(85.2, 85.3] and not the truncation interval around "85.3".

The daghi2026 row is re-run alongside, because its infeasibility is a result the
manuscript reports and a convention must not be able to talk it away.

Writes results/goyal_convention_sensitivity.json.
"""
from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SIBLING = PROJECT_ROOT.parent / "enum2x2" / "src"
if _SIBLING.is_dir():
    sys.path.insert(0, str(_SIBLING))

from enum2x2 import CONVENTIONS, exact_kappa, exactly_rounds_to, recover

N = 353
PAIRS = PROJECT_ROOT / "results" / "goyal_all_pairs.json"
OUT = PROJECT_ROOT / "results" / "goyal_convention_sensitivity.json"

# daghi2026, as registered in experiments/table_recovery/inputs.json.
DAGHI = dict(n=370, p_a="44.6", p_b="43.2", kappa="0.48", agreement="73",
             marginals_as_percent=True, agreement_as_percent=True)


def tables_for(row: dict, convention: str) -> list[dict]:
    """Tables compatible with both the kappa and the disagreement percentage."""
    r = recover(n=N, n_a=row["n_a"], n_b=row["n_b"], kappa=row["kappa"],
                convention=convention)
    return [t.as_dict() for t in r
            if exactly_rounds_to(Fraction(t.n10 + t.n01, N),
                                 row["disagreement_percent"],
                                 as_percent=True, convention=convention)]


def which_conventions(value: Fraction, printed: str, as_percent: bool) -> str:
    """Which readings of this printed figure admit the value the table produced."""
    half_up = exactly_rounds_to(value, printed, as_percent=as_percent,
                                convention="half_up")
    truncate = exactly_rounds_to(value, printed, as_percent=as_percent,
                                 convention="truncate")
    if half_up and truncate:
        return "either"
    return ("half_up only" if half_up
            else "truncate only" if truncate else "neither")


def main() -> int:
    pairs = json.loads(PAIRS.read_text())
    rows = pairs["rows"]
    assert pairs["N"] == N and len(rows) == pairs["pairs"] == 55

    per_row, summary = [], {}
    for convention in CONVENTIONS:
        nonempty = unique = 0
        for i, row in enumerate(rows):
            got = tables_for(row, convention)
            nonempty += bool(got)
            unique += len(got) == 1
            if convention == CONVENTIONS[0]:
                per_row.append({"a": row["a"], "b": row["b"], "n_a": row["n_a"],
                                "n_b": row["n_b"], "kappa": row["kappa"],
                                "disagreement_percent": row["disagreement_percent"],
                                "tables": {}})
            per_row[i]["tables"][convention] = got
        summary[convention] = {"non_empty": nonempty, "unique": unique,
                               "empty": len(rows) - nonempty}

    # The stored file applied the disagreement as its complement through the
    # `agreement` argument. Under half-up that is the same constraint, so the two
    # routes must agree; if they do not, one of them is wrong.
    complement = sum(
        1 for row in rows
        if recover(n=N, n_a=row["n_a"], n_b=row["n_b"], kappa=row["kappa"],
                   agreement=f"{100 - float(row['disagreement_percent']):.1f}",
                   agreement_as_percent=True))

    # Kappa alone identifies one table for all 55 pairs, so each printed figure
    # can be held against the value that table actually has and asked which
    # readings of the figure admit it.
    produced_by = {"kappa": {}, "disagreement_percent": {}}
    for row, out in zip(rows, per_row):
        cells = row["cells"]
        for name, value, printed, pct in (
                ("kappa", exact_kappa(**cells), row["kappa"], False),
                ("disagreement_percent", Fraction(cells["n10"] + cells["n01"], N),
                 row["disagreement_percent"], True)):
            verdict = which_conventions(value, printed, pct)
            out[f"{name}_produced_by"] = verdict
            produced_by[name][verdict] = produced_by[name].get(verdict, 0) + 1

    daghi = {}
    for convention in CONVENTIONS:
        r = recover(**DAGHI, convention=convention)
        daghi[convention] = {"status": r.status, "candidates": len(r),
                             "reason": r.reason,
                             "tables": [t.as_dict() for t in r]}

    out = {"source": "goyal2025, Table 3 and Figure 2; daghi2026 Table 2",
           "N": N, "pairs": len(rows),
           "constraints": "kappa and the disagreement percentage, both as printed",
           "summary": summary,
           "figures_produced_by": produced_by,
           "half_up_via_complement_agreement": complement,
           "stored_half_up_unique": pairs["unique_from_kappa_and_disagreement"],
           "stored_half_up_empty": pairs["empty_candidate_set"],
           "daghi2026": {"inputs": DAGHI, "by_convention": daghi},
           "rows": per_row}
    OUT.write_text(json.dumps(out, indent=2) + "\n")

    print(f"  {'convention':<12} {'non-empty':>10} {'unique':>8} {'empty':>7}")
    for convention, s in summary.items():
        print(f"  {convention:<12} {s['non_empty']:>10} {s['unique']:>8} {s['empty']:>7}")
    for name, counts in produced_by.items():
        print(f"\n  printed {name}, readings that admit the recovered value")
        for verdict, k in sorted(counts.items()):
            print(f"    {verdict:<14} {k:>3}")
    print(f"\n  half-up via the complement agreement: {complement} non-empty "
          f"(stored: {pairs['unique_from_kappa_and_disagreement']} unique, "
          f"{pairs['empty_candidate_set']} empty)")
    print("\n  daghi2026")
    for convention, d in daghi.items():
        print(f"    {convention:<10} {d['status']:<12} {d['candidates']} table(s)"
              f"   {d['reason'] or ''}")
    print(f"\n  written to {OUT.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

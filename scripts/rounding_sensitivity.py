"""Does the result depend on how an exact rounding tie is resolved?

The analysis treats a printed figure as the closed interval of values that round
to it, closed at both ends because sources do not state the convention they used.
That is a superset of what any one convention admits, chosen so that a table
cannot be dropped by guessing wrong.

The choice is only conservative if it changes nothing, and whether it changes
nothing is a question about this corpus rather than about the method. This re-runs
every eligible comparison under three endpoint rules and compares the results:

    closed      [lo, hi]   both ends admitted; the primary analysis
    half-up     [lo, hi)   a tie rounds away from zero, so the top is excluded
    half-down   (lo, hi]   a tie rounds toward zero, so the bottom is excluded

Written to results/rounding_sensitivity.json.
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

from enum2x2._core import exact_interval, exact_kappa

RULES = {"closed": (True, True), "half_up": (True, False), "half_down": (False, True)}


def compatible(n: int, a_counts, b_counts, kappa: str, agreement, agree_pct, rule):
    lo_in, hi_in = RULES[rule]

    def inside(value, printed, as_percent=False):
        lo, hi = exact_interval(printed, as_percent)
        return (lo <= value if lo_in else lo < value) and \
               (value <= hi if hi_in else value < hi)

    out = []
    for n_a in a_counts:
        for n_b in b_counts:
            if n * n == n_a * n_b + (n - n_a) * (n - n_b):
                continue
            for n11 in range(max(0, n_a + n_b - n), min(n_a, n_b) + 1):
                n10, n01 = n_a - n11, n_b - n11
                n00 = n - n11 - n10 - n01
                if n00 < 0:
                    continue
                if not inside(exact_kappa(n11, n10, n01, n00), kappa):
                    continue
                if agreement is not None and not inside(
                        Fraction(n11 + n00, n), agreement, agree_pct):
                    continue
                out.append((n11, n10, n01, n00))
    return out


def counts_for(printed, n, as_percent, rule):
    lo_in, hi_in = RULES[rule]
    lo, hi = exact_interval(printed, as_percent)
    return [c for c in range(n + 1)
            if (lo <= Fraction(c, n) if lo_in else lo < Fraction(c, n))
            and (Fraction(c, n) <= hi if hi_in else Fraction(c, n) < hi)]


def main() -> int:
    rows = json.loads((PROJECT_ROOT / "experiments" / "table_recovery"
                       / "inputs.json").read_text())
    per_rule, keys = {}, []
    for rule in RULES:
        got = {}
        for key, row in rows.items():
            if key == "_README" or row.get("status") != "recover":
                continue
            n, pct = row["N"], row.get("marginals_as_percent", False)
            a = ([row["n_A"]] if row.get("n_A") is not None
                 else counts_for(row["p_A"], n, pct, rule))
            b = ([row["n_B"]] if row.get("n_B") is not None
                 else counts_for(row["p_B"], n, pct, rule))
            got[key] = compatible(n, a, b, row["kappa"], row.get("p_o"),
                                  row.get("p_o_as_percent", False), rule)
        per_rule[rule] = got
        keys = list(got)

    differences = [k for k in keys
                   if len({tuple(sorted(per_rule[r][k])) for r in RULES}) > 1]
    report = {
        "rules": {r: "".join(("[" if RULES[r][0] else "(", "lo, hi",
                              "]" if RULES[r][1] else ")")) for r in RULES},
        "comparisons": len(keys),
        "candidate_counts": {r: {k: len(v) for k, v in per_rule[r].items()} for r in RULES},
        "comparisons_whose_set_differs": differences,
        "invariant": not differences,
    }
    path = PROJECT_ROOT / "results" / "rounding_sensitivity.json"
    path.write_text(json.dumps(report, indent=2) + "\n")

    print(f"  {len(keys)} comparisons under three endpoint rules")
    for r in RULES:
        print(f"    {r:10s} {report['rules'][r]:12s} "
              f"candidate counts {sorted(report['candidate_counts'][r].values())}")
    print(f"  sets differing between rules: {differences or 'none'}")
    print(f"  written to {path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

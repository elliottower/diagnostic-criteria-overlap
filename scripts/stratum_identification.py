"""Does the identification identity extend to the two-by-four table?

A comparative accuracy study applies two index tests and a reference standard to the
same patients. The resulting two-by-four table is two 2x2 tables, one per reference
stratum. Within a stratum the two sensitivities (or specificities) fix the row and
column totals, leaving one degree of freedom -- the same position this paper's corpus
is in. A published McNemar statistic for that stratum fixes the discordant sum, and
the marginals already fix the discordant difference.

Measured over random two-by-four tables rather than asserted. Writes
results/stratum_identification.json.
"""
from __future__ import annotations

import json
import pathlib
import random
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent.parent


def mcnemar_chisq(b: int, c: int) -> Fraction | None:
    """Uncorrected McNemar chi-square on the discordant cells; None when both are zero."""
    return None if b + c == 0 else Fraction((b - c) ** 2, b + c)


def stratum_candidates(s: int, row: int, col: int, chisq: Fraction | None) -> list[tuple]:
    """Every (a, b, c, d) with the given stratum size, row total, column total, chi-square."""
    out = []
    for a in range(min(row, col) + 1):
        b, c = row - a, col - a
        d = s - a - b - c
        if b < 0 or c < 0 or d < 0:
            continue
        if mcnemar_chisq(b, c) == chisq:
            out.append((a, b, c, d))
    return out


def main() -> None:
    random.seed()
    trials = 4000
    with_mcnemar, without_mcnemar = [], []
    equal_marginal_cases = 0
    equal_marginal_candidates = []

    for _ in range(trials):
        # A random diseased stratum of a two-by-four table.
        cells = [random.randint(0, 40) for _ in range(4)]
        s = sum(cells)
        if s == 0:
            continue
        a, b, c, d = cells
        row, col = a + b, a + c            # what the two sensitivities publish
        chisq = mcnemar_chisq(b, c)

        got = stratum_candidates(s, row, col, chisq)
        with_mcnemar.append(len(got))
        # Without the McNemar statistic, only the marginals constrain the stratum.
        loose = [t for t in stratum_candidates(s, row, col, None)] or []
        loose = [(x, row - x, col - x, s - (row - x) - (col - x) - x)
                 for x in range(min(row, col) + 1)
                 if s - (row - x) - (col - x) - x >= 0]
        without_mcnemar.append(len(loose))

        if b == c:                          # equal sensitivities: chi-square is 0
            equal_marginal_cases += 1
            equal_marginal_candidates.append(len(got))

    def summarize(xs):
        return {"n": len(xs), "mean": round(sum(xs) / len(xs), 3),
                "max": max(xs), "fraction_unique": round(sum(x == 1 for x in xs) / len(xs), 4)}

    out = {
        "what_this_measures": (
            "Within one reference stratum of a two-by-four table, whether the stratum size, "
            "both index-test marginals (i.e. both sensitivities) and a published McNemar "
            "chi-square identify the stratum's four cells."),
        "trials": trials,
        "marginals_only": summarize(without_mcnemar),
        "marginals_plus_mcnemar_chisq": summarize(with_mcnemar),
        "singular_case_equal_marginals": {
            "description": (
                "When the two sensitivities are equal the discordant cells are equal, the "
                "chi-square is 0 for every discordant total, and the statistic adds nothing."),
            "cases": equal_marginal_cases,
            "candidates": summarize(equal_marginal_candidates) if equal_marginal_candidates else None},
    }
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results/stratum_identification.json", "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

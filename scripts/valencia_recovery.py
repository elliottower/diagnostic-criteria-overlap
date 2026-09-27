"""Recover the joint table behind a sarcopenia comparison located after the freeze.

\\citet{valencia2024} compare the EWGSOP1 and EWGSOP2 criteria in 67 women with
rheumatoid arthritis. The article prints both positive counts, $\\kappa$, and the
statement that every patient EWGSOP2 identifies is also identified by EWGSOP1, and
no joint classification. The enumeration is given only the counts and $\\kappa$; the
containment is held out, so the zero cell is a prediction the article's own prose
checks.

Output: results/valencia_recovery.json
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from recover_tables import enumerate_tables  # noqa: E402

OUT = ROOT / "results" / "valencia_recovery.json"

# Front Med (Lausanne) 2024;11:1392604, Results: "43.3% (29/67) ... 16.4% (11/67)"
# and "a Cohen's kappa coefficient of 0.409".
PUBLISHED = {"N": 67, "n_A": 29, "n_B": 11, "kappa": "0.409"}

# Held out of the enumeration, used only to check what it returns:
# "All patients diagnosed with sarcopenia under EWGSOP-2 criteria also met the
# EWGSOP-1 criteria for sarcopenia."
HELD_OUT_CONTAINMENT = "n01 == 0"


def main() -> int:
    tables = enumerate_tables(PUBLISHED)
    report = {
        "source": "valencia2024",
        "comparison": "EWGSOP1 against EWGSOP2, sarcopenia in rheumatoid arthritis",
        "published_inputs": PUBLISHED,
        "held_out": {"claim": HELD_OUT_CONTAINMENT,
                     "quotation": "All patients diagnosed with sarcopenia under EWGSOP-2 "
                                  "criteria also met the EWGSOP-1 criteria for sarcopenia."},
        "candidate_count": len(tables),
        "candidates": tables,
        "every_candidate_nests": all(t["cells"]["n01"] == 0 for t in tables) if tables else False,
        "kappa_over_kappa_max": [t["kappa"] / t["kappa_max"] for t in tables],
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")

    print(f"  inputs: N={PUBLISHED['N']}, n_A={PUBLISHED['n_A']}, n_B={PUBLISHED['n_B']}, "
          f"kappa={PUBLISHED['kappa']}")
    print(f"  candidate tables: {len(tables)}")
    for t in tables:
        c = t["cells"]
        print(f"    {c['n11']}/{c['n10']}/{c['n01']}/{c['n00']}  kappa={t['kappa']:.4f}  "
              f"agreement={t['p_o']:.4f}  kappa/kappa_max={t['kappa'] / t['kappa_max']:.3f}")
    print(f"  held-out containment reproduced: {report['every_candidate_nests']}")
    print(f"  written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

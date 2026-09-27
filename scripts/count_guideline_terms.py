"""Compute the two tables in criterion_agreement_v2.tex that are derived rather than quoted.

Table 1  term counts in the GRRAS and STARD checklist items
Table 4  criterion-level kappa corrected for the rater-level floor

Both are written to results/ as JSON before anything is printed, so a crash in
formatting cannot lose the computation. The artifacts read here are the pinned
copies under reference/, hashed in reference/FETCH_LOG.json; the hash of each is
recorded in the output so a table and its provenance travel together.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import pathlib
import re

from _artifacts import artifacts_dir

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFERENCE = artifacts_dir()
OUT = ROOT / "results"

TERMS = [
    "reference standard", "index test", "diagnostic accuracy", "sensitivity",
    "specificity", "rater", "reliability", "agreement", "replicate",
    "repeated measurement",
]

# Table 4. Each row names the floor's provenance so a borrowed floor is visible.
# reliability 1.0 marks a criterion applied algorithmically to recorded fields,
# which has no rater and therefore no rater-induced error.
FLOOR_ROWS = [
    {
        "condition": "Multiple sclerosis",
        "comparison": "neurologist label against trial definition",
        "kappa": 0.22, "kappa_source": "guerra2026",
        "reliability_x": 0.545, "reliability_x_source": "zipoli2003 (0.52-0.57, four neurologists, 44 cases)",
        "reliability_y": 1.0, "reliability_y_source": "algorithmic on registry fields; no rater",
        "floor_borrowed_across_studies": True,
    },
    {
        "condition": "Multiple sclerosis",
        "comparison": "McDonald 2017 against McDonald 2024",
        "kappa": 0.65, "kappa_source": "mahmoudi2026",
        "reliability_x": 0.77, "reliability_x_source": "mahmoudi2026 (0.70-0.84, three readers)",
        "reliability_y": 0.77, "reliability_y_source": "mahmoudi2026, same readers, same study",
        "floor_borrowed_across_studies": False,
    },
    {
        "condition": "Stroke",
        "comparison": "TOAST against CCS",
        "kappa": 0.59, "kappa_source": "mcardle2014",
        "reliability_x": None, "reliability_x_source": "none published for TOAST",
        "reliability_y": None, "reliability_y_source": "none published for CCS",
        "floor_borrowed_across_studies": False,
        "note": "zhang2019 publishes 0.857 for CISS inter-rater. CISS is in neither "
                "side of this comparison, so substituting it is not licensed.",
    },
]


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_xml(raw: str) -> str:
    raw = re.sub(r"<[^>]+>", "\n", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


def grras_items(path: pathlib.Path) -> str:
    """GRRAS Table 1, from the checklist PDF's extracted text. Items only.

    NOT kottner2011.txt: scripts/render_text.py regenerates that file from the
    PubMed XML, which carries the abstract and none of the fifteen items.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.find("Identify in title or abstract")
    if start < 0:
        raise ValueError(f"GRRAS item list not found in {path}")
    return re.sub(r"\s+", " ", text[start:])


def stard_items(path: pathlib.Path) -> str:
    """STARD 2015 item list, from the pinned Europe PMC full text."""
    text = strip_xml(path.read_text(encoding="utf-8", errors="replace"))
    start = text.find("Identification as a study of diagnostic accuracy")
    end = text.find("Registration number and name of registry")
    if start < 0 or end <= start:
        raise ValueError(f"STARD item list not found in {path}")
    return text[start:end + 60]


def disattenuate(kappa: float, rel_x: float, rel_y: float) -> float:
    return kappa / math.sqrt(rel_x * rel_y)


def main() -> None:
    OUT.mkdir(exist_ok=True)

    grras_path = REFERENCE / "kottner2011.checklist.txt"
    stard_path = REFERENCE / "bossuyt2015.xml"
    grras = grras_items(grras_path)
    stard = stard_items(stard_path)

    table1 = {
        "description": "Term counts in the GRRAS and STARD checklist items",
        "sources": {
            "grras": {
                "citation": "kottner2011", "file": grras_path.name,
                "sha256": sha256(grras_path), "n_items": 15,
                "scope": "Table 1 checklist items only, not the surrounding paper",
            },
            "stard": {
                "citation": "bossuyt2015", "file": stard_path.name,
                "sha256": sha256(stard_path), "n_items": 30,
                "scope": "the 30-item checklist only, not the surrounding paper",
            },
        },
        "counts": {
            term: {
                "grras": len(re.findall(term, grras, re.I)),
                "stard": len(re.findall(term, stard, re.I)),
            }
            for term in TERMS
        },
    }
    table1["vocabularies_disjoint"] = all(
        c["grras"] == 0 or c["stard"] == 0 for c in table1["counts"].values()
    )

    rows = []
    for row in FLOOR_ROWS:
        out = dict(row)
        if row["reliability_x"] is None or row["reliability_y"] is None:
            out["kappa_corrected"] = None
            out["computable"] = False
        else:
            out["kappa_corrected"] = round(
                disattenuate(row["kappa"], row["reliability_x"], row["reliability_y"]), 3)
            out["computable"] = True
        rows.append(out)

    table4 = {
        "description": "Criterion-level kappa corrected for the rater-level floor",
        "formula": "kappa_corrected = kappa / sqrt(reliability_x * reliability_y)",
        "formula_source": "spearman1904",
        "caveat": "Derived for product-moment correlations between continuous measures. "
                  "Applied to kappa it is an approximation sensitive to prevalence and "
                  "to the marginal distributions.",
        "rows": rows,
        "n_pairs_in_distribution": 12,
        "n_pairs_with_any_floor": 3,
        "n_pairs_correctable": sum(1 for r in rows if r["computable"]),
    }

    (OUT / "table1_guideline_terms.json").write_text(json.dumps(table1, indent=2) + "\n")
    (OUT / "table4_floor_correction.json").write_text(json.dumps(table4, indent=2) + "\n")

    print("wrote results/table1_guideline_terms.json")
    print("     results/table4_floor_correction.json")
    print()
    print("%-22s %10s %10s" % ("term", "GRRAS(15)", "STARD(30)"))
    print("-" * 44)
    for term, c in table1["counts"].items():
        print("%-22s %10d %10d" % (term, c["grras"], c["stard"]))
    print()
    print("vocabularies disjoint:", table1["vocabularies_disjoint"])
    print()
    for r in rows:
        corrected = "not computable" if r["kappa_corrected"] is None else "%.3f" % r["kappa_corrected"]
        print("  %-20s %-38s kappa %.2f -> %s"
              % (r["condition"], r["comparison"], r["kappa"], corrected))


if __name__ == "__main__":
    main()

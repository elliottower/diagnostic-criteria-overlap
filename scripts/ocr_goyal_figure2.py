"""Read Goyal Figure 2 with OCR, and check it against the hand transcription.

Figure 2 is a matrix image: each cell carries Cohen's kappa above a disagreement
percentage. scripts/goyal_all_pairs.py transcribes it by eye. This recognises the
same figure with Apple's Vision framework and asserts the two agree, so the
transcription is not taken on trust.

    swiftc -O scripts/ocr/VisionOCR.swift -o scripts/ocr/visionocr
    python3 scripts/ocr_goyal_figure2.py <page4.png>

Writes results/goyal_figure2_ocr.json.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OCR = ROOT / "scripts" / "ocr" / "visionocr"
CAPTION_Y = 0.50          # everything below this is the caption and Table 3
ORDER = ["IADPSG 2010", "NICE 2015", "DIPSI 2009", "WHO 1999", "CDA 2013",
         "ADIPS 1998", "EASD 1996", "NZSSD 2004", "CDA 2003", "ADA 2004", "JSOG 1984"]


def recognise(png: pathlib.Path) -> list[tuple[str, float, float]]:
    out = subprocess.run([str(OCR), str(png)], capture_output=True, text=True, check=True).stdout
    toks = []
    for line in out.splitlines():
        p = line.split("\t")
        if len(p) == 6:
            toks.append((p[0], float(p[1]), float(p[2])))
    return toks


def cluster(values: list[float], tol: float) -> list[float]:
    """Centres of groups of coordinates lying within tol of one another."""
    out = []
    for v in sorted(values):
        if out and v - out[-1][-1] <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(g) / len(g) for g in out]


def main() -> None:
    png = pathlib.Path(sys.argv[1])
    toks = [t for t in recognise(png) if t[2] > CAPTION_Y]
    kappa = [t for t in toks if re.fullmatch(r"[01]\.\d{3}", t[0])]
    pct = [t for t in toks if re.fullmatch(r"\d{1,2}\.\d%|0%", t[0])]

    cols = cluster([t[1] for t in kappa], 0.03)
    rows = cluster([t[2] for t in kappa], 0.01)
    rows.sort(reverse=True)                       # Vision origin is bottom left

    def nearest(seq, v):
        return min(range(len(seq)), key=lambda i: abs(seq[i] - v))

    grid: dict[tuple[int, int], dict] = {}
    for text, x, y in kappa:
        grid[(nearest(rows, y), nearest(cols, x))] = {"kappa": text}
    for text, x, y in pct:
        # the percentage sits just under its kappa
        r = nearest(rows, y + 0.011)
        key = (r, nearest(cols, x))
        if key in grid:
            grid[key]["disagreement_percent"] = text.rstrip("%")

    # The matrix is upper triangular: column positions are absolute, so column j
    # is ORDER[j + 1], and row i carries cells only for j >= i.
    read = {}
    for (r, c), cell in sorted(grid.items()):
        if r >= len(ORDER) - 1 or c + 1 >= len(ORDER) or c < r:
            continue
        a, b = ORDER[r], ORDER[c + 1]
        if "disagreement_percent" in cell:
            read[f"{a} | {b}"] = (cell["kappa"], cell["disagreement_percent"])

    hand = {}
    src = (ROOT / "scripts" / "goyal_all_pairs.py").read_text()
    fig = eval(src[src.index("FIG2 = {") + len("FIG2 = "):src.index("# Table 3 repeats")].strip())
    for ai, a in enumerate(ORDER):
        for j, b in enumerate(ORDER[ai + 1:]):
            if a in fig and j < len(fig[a]):
                hand[f"{a} | {b}"] = fig[a][j]

    # Vision sometimes drops a cell at page scale. Re-read each missing cell from a
    # magnified crop of its row band before reporting it as unrecognised.
    recovered = {}
    if rows:
        band = (rows[0] - rows[1]) / 2 if len(rows) > 1 else 0.02
        im = Image.open(png)
        W, H = im.size
        for key in [k for k in hand if k not in read]:
            a = key.split(" | ")[0]
            r = ORDER.index(a)
            if r >= len(rows):
                continue
            y = rows[r]
            box = (int(0.10 * W), int((1 - (y + band)) * H), W, int((1 - (y - band)) * H))
            crop = im.crop(box)
            crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
            tmp = png.with_name(f"_row{r}.png")
            crop.save(tmp)
            toks_r = recognise(tmp)
            tmp.unlink()
            ks = [x for x in toks_r if re.fullmatch(r"[01]\.\d{3}", x[0])]
            ps = [x for x in toks_r if re.fullmatch(r"\d{1,2}\.\d%|0%", x[0])]
            ks.sort(key=lambda x: x[1])
            ps.sort(key=lambda x: x[1])
            b = key.split(" | ")[1]
            c = ORDER.index(b) - 1
            idx = c - r
            if 0 <= idx < len(ks) and idx < len(ps):
                read[key] = (ks[idx][0], ps[idx][0].rstrip("%"))
                recovered[key] = "magnified row crop"

    agree = [k for k in hand if k in read and read[k] == hand[k]]
    differ = {k: {"ocr": read[k], "hand": hand[k]} for k in hand if k in read and read[k] != hand[k]}
    missed = [k for k in hand if k not in read]

    json.dump({"png": str(png), "cells_recognised": len(read), "cells_hand": len(hand),
               "agree": len(agree), "differ": differ, "not_recognised": missed,
               "recovered_by_crop": recovered},
              open(ROOT / "results/goyal_figure2_ocr.json", "w"), indent=2)
    print(f"  hand transcription   {len(hand)} cells")
    print(f"  OCR recognised       {len(read)} cells")
    print(f"  agree                {len(agree)}")
    print(f"  differ               {len(differ)}")
    for k, v in differ.items():
        print(f"      {k}: ocr {v['ocr']}  hand {v['hand']}")
    print(f"  recovered by crop    {len(recovered)}")
    print(f"  not recognised       {len(missed)}  {missed if missed else ''}")


if __name__ == "__main__":
    main()

"""Render each retrieved record to plain text, which is what quotations are checked against.

The XML is the artifact as retrieved and keeps its own sha256. It cannot be searched directly:
PubMed and Europe PMC encode Greek letters and mathematical symbols as character entities, so
`α-synuclein` in a quotation and `&#x03B1;-synuclein` in the file do not match, and a quotation
that is genuinely present reads as absent. This step unescapes entities and strips markup,
leaving the words in document order.

Both files are kept and both hashes recorded, so the text a quotation resolved against can be
regenerated from the record that was downloaded.
"""
from __future__ import annotations

import hashlib
import html
import json
import pathlib
import re

from _artifacts import artifacts_dir

ROOT = pathlib.Path(__file__).resolve().parent.parent
REF = artifacts_dir()
LEDGER = ROOT / "reference" / "FETCH_LOG.json"

# Tags whose content is markup rather than prose. Dropping the element, not just its angle
# brackets, keeps reference lists and formula markup out of the searchable text.
DROP = re.compile(r"<(ref-list|back|graphic|inline-formula|disp-formula|tex-math)\b.*?</\1>", re.S)
BLOCK = re.compile(r"</(p|title|abstract|sec|AbstractText|ArticleTitle|caption|td|tr|li)>", re.I)


def render(raw: str) -> str:
    s = DROP.sub(" ", raw)
    s = BLOCK.sub("\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(html.unescape(s))     # &amp;#x03B1; occurs in some records
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip() + "\n"


def _is_our_output(ledger: dict, out: pathlib.Path) -> bool:
    """True when `out` is a previous run's product, so overwriting it loses nothing.

    A file this script did not write is hand-extracted from a source it cannot
    reach -- a checklist table inside a PDF, say -- and regenerating the key from
    its XML would replace the only copy with an abstract. That happened once, to
    the GRRAS checklist; the guard exists because of it.
    """
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    return any(rec.get("file") == out.name
               and rec.get("extract_cmd") == "python3 scripts/render_text.py"
               and rec.get("sha256") == digest
               for rec in ledger.values())


def main() -> None:
    ledger = json.loads(LEDGER.read_text())
    made = 0
    skipped = 0
    for key, rec in sorted(ledger.items()):
        fname = rec.get("file")
        if not fname or not fname.endswith(".xml"):
            continue
        src = REF / fname
        if not src.exists():
            continue
        out = REF / f"{key}.txt"
        if out.exists() and not _is_our_output(ledger, out):
            print(f"  SKIP {out.name}: not produced by this script, refusing to overwrite")
            skipped += 1
            continue
        text = render(src.read_text(errors="replace"))
        out.write_text(text)
        rec["xml"] = fname
        rec["xml_sha256"] = rec.get("sha256", "")
        rec["file"] = out.name
        rec["sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
        rec["extract_cmd"] = "python3 scripts/render_text.py"
        rec["chars"] = len(text)
        made += 1
    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True))
    print(f"  rendered {made} records to text"
          + (f", skipped {skipped} hand-extracted" if skipped else ""))


if __name__ == "__main__":
    main()

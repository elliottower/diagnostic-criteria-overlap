"""Fetch open-access PDFs for entries the identifier route left at metadata tier.

`fetch_sources.py` reaches Europe PMC and NCBI PMC. Journals outside those
indexes -- BMC, MDPI, npj, SAGE -- publish open access at their own URLs, which
OpenAlex records as `best_oa_location.pdf_url`. This asks OpenAlex for each DOI,
downloads the PDF it names, renders it with pdftotext, and upgrades the ledger
record to the `pdf` tier, keeping the prior record as `alt`.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _artifacts import artifacts_dir

ROOT = pathlib.Path(__file__).resolve().parent.parent
REF = artifacts_dir()
LEDGER = REF / "FETCH_LOG.json"
UA = "neurology-nosology-survey citations pass (elliot@elliottower.ai)"


def get(url: str, timeout: int = 60) -> bytes:
    return subprocess.run(
        ["curl", "-sSL", "--max-time", str(timeout), "-A", UA, url],
        capture_output=True).stdout


def oa_pdf_url(doi: str) -> str:
    u = ("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="") +
         "?mailto=elliot@elliottower.ai")
    try:
        r = json.loads(get(u))
    except Exception:
        return ""
    for loc in [r.get("best_oa_location")] + (r.get("locations") or []):
        if loc and loc.get("pdf_url"):
            return loc["pdf_url"]
    return ""


def main() -> int:
    bib = (ROOT / "paper" / "references_candidates.bib").read_text()
    dois = dict(re.findall(r"@\w+\{([^,]+),.*?doi\s*=\s*\{([^}]+)\}", bib, re.S))
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    for key, doi in sorted(dois.items()):
        prev = ledger.get(key, {})
        if prev.get("tier") in ("fulltext", "pdf"):
            print(f"  {key:18s} have it ({prev['tier']})")
            continue
        url = oa_pdf_url(doi)
        time.sleep(0.3)
        if not url:
            print(f"  {key:18s} no open-access PDF recorded")
            continue
        pdf, txt = REF / f"{key}.pdf", REF / f"{key}.txt"
        pdf.write_bytes(get(url))
        if pdf.stat().st_size < 20000 or not pdf.read_bytes().startswith(b"%PDF"):
            pdf.unlink(missing_ok=True)
            print(f"  {key:18s} FAILED  {url[:60]}")
            continue
        subprocess.run(["pdftotext", "-nopgbrk", str(pdf), str(txt)], capture_output=True)
        if not txt.exists() or txt.stat().st_size < 500:
            print(f"  {key:18s} PDF ok, extraction empty")
            continue
        body = txt.read_text(errors="replace")
        rec = {"chars": len(body),
               "extract_cmd": f"pdftotext -nopgbrk {key}.pdf {key}.txt",
               "file": f"{key}.txt", "note": f"Open-access PDF, doi {doi}",
               "sha256": hashlib.sha256(txt.read_bytes()).hexdigest(),
               "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
               "tier": "pdf"}
        if prev and prev.get("tier") in ("abstract", "metadata"):
            rec["alt"] = {k: v for k, v in prev.items() if k != "alt"}
        ledger[key] = rec
        LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True))
        print(f"  {key:18s} pdf      {len(body):>7,} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())

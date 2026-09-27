#!/usr/bin/env python3
"""Assemble the Zenodo deposit: three files and nothing else.

    submission/zenodo/DESCRIPTION.txt
    submission/zenodo/diagnostic-criteria-overlap.zip
    submission/zenodo/criterion_agreement_v1.pdf

The archive is the repository's tracked files. This repository was filtered to one
paper when it was created, so there is no per-paper selection to do here; what the
build still has to guarantee is that nothing which must never reach a public archive
has appeared since. Those checks are assertions rather than filters, because a filter
has to be right about files that do not exist yet.

The deposited PDF is numbered by the Zenodo record, not the working draft: the first
upload is v1 whatever letter-suffixed draft built it. A public reader should not be
shown a revision chain.
"""
import pathlib
import shutil
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "submission" / "zenodo"
ZIP = OUT / "diagnostic-criteria-overlap.zip"
PDF_SRC = pathlib.Path.home() / "Documents" / "GitHub" / "neurology-nosology-survey" / \
    "paper" / "criterion_agreement_v10.pdf"
PDF_OUT = OUT / "criterion_agreement_v1.pdf"

#: Path prefixes that must never appear in the archive. paper/ carries cover letters and
#: per-venue drafts; the others carry peer review, venue strategy and private email.
FORBIDDEN = ("paper/", "planning/", "reviews/", "correspondence/", "submission/",
             ".git/", "__pycache__/", ".venv/", ".results/")


class DepositError(RuntimeError):
    pass


def tracked_files() -> list[str]:
    r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise DepositError(f"git ls-files failed: {r.stderr.strip()}")
    return [l for l in r.stdout.splitlines() if l]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if ZIP.exists():
        raise DepositError(f"refusing to overwrite {ZIP}")

    names = tracked_files()
    if not names:
        raise DepositError("no tracked files; run this from a committed tree")

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:
            z.write(ROOT / name, name)

    with zipfile.ZipFile(ZIP) as z:
        entries = z.namelist()
    leaked = [e for e in entries if e.startswith(FORBIDDEN)]
    if leaked:
        ZIP.unlink()
        raise DepositError(f"archive would have carried {leaked[:5]}")
    if not any(e.startswith("results/") for e in entries):
        ZIP.unlink()
        raise DepositError("archive carries no results/; that is not this deposit")

    if not PDF_SRC.exists():
        raise DepositError(f"manuscript PDF absent: {PDF_SRC}")
    shutil.copy2(PDF_SRC, PDF_OUT)

    print(f"{ZIP.name}: {len(entries)} entries, {ZIP.stat().st_size / 1e6:.1f} MB")
    print(f"{PDF_OUT.name}: {PDF_OUT.stat().st_size / 1e6:.1f} MB")
    extra = sorted(p.name for p in OUT.iterdir()
                   if p.name not in {ZIP.name, PDF_OUT.name, "DESCRIPTION.txt"})
    print("deposit holds:", ", ".join(sorted(p.name for p in OUT.iterdir())))
    if extra:
        print(f"WARNING: {extra} should not be in the deposit")


if __name__ == "__main__":
    main()

# Notebook

Provenance for the criterion-agreement paper. Corrections found while preparing
the manuscript are recorded here and are invisible in it.

## 2026-08-26 — split out of neurology-nosology

`neurology-nosology` holds a philosophy-of-medicine paper submitted to
*Philosophy of Medicine*. This is a methods paper aimed at the *Journal of
Clinical Epidemiology*. Two venues, two audiences, and a code link that resolves
to the wrong paper either way, so they were separated. The pinned artifacts moved
to `$CITATIONS_HOME/artifacts`, shared by both.

## 2026-08-26 — a prior-art review cited a paper that does not exist

The review reported that the paper's second claim was pre-empted by *Kraemer HC
(1990), "Kappa and attenuation of the odds ratio," Epidemiology*. It is not a
real article. PubMed indexes three Kraemer papers in *Epidemiology*, the earliest
from 2010, and his complete 1988–1992 record — 36 papers, retrieved by esearch on
`Kraemer HC[Author] AND (1988[dp] OR ... OR 1992[dp])` — contains nothing of the
kind.

The real work is **Thompson & Walter 1988**, "A reappraisal of the kappa
coefficient," J Clin Epidemiol 41:949–58 (PMID 3057117), which relates kappa to
attenuation of an **odds ratio** under non-differential misclassification.
Kraemer & Bloch 1988 (PMID 3193139) is the reply in the same issue, ten pages
later. The review appears to have fused the two and invented a journal and year.

Claim 2 stands: Thompson and Walter ask how an unreliable measure biases a
downstream association estimate, and this paper asks how two measures should be
read against each other. Both are cited and distinguished in §5, with Spearman
1904 for the correction itself.

Every source was resolved by esearch before being cited; none was guessed.

## 2026-08-26 — render_text.py destroyed a hand-extracted artifact

It regenerates `reference/<key>.txt` from the PubMed XML.
`reference/kottner2011.txt` held the GRRAS Table 1 checklist, extracted from the
PDF, and the renderer replaced all fifteen items with the abstract. The items are
the only reason GRRAS is pinned. Recovered by re-extracting to
`kottner2011.checklist.txt`; the auditor reads it as a second artifact for the
same key, mapping `f.stem.split(".")[0]`.

The script now refuses to overwrite any file it did not itself produce, verified
by hash against the ledger. Tested both directions: it skips when the file is
foreign and still renders when the file is absent.

## Findings, with where each number comes from

**Table 1.** The GRRAS and STARD checklists share no vocabulary. Ten terms, every
one zero on one side. `scripts/count_guideline_terms.py` →
`results/table1_guideline_terms.json`, carrying the artifact hashes.

**Table 4.** The floor correction is computable for two of the three pairs that
have any published floor. Stroke admits none: `zhang2019` publishes 0.857 for
CISS inter-rater, and the comparison at issue is TOAST against CCS, so the floor
belongs to a criterion outside the comparison. Substituting it would import the
error the correction exists to remove.

## Venue

*Journal of Clinical Epidemiology*, Original Research — 3,000 words, 5 tables,
5 figures. GRRAS and QAREL were both published there. v2 is 2,109 words of prose
across 4 tables.

Known reviewer risks, in the order they are likely to be raised: the paper
proposes reporting requirements where this literature produces them by consensus
panel; Table 3 is a convenience sample rather than a systematic review; and
Spearman's correction was derived for product-moment correlations between
continuous measures, so applying it to kappa is an approximation.

---

## 2026-09-04 — the statistical core removed, and what replaced it

An external review found the paper's headline numbers indefensible. The finding
held up on checking and the paper changed shape around it.

**What was wrong.** v2 and v3 applied Spearman's correction for attenuation to a
criterion-level Cohen's kappa, using a separately published inter-rater kappa as
the reliability term, and reported corrected values of 0.30 and 0.84. Two
independent faults:

1. The correction is derived for the product-moment correlation under classical
   test theory. Kappa is chance-corrected and depends on the marginals of the
   table it summarizes, so the substitution is undefined rather than approximate.
   `attencorr2022`, the current treatment of attenuation-corrected reliability,
   does not mention kappa once, and argues the product-moment correlation is
   itself deflated by categorization.
2. Independent of the theory, the two inputs came from different populations.
   Zipoli's 0.52--0.57 is four neurologists on 44 cases; Guerra's 0.22 is a
   registry of 20,306 at roughly 4% prevalence. Kappa moves with prevalence, so
   the ratio is not an approximation of anything.

Removed in v4: the equation, both corrected values, the "Corrected" column, and
the inferential claim that criterion divergence accounted for most of the
shortfall.

**"Floor" is false, not merely imprecise.** A second research pass supplied
counterexamples. If A and B are the same classification while their replicates
are noisy, cross-criterion kappa is 1 while both within-criterion kappas can be
0.5. If both criteria have perfect repeatability and B is the complement of A,
cross-criterion kappa is -1. Identical reliability information is compatible with
opposite cross-criterion agreement. Within-criterion reliability is therefore
needed to *attribute* disagreement, not to bound it. Section 5's framing changes
accordingly; the section title no longer stands.

**What can be computed.** Only quantities a published table identifies: the full
2x2 where recoverable, both criterion prevalences, raw agreement, total and
directional discordance, the published kappa, and kappa_max as a marginal
diagnostic. Reliability-adjusted agreement is not identified by an aggregate
table plus a borrowed rater kappa, and a two-test latent class model on one 2x2
is underidentified by two parameters.

**The category-count problem, found by reading the sources.** Three rows are not
binary: stroke `mcardle2014` compares five ischaemic subtypes, `zhang2019` is
multi-category, `zhu2016` frailty is three-level. `warrens2021` Theorem 8
constructs tables with the same observed agreement and the same disagreement
structure and proves the kappa family strictly increases with the number of
categories. Binary and multi-category rows therefore cannot occupy one
distribution. This is a stronger objection than the prevalence one and no
adjustment repairs it.

**Two factual errors found in the table.** `zhang2019` n was 623; the paper
accrued 623 and analysed 299. `heianza2012` publishes a third pair in a table
footnote, kappa = 0.668 between ADA fasting glucose and ADA HbA1c, two
operationalizations of one criteria set agreeing less well than either does with
the rival Japanese criteria.

**A duplicate of my own making.** `simguide2026` was fetched as a new source and
is `vanbelle2025`, already in the bibliography. Removed from the candidates file,
the ledger and the artifact store. The second Vanbelle 2025 paper, *From
tetrachoric to kappa* (BJMSP, 10.1111/bmsp.70021), is a different work and is
now staged as `vanbelle2025b`.

**Sources added.** Sixteen of eighteen agreement-methodology candidates reached
readable tier and live in the shared citations library. `blandaltman1986` came
from the author's own site after the publisher route failed; `foulds2010` and
`openshaw1984` from author and course copies. Ten further coefficient papers were
added at metadata tier and can be cited but not quoted. `warrens2021` and
`wongpakaran2013` came in at full text.

**Decisions standing at the end of the session.**

- The paper is a methodological-conceptual article with audited clinical
  evidence, not a statistics paper and not a commentary.
- The thesis is the epistemic one: a contingency table does not determine
  whether agreement or accuracy is the right report, and that choice assigns
  authority to one criterion.
- Evidence is presented as an audited series, never as a distribution, a
  ranking, or a ceiling.
- Two panels, binary and multi-category, because Theorem 8 requires it.
- The simulation and the latent model are separate future work and block
  nothing.

## 2026-09-09 — Liveliness, and the register of the introduction

**The defect.** v9c's introduction opened on 20,306 patients and then 326, 540,
1,277, sensitivity 37.6%, kappa 0.22 and two prevalences, all before the reader was
told what question the counts answer. Every number is correct and every quotation
verifies. The problem is rhetorical sequence: the Guerra case is the demonstration
and was serving as the premise.

**The register check.** Seven JECP full texts were fetched from PMC (13180462,
13242882, 13242895, 13278660, 13345642, 13405251, 13446818; 980--7,505 words) and
read for how each introduction enters. All seven open on the practice, in the
present tense, with a citation in the first or second sentence. None opens on a
figure and none on a specific study. For comparison, `guerra2026` (J Neurol) opens
on the disease biology, `hazan2024` (Neurology) on the field's recent history with
dated approvals, and `johnson2026acr` (Arthritis & Rheumatology) on what
classification criteria are for. A clinical journal opens on the clinic; the number
belongs in paragraph two.

**The name.** "Liveliness" is the property a paper has when it takes a position
rather than reporting a procedure. The term is used in `neurology-nosology` commit
`9a299ca` ("carry v8 through its liveliness pass") and was defined nowhere, so it
existed only in conversation. It is now written into the `house-style` skill as a
separate pass that runs after the cringe pass, with the venue table above and a
six-item structural check. It is recorded here because the two repos share the
convention and the commit message that used it is in this project's history.

**A rate measurement that does not substitute for the check.** Hedge and claim
verbs per 1000 words: the seven JECP exemplars run a median 4.3 hedge / 2.4 claim /
4.0 first-person; `criterion_agreement_v9c`, `ms_identity_criterion_v1s` and
`ad_identity_criterion_v2e` run 1.1--1.6 / 7.7--9.1 / 0.5--0.9. The drafts are
assertive and impersonal against the venue. The rate did not detect the
statistics-first opening, so it corroborates and does not score.

## 2026-09-09 — v9d: introduction rebuilt, and a verification defect

**Introduction.** Rebuilt in five paragraphs entering on the practice rather than on
the counts: what criteria decide, the registry case, the two vocabularies, the
delirium case where a $\kappa$ conceals exact nesting, then the aim. `guerra2026`
prints the accuracy figure itself (91.1\%, 90.7--91.5) and prints no $\kappa$ at
all, so the 91.1\% against 15.2\% contrast is the source's own headline against a
quantity computed from the cells it also prints. Its Table 3 is headed
"Neurologist's definition as Gold Standard" and its limitations state the measures
quantify performance "in the absence of a true gold standard for SPMS diagnosis" —
one paper holding both positions, which now carries the two-conventions paragraph.

**A guideline claim that was false in v9c.** v9b carried a paragraph on
`johnson2026acr`: the ACR methods for criteria development recommend "Comparisons
with previous criteria" and an "Independent validation cohort ... compare to older
criteria/alternatives", under a triangular design that scores each criteria set
against an adjudicated standard and so never produces the old-by-new table. The v9c
cuts removed that paragraph but left the roadmap asserting that no guidance is
written for a design in which the criterion varies. v9d restores the paragraph and
states the narrower true claim: the gap is inside the guidance written for the
design.

**The claims files could not be read, and the earlier count was unchecked.** Three
of four claims files declared `extract_cmd: pdftotext` or `python3
scripts/render_text.py` against a `local:` that is already a `.txt`. `pdftotext` on
a text file exits 1 with "Couldn't read xref table", so those quotes returned
`unchecked` on every run — no measurement, not a pass. The `reference/*.txt`
artifacts are gitignored and were absent locally as well; they were restored from
the shared library with a sha256 check against the value recorded in each claims
file, and all four matched. `extract_cmd` is now `"none -- artifact is already
text"` throughout. A claims file for `johnson2026acr` was added, since its four
quotations had been used in two papers without ever being pinned. `citations
verify` now reads all ten quotes: **10 found, 0 not found, 0 unchecked.**

**Two residual warnings, both documented in the claims files rather than fixed.**
The `truncated` flag on the Guerra Table 3 header is a false positive — the render
concatenates two column headers, so the quote is a complete cell followed with no
separator by the next one. The ACR adjudication recommendation appears three times
in the render; the record pins the third by a suffix, the three being the same
sentence.

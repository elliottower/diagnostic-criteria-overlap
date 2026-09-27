# Known-truth benchmark inventory

Inclusion rule, applied strictly. A source qualifies as **known truth** only if
it publishes both:

1. enough to determine all four cells of a pair — either the 2x2 itself, an
   overlap count with both marginals and N, or both off-diagonals with both
   marginals; **and**
2. a **published** summary statistic to reconstruct *from*, which the cells were
   not used to compute here.

A source failing (1) is a reconstruction case. A source failing (2) cannot be a
benchmark at all: with no published statistic there is nothing to recover from.

| source | cells determined? | published statistic? | qualifies | pairs | condition |
|---|---|---|---|---:|---|
| `wancata2007` | yes — Table 3 marginals + every pairwise overlap + N | yes, ten kappas | **yes** | 10 | dementia |
| `tschanz2000` | yes — Table 2, two complete 2x2s | yes, kappa + % agreement | **yes** | 2 | dementia |
| `treml2024` | yes — both off-diagonals, marginals, N, three variants | yes, kappa + CI each | **yes** | 3 | prolonged grief |
| `solano2009` | yes — prose gives one discordance each way, with marginals and N | yes, kappa + CI | **yes** | 1 | antiphospholipid |
| `inoue2012` (registered) | yes — cells published | yes | **yes** | 2 | diabetes |
| `guerra2026` (registered) | yes — cells published | **no** — the kappa was derived by this analysis from those cells | **no, circular** | 0 | multiple sclerosis |
| `tay2015` | yes — prose determines the binary pair | **no** — published kappa is three-category, not the binary pair | **no** | 0 | dementia/MCI |
| `lee2018` | partial — three criteria counts, not pairwise overlaps | yes, two kappas | reconstruction case | 0 | Sjogren's |
| `pollock2000` | no — kappas given as ranges | ranges only | context only | 0 | alcohol use |
| `saraux2013` | no — kappas given as ranges | ranges only | context only | 0 | rheumatoid arthritis |

## Count against the decision rule

- **Independent articles: 5** (Wancata, Tschanz, Treml, Solano, Inoue)
- **Conditions: 4** (dementia, prolonged grief, antiphospholipid, diabetes)
- **Pairwise tables: 18**
- **Concentration: 10 of 18 from a single cohort** (Wancata)

Against the stated thresholds — 20 pairs, 5 articles, 4 conditions — this
clears articles and conditions and falls two pairs short, with heavy clustering
in one source.

That places it in the second row of the decision rule: **a limited benchmark**,
to be presented with the dependence stated, not as eighteen independent
validations.

## Two exclusions worth keeping visible

`guerra2026` publishes its cells but no agreement statistic; the kappa in the
registered corpus was computed by this analysis from those very cells. Using it
as a benchmark would test the arithmetic against itself.

`tay2015` determines a binary table from prose but publishes only a
three-category kappa and Gwet's AC1. There is no binary published statistic to
reconstruct from.

## What would close the gap

Acute kidney injury. RIFLE, AKIN and KDIGO are applied to the same patients
routinely, cross-tabulations are commonly published, sample sizes span small
cohorts to thousands, and the criteria range from near-nested to substantially
divergent through baseline-creatinine and observation-window choices. Two or
three AKI studies publishing stagewise cross-tabs would add independent
articles in a different clinical and statistical regime, which matters more
than the raw pair count.

Nothing here has been run. This is an inventory of what each source prints.

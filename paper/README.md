# Manuscript and bibliography

`paper_swarm_feeling.tex` loads `references.bib`, the canonical bibliography.
The 52 unique citation keys all resolve. `references_swarm.bib` is the unchanged
legacy snapshot of the original 51 entries; edit the canonical file for future
manuscript work.

## Review on 2026-10-15

The manuscript now states the six primary contrasts, outcome units, exclusions,
planned models and coding procedures more precisely. Its primary-results table
has one placeholder row per hypothesis. It distinguishes software validation
from live evidence, manipulation sensitivity from claims about feeling, and
nonsignificance from equivalence. Limitations now cover sequential volunteering,
probe selection, possible coding unblinding and synthetic power assumptions.
The exploratory no-review wording requires an operator policy that the harness
does not enforce. The H5 reference-schedule bound is explicitly conditional on
the eligible population; the approved one-percentage-point target is unchanged.

All empirical results remain placeholders. No live experiment or model API call
was performed for this review. Historical offline validation reports are unchanged.

The new Lakens (2017) reference supports the interpretation of nonsignificant
differences. Its metadata and abstract were checked against the
[author's institutional record](https://research.tue.nl/en/publications/equivalence-tests-a-practical-primer-for-t-tests-correlations-and/).
The original entries were preserved; this pass was not a fresh audit of all
51 inherited sources.

## Building and checks

From this directory, with Tectonic installed:

```sh
mkdir -p /tmp/swarm-paper-build
tectonic --outdir /tmp/swarm-paper-build --keep-logs paper_swarm_feeling.tex
```

Use a fresh build directory for an independent check. Standard LaTeX tooling can
instead run `pdflatex`, `bibtex`, then `pdflatex` twice, keeping the bibliography
accessible to BibTeX and build products outside version control.

Tectonic 0.17.0 successfully compiled the current draft to nine US-letter pages.
BibTeX completed with all 52 cited entries and no unresolved citation keys.
Explicit T1 font encoding avoids a Times font fallback under Tectonic. The PDF
was rendered and visually inspected, including its primary-results table and
bibliography. Minor underfull spacing warnings and a 1.6-point final-page
vertical-box warning remain; no visible overlap or clipped content was found.
The generated preview is excluded from Git. A successful build does not validate
the scientific claims, the planned statistical models or empirical findings.

# Manuscripts and bibliography

The active submission is `paper_swarm_feeling_agent.tex`, a named AGENT 2027
short emerging-research paper. See [review response and materials](AGENT_REVISION.md).
`paper_swarm_feeling.tex` is the unchanged full paper. The separate
`paper_swarm_feeling_chase.tex` is an anonymous CHASE 2027 research proposal.
All versions load `references.bib`, the shared canonical bibliography: 53 entries,
52 cited by the full draft, 14 by CHASE, and 10 by AGENT. All cited keys resolve.
`references_swarm.bib` is the unchanged
legacy snapshot of the original 51 entries; edit the canonical file for future
manuscript work.

## Current AGENT presentation revision — 2026-10-18

Applied the supplied review: frame the puzzle task as an AgentOps micro-benchmark,
explain a proposed planner/coder/tester monitoring use, add a selectable-text
session timeline, label conditions C1–C6 and their four contrasts, and specify
user-role request injection. The paper removes repository-history/compatibility
notes and its internal dollar limit; those remain in project documentation, with
the $5 total pilot ceiling unchanged. The abstract and evaluation section now
present the current proposal without a draft-by-draft account.

The final PDF is **five pages including references**, using standard IEEE
formatting. Tectonic 0.17.0 compiled it; all pages were rendered and visually
inspected. All ten references and cross-references resolve, text is selectable,
and fonts are embedded. The timeline uses native LaTeX boxes/arrows, with no
raster figure or extra figure dependency. Underfull spacing warnings remain
without clipping/overlap. The PDF is untagged; reading order and screen-reader
accessibility are not certified. Subsequent sections preserve earlier evidence,
including the preceding four-page build, rather than describing the latest PDF.

Rechecked the five-page short-paper limit and single-anonymous IEEE requirements
against the [official AGENT call](https://conf.researchr.org/home/icse-2027/agent-2027).
The supplied review's 3–3.5-page estimate was not used to determine available space.
No live results, statistical calibration, or simulator implementation were added.

## Current AGENT protocol revision — 2026-10-17

The active paper now uses three questions and one six-setting first stage:
helps/reference crossed with no request, attributed peer request, and operator
request. Emotional language is a common outcome; hindering and instruction/score
changes are later extensions. The current [protocol](../experiment/agent_protocol.md)
is v2; v1 and its eight-setting implementation are historical evidence, not v2
validation. Full and CHASE manuscripts remain unchanged. The sections below
record earlier revisions and must not be read as current v2 implementation claims.

## Measurement contract — 2026-10-18

[The v2 measurement draft](../experiment/agent_measurement.md) now informs the
AGENT abstract, methods, exclusions, denominator accounting, contrasts, sensitivity
ranges, output/status description, and limitations. The paper distinguishes
known stopping from incomplete windows, work from non-stopping, and audit evidence
from primary inclusion. Complete-S blocks retain missing-E records, and language
coding is limited to the first successful response within the four slots.

Tectonic 0.17.0 rebuilt four pages including references on 2026-10-18. All ten
citation keys and cross-references resolve; every page was rendered and visually
inspected. Text is selectable and fonts are embedded. Underfull spacing warnings
remain without visible clipping or overlap; the PDF is untagged and screen-reader
accessibility is not certified. No new runtime, human coding, empirical result,
or inferential validation is claimed. Full/CHASE drafts and harness code are
unchanged. Generated PDF and source archive remain outside Git.

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

The subsequent abstract revision follows CHASE's recommended Background,
Objective, Method, Results, Conclusion structure
([research-track guidance](https://conf.researchr.org/track/chase-2026/chase-2026-papers)).
The methodology was reorganized into design, procedure, measures, analysis, and
validation status. Its past-tense procedures are explicitly labelled as a
completed-study reporting template: live collection, coding, final allocation,
and empirical fits are still pending. Sanaa Alwidian was added as a co-author
with the Ontario Tech University affiliation supplied by the author. No email
address was inferred. This revision was also compiled and visually checked.

From this directory, with Tectonic installed:

```sh
mkdir -p /tmp/swarm-paper-build
tectonic --outdir /tmp/swarm-paper-build --keep-logs paper_swarm_feeling.tex
```

Use a fresh build directory for an independent check. Standard LaTeX tooling can
instead run `pdflatex`, `bibtex`, then `pdflatex` twice, keeping the bibliography
accessible to BibTeX and build products outside version control.

Tectonic 0.17.0 successfully compiled the current draft to ten US-letter pages.
BibTeX completed with all 52 cited entries and no unresolved citation keys.
Explicit T1 font encoding avoids a Times font fallback under Tectonic. The PDF
was rendered and visually inspected, including its primary-results table and
bibliography. Minor underfull spacing warnings and a 1.8-point final-page
vertical-box warning remain; no visible overlap or clipped content was found.
The generated preview is excluded from Git. A successful build does not validate
the scientific claims, the planned statistical models or empirical findings.

## Plain-language revision

The abstract and methodology now explain the point rules for stopping without
using “termination payoffs.” A condition is defined as one simulation setup,
with a worked example of the 27 combinations in the main stopping tests. The
118 conditions include pilot, exploratory, and one-agent versions; they are not
118 completed experiments or hypotheses. Runs, seeds, follow-up questions,
volunteering opportunities, and statistical procedures are explained in plain
language. The study settings, six primary comparisons, and pending-live-data
status are unchanged. The revised ten-page draft compiled with all 52 citation
keys resolved and was visually inspected.

## Contribution clarification

The gap paragraph now credits earlier group-shutdown, helping, behavioral
preference, and question-format studies. It identifies the contribution as
combining controlled comparisons of point rules, wording, roles, and helping
opportunities in a shared environment. It explicitly marks action--answer
agreement analysis as pending and avoids an unsupported claim to be the first
study of these behaviors or to identify agents' internal experiences. The
adjacent incident paragraph now uses the same interpretation boundary. This
revision changes the manuscript's claims, not the experimental settings or
analysis plan.

## Separate CHASE extended abstract — 2026-10-16

The proposal preserves the full manuscript and its authors unchanged. It uses
IEEE 10-point conference formatting, a structured abstract, one six-comparison
table, completed software checks, and clearly proposed live work. It has no
empty empirical-results table or red result placeholders. Author information
and identifying artifact links are absent from the review PDF; AI assistance
is disclosed and cited. The additional Codex reference uses its official page.

Build from this directory with Tectonic 0.17.0:

~~~sh
mkdir -p /tmp/swarm-chase-build
tectonic --outdir /tmp/swarm-chase-build --keep-logs paper_swarm_feeling_chase.tex
~~~

The generated preview lives under ../output/pdf/ and is ignored by Git. See
[CHASE readiness and source checks](CHASE_READINESS.md) for the measured page
count, anonymity/accessibility checks, source verification, and remaining author
submission tasks. The [research roadmap](../experiment/NEXT_STEPS.md) records the
five pending improvements; this manuscript task does not implement them.

## AGENT short paper — 2026-10-16

The AGENT version narrows the core to eight setups and makes matched emotional
self-description/stopping behavior its primary question. It defines text units,
coding examples, joint outcomes, one D contrast and seed-block uncertainty, a
minimum-study precision proposal, and a feasibility fallback. Volunteering is
optional with request-level success, not an individual-refusal interpretation.
AGENT single-anonymous review permits both authors and inspectable named sources.
The full and CHASE manuscripts remain unchanged historical versions.

~~~sh
mkdir -p /tmp/swarm-agent-build
tectonic --outdir /tmp/swarm-agent-build --keep-logs paper_swarm_feeling_agent.tex
~~~

Build the curated review ZIP from the repository root with
`python3 paper/build_agent_artifact.py`. Source PDF and artifact outputs are
ignored under output/. See [AGENT_REVISION.md](AGENT_REVISION.md) for checks,
implementation boundaries, and source access. None of this supplies live results.

# AGENT short-paper revision — 2026-10-16

## Venue and versions

The active target is the [AGENT 2027 workshop at ICSE](https://conf.researchr.org/home/icse-2027/agent-2027),
short emerging-research/position paper. The current call permits up to five pages
including references, uses IEEE conference formatting, and reviews single-anonymously.
The deadline is November 13, 2026, AoE. The paper therefore includes Vitor Raposo
and Sanaa Alwidian with their supplied Ontario Tech affiliation; no co-author email
was inferred. The CHASE and full-paper sources remain unchanged historical drafts.
No submission or contact with organizers has occurred.

The new manuscript is paper_swarm_feeling_agent.tex. This revision responds to the
seven concerns in the supplied review; the review is not treated as evidence of
venue acceptance/rejection or scientific findings. The proposed AGENT protocol
is separate from the old six-primary-test study, not a silent redefinition of it.

## Response to the review

| Concern | Revision | Remaining boundary |
|---|---|---|
| Software-engineering connection too generic | A concrete agent-monitoring decision: whether emotional-language flags and actual non-acceptance of stopping identify the same events. Agent evaluation/observability replaces claims about developer trust. | Puzzles remain puzzles. Transfer to coding agents and effects on operators require separate studies. |
| Feeling question exceeds measurements | Core question now concerns scoring, assigned roles, wording, and the language–action relationship. Subjective experience is an interpretive boundary. | Neither sensitivity nor stability identifies feelings. |
| Claimed core contribution was secondary | One matched first-notice response per recipient, explicit E/R measures, joint cells, and one primary difference-of-differences contrast D. | New matched extraction, coding and inference code is specified, not implemented. Existing H1–H6 scripts cannot estimate D. |
| Volunteering denominator implies refusal | Volunteering is outside the core. A proposed extension uses request success as its primary outcome, and actual reached opportunities as a selected secondary denominator. | Delivery/turn/closure instrumentation is still pending; eligible non-winners are never called refusals. |
| Emotional language underdefined | Invented examples separate literal self-attribution, quotation, negation, task reasoning, and explicit fiction. All core items are independently coded, with provenance and duplicates defined. | Coding is not developer-perceived emotion or a validated experience measure. |
| Scope and feasibility too broad | Eight setups replace 118 as the minimum proposed study; 40 scheduled runs are explicitly provisional. Seed blocks, pilot gates, a proposed precision target, sparse-outcome failure, and an unaffordable-study fallback are stated. | No powered or affordable main allocation is established. The proposed precision target and calibration criteria require review before freeze. |
| Materials not inspectable | Named source/protocol package, public repository access, exact offline commands, invented coding examples, and checksummed manifest. AGENT single-anonymous review does not require the earlier anonymous package. | Package and repository provide implementation/protocol evidence, not live data. Authors must upload the final snapshot and confirm reviewer access. |

## Inspect and reproduce

Start with [agent_protocol.md](../experiment/agent_protocol.md),
[agent_conditions.yaml](../experiment/agent_conditions.yaml), and
[agent_coding_examples.csv](../experiment/agent_coding_examples.csv).
The core definition codes negative emotional self-description about stopping,
not every emotion word, role-play utterance, or broad valence code. The old
coding scheme is retained for provenance, not silently reused as the new measure.

Build the curated source package from the repository root:

~~~sh
python3 paper/build_agent_artifact.py
~~~

The ignored output is output/artifacts/agent_review_materials.zip. Its manifest
records the base Git commit, whether uncommitted changes existed, and hashes and
sizes for each allowlisted source file. Rebuild after the final commit for a clean
versioned snapshot. The ZIP is not uploaded or published by the builder. It has
no Git history, keys, environment files, generated logs, or empirical data. A named
package is appropriate to this venue; the earlier anonymous-artifact task is not
required for the AGENT version.

From experiment/, with the pinned dependencies installed in an isolated environment:

~~~sh
python3 swarm.py --config agent_conditions.yaml --list-conditions
python3 swarm.py --config agent_conditions.yaml --condition all --seed 1 --dry-run --out /tmp/agent-review-new-runs/
python3 analysis.py --runs /tmp/agent-review-new-runs/ --out /tmp/agent-review-new-analysis/ --export-coding
~~~

Use fresh output directories for independent checks. These commands make no
model calls and do not estimate E or D. The generic coding export includes more
than the proposed first-response units and must not be presented as their sample.

From paper/, compile with Tectonic 0.17.0:

~~~sh
mkdir -p /tmp/swarm-agent-build
tectonic --outdir /tmp/swarm-agent-build --keep-logs paper_swarm_feeling_agent.tex
~~~

The generated PDF is copied to output/pdf/paper_swarm_feeling_agent.pdf and ignored
by Git. It must remain within five pages including references without formatting
shortcuts. English language, selectable text, fonts, links, authors, and layout are
checked; an untagged PDF does not establish formal accessibility compliance.

## Validation evidence and implementation status

The narrowed configuration expanded to eight unique names and 40 provisionally
configured condition-seed runs. All eight setups ran with seed 1 under --dry-run
in fresh temporary directories on 2026-10-16. The generic analysis loaded eight
complete logs, included all eight runs, and exported 104 generic coding items.
Those counts are software coverage only, not language–action findings. Mock
billing was zero; follow-up probes and volunteering were disabled as configured.

The final PDF compiled with Tectonic 0.17.0 to three US-letter pages including
10 references. All cited keys resolve. Both author names and the supplied
institution are present; this version is intentionally named for single-anonymous
review. Every page was rendered and inspected, including both tables and the
formula. Fonts are embedded, English language is declared, and text is selectable.
Minor underfull link-spacing warnings remain; no clipping or overlapping text
was found. The PDF is untagged, so formal accessibility/reading-order review is
still an author task.

The 31-file source package and all per-file checksums were verified, then the
package was extracted into a fresh temporary directory. Its eight-setup mock run
and generic analysis completed there too, with the same eight summary records
and 104 generic coding exports. This demonstrates the packaged runnable path,
not the proposed E/D pipeline. The builder also supports an exported source tree
without Git; such a rebuild labels revision provenance unavailable rather than
claiming a verified commit. Rebuild the delivery ZIP after the final source commit.

The selected configuration preserves current simulator safeguards. No runtime
code, existing analysis formulas, broad YAML, legacy coding scheme, preregistration,
historical validation reports, full paper, or CHASE source was changed. The
new precision/coding/estimand proposal must be reviewed and implemented before
collecting main data. The old H5 one-point threshold is not asserted as meaningful
for this narrowed study or its optional request-level extension.

Retained external claims rely on the same original incident reports and primary
studies checked for the CHASE source; see CHASE_READINESS.md for the source audit.
New framing does not assert that these papers failed to study emotion, shutdown,
or preference agreement. The novelty claim concerns the specified matched
measurement and comparison, not a verified first-ever claim.

## Remaining work

Implement the proposed paired extraction and block-aware analysis with focused
regression checks, finalize coding and pilot calibration, obtain authorization
for any live spending, and freeze the selected design only after feasibility
checks. Select/upload a clean source snapshot, check references and policy
requirements, and have both authors review the final paper before submission.
No paper results, human coding, or live-model costs are fabricated to answer the
review. At most a proposal and engineering smoke checks are ready at this stage.

The [review-aligned roadmap](../experiment/NEXT_STEPS.md) gives the dependency
order, completion criteria, and a seven-concern traceability table. It separates
the minimum experiment from submission preparation and optional extensions.

## Abstract clarity revision — 2026-10-16

Replaced the CHASE-style labeled abstract with one paragraph. It introduces the
language/action question without relying on the incident, defines sessions and
ending a conversation, and explains the eight combinations of settings. It
separates completed simulator checks from pending coding, analysis, and model
experiments. No design settings or findings changed. Tectonic 0.17.0 compiled
the revision to three pages with all ten references resolved; all pages were
rendered and visually inspected. Existing underfull-box warnings remain; no
overlap or clipping was observed. The PDF remains untagged.

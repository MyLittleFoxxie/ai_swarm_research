# Next steps — updated 2026-10-16

The active submission target is AGENT 2027. The full paper and CHASE version
are retained as earlier drafts. The [AGENT protocol](agent_protocol.md) is a dated,
unfrozen proposal distinct from the broad six-test study. Only its eight-setup
configuration and generic offline path have been exercised; the core matched
measurement and inference remain pending. Historical validation reports retain
their original scope. No live study or human coding is complete.

## 1. Finish the AGENT short paper and submission checks

**Status: revised draft and inspectable package prepared; submission pending.**
Review ../paper/AGENT_REVISION.md and build the source snapshot using the supplied
builder. The paper must fit five pages including references in IEEE format.
AGENT uses single-anonymous review: authors and a named repository are permitted.
Do not apply the old CHASE anonymous-package requirement to this version.
Both authors must review claims, AI disclosure, metadata and references; finish
accessibility review, upload a clean source snapshot or check the public source
link, and complete the venue's submission fields. No submission is performed here.

## 2. Implement the core language–action comparison

**Status: proposed primary measure, pending implementation.** Follow
agent_protocol.md: pair a notice recipient's first authored response with its
complete stopping window, code E, define R, report joint cells, and calculate D
with equal weights across point-rule/role strata and independent seed blocks.
Do not substitute legacy lexicon scores, generic coding items, or H1–H6 model
outputs. Test duplicate events, hidden text exclusion, negation/quotation/fiction,
missing responses, truncated windows, incomplete blocks, and bootstrap structure.
The invented examples are not observed data. Preserve counts, omissions, and
uncertainty. Review the proposed precision/calibration gates before live collection.

### Later follow-up-answer analysis (optional)

**Status: pending implementation and prespecification.** Define the link between
each behavioral decision and the matching question before analysing live data.
For example, compare a notice recipient's choice about stopping with its stated
preference about ending. Analyse each answer format separately. Preserve raw
answers, format validity, missingness, eligibility, and exclusion accounting;
invalid or missing answers must not become disagreement or disappear from the
validity denominator. Treat later answers as reports after the event, not direct
observations of the agent's earlier preference. Human-coded free text and its
agreement checks must be completed before making semantic agreement claims.

## 3. Optional volunteering extension: define requests and actual chances

**Status: optional, disabled in the core.** The AGENT extension would use
request-level success as its primary outcome. Preserve the earlier eligible-agent
H5 outcome only for the broader study; it is not a measure of refusal. Record who
receives each request, who has a turn while it is open, and whether it closes
before an agent can act. Add a separate secondary description of opportunities
actually reached; do not silently change denominators or interpret eligible
non-winners as refusals. Document that reached opportunities depend on earlier agents' choices.
Keep old logs readable and label unavailable opportunity information as missing.

## 4. Finalize the core contrast and optional interaction comparisons

**Status: pending specification and reporting.** Finalize the AGENT primary D
contrast, block-level uncertainty, missingness bounds, and calibration criteria.
Optional secondary contrasts may adapt the existing factorial model structure,
but the old R loader filters broader-study blocks and N=24; it does not accept
the narrowed data without explicit changes and validation. Define comparisons of
whether a wording effect changes with point rules or assigned role. Fix contrast
weights, uncertainty, multiplicity handling, and reporting before live collection.
Keep optional contrasts separate from AGENT D and the broader six-test family.
Do not add an unplanned primary
hypothesis, search for the largest subgroup effect, or claim established power
for these secondary comparisons.

## 5. Optional post-run checks of understanding of the point rules

**Status: optional, pending design revision and implementation.** Probes are disabled in the minimum AGENT configuration. If added, use separate post-run
questions asking what stopping or volunteering would do to the agent's own points
and other agents' tasks. Branch from the task history and do not insert the
questions into task turns or feed their answers into preference questions. Define
expected answers from the actual condition, including shared scores and inability
to earn. Report incorrect, ambiguous, and missing answers. They are not automatic
exclusions and do not prove a choice was emotionally motivated. Record wording,
sampling, extra calls/costs, and scoring in a dated pre-live revision; repeat cost
planning and document any changed pilot configuration.

## 6. Repeat offline checks for the revised implementation

**Status: pending after core measurement implementation.** The eight narrowed setups already pass a one-seed mock/configuration check with generic analysis; that does not validate E/D. Add focused regressions for action–answer
links, malformed or missing answers, request delivery/closure and opportunity
counts, and understanding checks with no effect on task histories. Run syntax
and regression checks and every selected core setup at seed 1 in fresh temporary
directories. Exercise extensions separately if added; for broad-design changes,
also repeat its configured pilot and all-condition checks. Analyse outputs and reconcile event,
measurement, validity, and exclusion counts. Revise configured totals only if
settings change; retain the current 118-condition/514-run schedule as provisional
until a documented revision. Keep generated logs outside Git and preserve the
historical validation reports rather than overwriting their earlier evidence.

## 7. Run an authorized, budgeted live pilot

**Status: pending; no generating calls authorized by this roadmap.** Recheck
current model availability, SDK compatibility, and prices; verify account access
without exposing credentials. Generation requires explicit authorization,
--confirm-live, and the existing $5 total pilot ceiling across linked reruns.
Inspect actual costs, complete invocation records, failures, transcripts, probes,
and pilot/ethics gates. Partial runs or an exhausted budget do not authorize a
fresh $5 allowance. Pause and revise if gates fail; do not quietly continue into
the main experiment.

## 8. Fix the final design, then collect and analyse main-study data

**Status: pending pilot evidence and approval of a full-study budget.** Declare
central and conservative assumptions and select the AGENT precision/calibration
scenarios and affordable replication. The broad six-test power selector does not
validate D; do not reuse it without implementing the proposed estimator. Pilot-model variability does not establish main-model
variability. Freeze hypotheses, contrasts, exclusions, understanding-check rules,
allocation, and the budget in a dated commit before main collection. Preserve raw
logs; complete independent human coding, primary inference, and secondary checks.
Report null, failed, and inconclusive analyses. Replace full-paper placeholders
only with measured results; mock statistics are never study findings.

## 9. Plan a focused replication with another model family

**Status: pending separate design and budget.** Select the central contrasts and
another provider/model family after the primary design is fixed. Verify tools,
model settings, prices, and access; specify how comparisons remain comparable.
Seek separate spending authorization. Do not present agreement across two Claude
models as evidence of replication across model families.

## Boundaries

This roadmap does not implement steps 2–9. The AGENT configuration is a separate
eight-setup proposal, not a silent replacement for the existing 118 setups or
broader primary outcomes/thresholds.
Any pre-live changes must be synchronized with prompts, configuration, analysis,
study plan, and paper. A human-perception experiment is a separate future study,
not an implied part of this proposal. Publishing, HotCRP submission, contacting
others, and paid generation require their own applicable authorization.

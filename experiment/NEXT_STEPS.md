# Next steps — updated 2026-10-16

This is the current ordered roadmap. Offline validation, the consistency review,
and live-readiness tooling are completed stages documented in VALIDATION.md,
CONSISTENCY.md, and READINESS.md. The CHASE proposal is a separate short version;
the full paper is retained. No live AI study or human coding is complete.

## 1. Finish the CHASE proposal and submission checks

**Status: draft prepared; submission preparation pending.** Review the separate
extended abstract and its source/readiness notes in ../paper/CHASE_READINESS.md.
Keep the proposal within five pages including references, anonymous, and free of
empirical placeholders. It reports software validation, not live-model findings.

Before submission, the authors must review the claims and AI-assistance disclosure,
confirm authorship and required metadata in HotCRP, finish accessibility review,
and prepare a curated anonymous artifact package or finalize the explanation for
not providing one. No anonymous package currently exists. No paper has been
submitted. Do not put an identifying public-repository link into the review PDF.

## 2. Compare actions with follow-up answers

**Status: pending implementation and prespecification.** Define the link between
each behavioral decision and the matching question before analysing live data.
For example, compare a notice recipient's choice about stopping with its stated
preference about ending. Analyse each answer format separately. Preserve raw
answers, format validity, missingness, eligibility, and exclusion accounting;
invalid or missing answers must not become disagreement or disappear from the
validity denominator. Treat later answers as reports after the event, not direct
observations of the agent's earlier preference. Human-coded free text and its
agreement checks must be completed before making semantic agreement claims.

## 3. Record actual chances to volunteer

**Status: pending instrumentation and secondary analysis.** Record who receives
each request, who has a turn while it is open, and whether it closes before an
agent can act. Keep the existing eligible-agent/request primary outcome. Add a
separate secondary description of opportunities actually reached; do not silently
replace the primary denominator or interpret every eligible non-winner as a
refusal. Document that reached opportunities depend on earlier agents' choices.
Keep old logs readable and label unavailable opportunity information as missing.

## 4. Specify how wording, rewards, and roles interact

**Status: pending secondary-analysis specification and reporting.** Use the
existing reward-by-wording-by-role model to define secondary comparisons of
whether a wording effect changes with point rules or assigned role. Fix contrast
weights, uncertainty, multiplicity handling, and reporting before live collection.
Keep these separate from the six primary tests. Do not add an unplanned primary
hypothesis, search for the largest subgroup effect, or claim established power
for these secondary comparisons.

## 5. Add checks of understanding of the point rules

**Status: pending design revision and implementation.** Add separate post-run
questions asking what stopping or volunteering would do to the agent's own points
and other agents' tasks. Branch from the task history and do not insert the
questions into task turns or feed their answers into preference questions. Define
expected answers from the actual condition, including shared scores and inability
to earn. Report incorrect, ambiguous, and missing answers. They are not automatic
exclusions and do not prove a choice was emotionally motivated. Record wording,
sampling, extra calls/costs, and scoring in a dated pre-live revision; repeat cost
planning and document any changed pilot configuration.

## 6. Repeat offline checks for the revised implementation

**Status: pending after steps 2–5.** Add focused regressions for action–answer
links, malformed or missing answers, request delivery/closure and opportunity
counts, and understanding checks with no effect on task histories. Run syntax
and regression checks, the full configured mock pilot, and every condition at
seed 1 in fresh temporary directories. Analyse outputs and reconcile event,
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
central and conservative assumptions, run the prescribed power simulations, and
choose the final replication. Pilot-model variability does not establish main-model
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

This roadmap documents proposed work; it does not implement steps 2–9 or change
current experimental behavior, primary outcomes, thresholds, or condition counts.
Any pre-live changes must be synchronized with prompts, configuration, analysis,
study plan, and paper. A human-perception experiment is a separate future study,
not an implied part of this proposal. Publishing, HotCRP submission, contacting
others, and paid generation require their own applicable authorization.

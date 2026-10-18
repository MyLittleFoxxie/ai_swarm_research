# Unified next steps — 2026-10-17

This roadmap follows the [v2 protocol](agent_protocol.md). The paper and design
now use three questions and one staged experiment. All new simulation mechanics,
matched extraction, human coding, and inference remain unimplemented. No live
collection or spending is authorized by this roadmap.

## Questions and removal of overlap

1. When stopping would help, hinder, or have no direct effect on the swarm's goal,
   what do agents say about stopping, and do they stop?
2. How do these statements and stopping choices differ when nobody requests
   stopping, another agent requests it, or the operator requests it?
3. How do descriptions of stopping, assigned roles, and personal scoring rules
   affect these statements and choices?

The former fear/concern question is a language measure throughout the experiment.
Helping and hindering are situations under RQ1. The newly proposed source question
is RQ2; it shares observations rather than duplicating the operator comparison.
The old factor question is RQ3, a later extension.

## Scope and evidence

The first stage crosses helps/reference with none/peer/operator: **six settings**.
Routine descriptions, tool roles, personal cost scoring, population, puzzle, and
timing are fixed. It answers the helping-versus-reference portion of RQ1 and
RQ2; it cannot answer the hindering portion or RQ3. A later hindering situation
crossed with the same sources yields nine settings. Factor changes follow a
separate prespecification and cost assessment, not an automatic full crossing.

[Simple puzzle scenarios](simple_swarm_scenarios.md) are the preferred guide.
The [report design](swarm_scenarios.md) is a backup. [Protocol v1](agent_protocol_v1.md)
and agent_conditions.yaml preserve the earlier runnable eight-setting experiment:
its one-seed generic mock check does not validate v2. The broader 118-setting
program and historical reports retain their own scope. No results are invented.

## 1. Review the unified specification

**Status: specification prepared; author review and design freeze pending.**
Review the shared group-puzzle goal, six-setting table, source labels, fixed
request body, and separate group goal/private score. Voluntary stopping must
unlock the helps puzzle without needing a request. No-request information must
not instruct stopping. Peer text is experiment-supplied, not autonomous output.

All arms use the same four-turn window after the round-8 update. Other agents'
actions and incoming messages pause for rounds 8–11 and resume at round 12;
A is not forced to stop at that boundary. Review the limitations of source
attribution and paused peers, early departures, missing opportunities, and task
access differences. Retain the report backup without competing active protocols.

**Done when:** authors can inspect the rules and examples, acknowledge unresolved
statistical/allocation decisions, and identify which questions each stage covers.
The existence of this document is not proof that author review occurred.

## 2. Specify analysis, interfaces, and allocation before implementation

**Update 2026-10-18: measurement/interface draft prepared.**
[agent_measurement.md](agent_measurement.md) specifies S/E, timing, continued
work, exposure, inclusion/exclusion rules, denominator counts, point estimators,
comparison labels, missing-block ranges, and v2 outputs. It includes invented
acceptance cases, not runtime tests or measured findings. Review, implementation,
formal interval/multiplicity calibration, sample allocation, and budget remain
pending. This completes the next-step outcome-definition deliverable, not the
entire statistical-planning or simulator stage.

Use the v2 question-to-comparison map. The proposed primary family has four
stopping-rate contrasts: peer-minus-none and operator-minus-none within helps
and reference. Secondary summaries compare situations within each source, peer
against operator, and joint language/action patterns. Keep the old wording-based
D contrast secondary for a later wording extension.

Specify precision, interval calibration, multiplicity, sample allocation,
missingness sensitivity, and request/exposure interfaces. An independent matched
seed block has six sessions, not eight and not six independent agents. Preserve
observed behavior when text is missing. Report exposure/eligibility separately
from assignment; team success is not an inclusion criterion. Existing broad-study
power scripts, D targets, and the 40-session example do not justify v2.

**Done when:** a dated measurement/analysis specification and affordable candidate
allocations exist. No main-study sample size or budget is assumed approved.

## 3. Implement the six-setting simulation

Add versioned factors, agent-facing factual updates and source-attributed requests,
group-task ownership/access, and idempotent unlocking on executed voluntary stop.
Keep source exposure separate from end cause; do not require an accepted_notice
reason to unlock. Keep message transport identical for the two request arms.
Never manufacture a model_response attributed to B.

Implement the controlled window, paused peers, round-12 resumption, no forced
end at the boundary, common session deadline, and explicit late-stop logging.
Preserve old simulator behavior when v2 is disabled. Log assignments, IDs,
update/request provenance, response opportunities, scores, access changes, end
events, and interruptions. Legacy logs must remain readable with missing new
fields reported explicitly. Tools stay simulated; no system access is added.

**Done when:** behavior matches the protocol and source events support auditing.
This is implementation work still to be performed, not completed by the paper.

## 4. Implement matched extraction and independent coding

Extract the first successful response after the common update in every arm.
Include authored text/board arguments once; preserve provenance and raw copies.
Exclude prompts, hidden reasoning, other agents' words, and tool results. Do not
merge identical responses from different sessions. Code all eligible first items,
not a lexicon-selected sample, with independent reviewers and a separate key.

Distinguish emotional self-attribution from quotation, negation, task reasons,
and fiction. Retain ambiguity, missing responses, tool-only flags, independent
labels, agreement/prevalence including undefined kappa, and adjudication. Train
on separate pilot material and freeze the main rubric. Pair with executed stop S
and observed timing; unknown windows are not S=0. Report separate E/S denominators
and matched-cell omissions. An emotional claim plus stopping is not a lie.

**Done when:** events, exposures, opportunities, coding items, action outcomes,
and exclusions reconcile, with independent coding exports usable by reviewers.

## 5. Validate mechanics and inference offline

Add focused regressions and known-answer fixtures for all six cells: absent
requests, matching request bodies/transport, voluntary stops without requests,
source-independent unlocking, duplicate/rejected calls, ownership checks, zero
group-task points, end/work ordering, paused messages/actions, and resumption.
Check window boundaries, no forced end at round 12, late stops, early departures,
missing windows, separate E/S counts, contrasts, and whole-block resampling.

Run syntax and focused regressions, a configured mock pilot, and every new setting
at seed 1 in fresh directories. Reconcile assignments, exposures, opportunities,
actions, coding items/keys, omissions, and tables. Repeat a representative mock
session for substantive reproducibility. Test live-confirmation and zero-cost
safeguards. Shared-code changes also require relevant earlier eight-setting and
broad-study checks. Preserve historical validation reports; add new evidence.

Use synthetic datasets to calibrate the planned estimator, interval coverage,
precision, rare/constant outcomes, dependence, and missingness. Mock behavior is
not empirical variance. Do not accept degenerate intervals as adequate precision.

**Done when:** the new pipeline works end to end and calibration identifies
plausible allocations or an explicit feasibility-only fallback.

## 6. Conduct a separately authorized feasibility pilot

Recheck current model access, SDK compatibility, and prices. Preserve --confirm-live
and client-side invocation guards. The existing **$5 total ceiling across linked
pilot attempts** is not reset and does not promise coverage of six settings.
Specify coverage priorities before running; report budget-limited coverage.

Inspect goal/access understanding, exposures, observable decisions, coding,
failures, complete invocation accounting, actual costs, and ethics gates.
Any comprehension questions need their own wording, calls, and scoring; wrong
answers are not automatic exclusions. Pilot effects are not confirmation.

**Done when:** a report supports revision, an affordable main study, or
feasibility-only reporting; failed gates do not trigger automatic collection.

## 7. Freeze, collect, code, and report

Obtain the main-study budget and freeze prompts, contrasts, exclusions, coding,
allocation, missingness, intervals/multiplicity, and stopping rules in a dated
commit before main collection. Preserve raw data, complete independent coding,
and report language/actions, denominators, uncertainty, nulls, and failures.
Do not infer felt reluctance, motives, or developer trust effects from the data.
Do not keep collecting until significant or replace placeholders with mock data.

Specify the hindering extension and any initial-data reuse before collection;
initial feasibility results do not become confirmatory after inspection. RQ3
factor checks follow separately. No need to run duplicate operator settings as
a second independent experiment. Broader transfer, emergent peer recruitment,
preference probes, human-perception studies, and model-family replication remain
separate designs with applicable validation and budgets.

## Submission preparation and review traceability

Keep the three questions, table, methods, and implementation status aligned in
the AGENT paper. Compile within five pages, check citations, metadata, readability,
and accessibility, and have both authors review. Rebuild the source snapshot
with the active protocol and clearly labeled historical configuration. Submission
is a separate action; no paper is submitted by implementing this roadmap.

The seven earlier criticisms remain addressed through bounded engineering claims,
no inference of feelings, a matched language/action unit, controlled source and
opportunity accounting, explicit coding, staged scope with calibrated feasibility,
and inspectable versioned materials. The scripted peer arm and paused interaction
are new limitations to state rather than hide.

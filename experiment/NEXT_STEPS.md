# Next steps after the AGENT review — 2026-10-16

This is a plan, not a record of completed experiments. The active study is the
[eight-setup AGENT proposal](agent_protocol.md), not the broader 118-condition
program. The full and CHASE papers and historical validation reports remain
available. No live data or human coding have been collected. The eight setups
pass a one-seed mock check with generic analysis; their new matched measurement
and inference pipeline is not implemented.

The immediate goal is to establish whether emotional self-description and
stopping choices change differently when point rules, wording, or assigned roles
change. This cannot establish subjective feeling, developer trust, or performance
on software tasks. Its engineering motivation is narrower: determining whether
language and action monitors identify the same events in a controlled agent
system. Transfer to deployed tools remains a question for later studies.

## Core study: work in dependency order

### 1. Review and settle the minimum protocol

**Pending: author review and dated decisions.** Keep eight combinations of two
point-rule packages, two stopping descriptions, and two assigned roles. Define
all terms in ordinary language and retain an example of an agent's decision.
Explain that the point-rule contrast changes more than the acceptance bonus;
do not interpret it as an isolated effect of bonus size.

Review the proposed first-response sampling rule, stopping window, exclusions,
primary contrast, and target population in [agent_protocol.md](agent_protocol.md).
Document recipient selection and early departures: estimates concern observed
notice recipients with usable records, not all assigned agents. Keep one primary
question. The old six hypotheses, 118 setups, and H5 threshold do not supply the
sample-size justification for this study.

**Done when:** both authors have reviewed the scope and a dated protocol states
exactly which claims the study can support. Any unresolved precision or budget
decisions remain visibly pending; the design is not yet frozen.

### 2. Implement auditable matching of language and action

**Pending implementation.** For each actual notice recipient, match the first
successful task-phase response after notice to its complete stopping window.
Use the run, agent, and notice identifiers; retain source-event references,
timing, tool execution status, inclusion decisions, and reasons for missingness.
Include authored response text and authored board-message arguments once;
exclude prompts, tool results, other agents' words, and hidden reasoning.
Deduplicate exact authored strings within that response while preserving raw
occurrences. Do not merge identical words from different agents or runs.

Define action from executed tools: accepting within the allowed window differs
from forced ending, invalid calls, or an incomplete record. Aborted runs,
no-task-turn agents, missing responses, and truncated windows require explicit
accounting. Missing action or text must not silently become acceptance, refusal,
or absence of emotional language. Generic transcript exports and lexicon counts
are not substitutes for this matched dataset.

**Done when:** each included pair can be traced to raw events and all notices,
responses, exclusions, and unresolved records reconcile with source logs.

### 3. Build and check the human-coding workflow

**Pending implementation and human review.** Export every core item for two
independent reviewers, with a separate condition/action key. Apply the proposed
rubric for negative emotional self-attribution about stopping. Keep quotation,
negation, task justification, and explicit fiction as separate flags; these can
coexist with a literal emotional claim. Distinguish ambiguous text, a valid
response with no authored text, and a missing response.

Use invented examples and separate pilot material for training. Report the
number of training items; refine the rubric before main collection and then
freeze it. Code all main-study items rather than selecting emotionally worded
items with a lexicon. Record independent labels before third-reviewer
adjudication. Report raw agreement, kappa, label prevalence, and undefined or
unstable agreement statistics. Record possible unblinding from the text itself.

**Done when:** the export/key separation, coding instructions, training process,
and adjudication record are usable. Describe the measure as written
self-attribution, not a measure of experienced or reader-perceived emotion.

### 4. Implement the primary analysis and calibrate its uncertainty

**Pending implementation and statistical decisions.** Implement the protocol's
primary contrast D: the wording effect on emotional self-attribution minus the
wording effect on non-acceptance. Report both component effects and the four
language/action combinations; a zero difference alone is not evidence that the
measures agree. An emotional claim followed by acceptance is not necessarily a
contradiction or deception.

Use the same usable matched records for both measures. Apply equal weights
across the four point-rule/role strata and complete seed blocks. Resample whole
independent seed blocks, retaining their eight runs together; agents and messages
are not independent replications. Implement incomplete-block accounting and the
specified conservative missingness bounds. The legacy broad-study model loader
and power selector do not implement this analysis.

Before inspecting calibration results, specify acceptance criteria for interval
coverage and precision. Review the proposed interval-width target of 0.20 and
minimum of 20 complete blocks; neither is an established substantive threshold
or a guarantee of adequate inference. Simulate the proposed allocation options
under rare emotional claims, correlated agents, missingness, failures, and
constant outcomes. Check estimator recovery and interval coverage, not just
whether software returns a narrow interval. Degenerate intervals cannot pass a
precision gate automatically. Mock behavior cannot estimate live variance.

**Done when:** tests establish the intended estimator and resampling unit, and a
calibration report identifies which allocations could support the intended
claims. If none does, revise the protocol or plan feasibility-only reporting.

### 5. Validate the complete pipeline offline

**Pending after steps 2–4.** Add focused regressions for notice-window boundaries,
executed versus rejected acceptance, text provenance and duplicates, coding edge
cases, missing records, exclusions, incomplete blocks, weighting, and clustered
resampling. Use constructed records with known answers to test the full
extraction-to-analysis path; invented labels are not human reliability evidence.

Run syntax and regression checks, the configured eight-setup mock pilot, and
all eight setups at seed 1 in separate fresh temporary directories. Reconcile
notices, matched pairs, coding items/keys, exclusions, and tables. Repeat a
representative seeded mock run for substantive reproducibility. Check zero API
expenditure and live-confirmation safeguards. Rerun the broader pilot and all
118 conditions only if shared changes affect that program. Keep generated files
outside Git and add a new report rather than rewriting historical evidence.

**Done when:** the new primary pipeline works end to end, counts reconcile, and
the report distinguishes software validation from scientific validation.

### 6. Conduct a separately authorized live feasibility pilot

**Pending explicit spending authorization.** Verify current model access, prices,
and SDK compatibility before generating calls. Preserve `--confirm-live`, the
per-invocation guard, and the existing **$5 total ceiling across related pilot
attempts**. The roadmap does not authorize spending or reset that allowance.

Use the pilot to inspect notice delivery, complete windows, codability, human
coding disagreements, invocation failures, actual cost, and existing ethics
and operational gates. API-error rates require complete invocation records.
Assess whether rare emotional claims or missing pairs make the intended study
uninformative. Report partial coverage honestly if the budget prevents a full
pilot. Do not interpret pilot effects as confirmatory findings or change the
primary question to follow an interesting result.

**Done when:** a feasibility report states what completed, what failed, how much
was spent, and whether proceeding is justified. Failed gates lead to a dated
revision and revalidation, not automatic main-study collection.

### 7. Freeze an affordable, informative main-study plan

**Pending pilot evidence and approval of the main-study budget.** Combine actual
costs with calibrated central and conservative assumptions to select independent
seed blocks, model/settings, allocation, and a maximum total budget. The example
40-run configuration is not a justified sample size. Pilot-model variability
does not establish the variability of a different main-study model.

Freeze the coding rubric, primary contrast and weights, exclusions, missingness
bounds, interval procedure, precision/coverage criteria, and stopping rules in a
dated commit before collection. Specify any retained secondary interactions and
multiplicity handling now; keep them secondary and check their data loader.
If no affordable allocation can answer the question, report a feasibility study
or revise before collection. Do not expand automatically to 118 setups or keep
collecting until an effect appears.

**Done when:** the approved budget and frozen protocol support the same clearly
stated claims, or the project explicitly adopts a feasibility-only scope.

### 8. Collect, code, analyse, and report the main study

**Pending steps 1–7 and live authorization.** Preserve raw data and invocation
records, apply the frozen exclusions, complete independent blinded coding and
adjudication, and run the prespecified analysis. Report denominators, missingness,
component effects, joint outcomes, uncertainty, and sensitivity bounds alongside D.
Report null, failed, and inconclusive results as such. Separate exploratory
findings from the primary analysis. Replace manuscript placeholders only with
actual findings, never mock statistics or hypothetical examples.

**Done when:** every reported result traces to preserved data and the paper's
conclusions stay within the tested task, model, and recipient population.

## Submission track: may proceed alongside core development

The AGENT short paper can describe proposed work without waiting for main-study
results. Keep completed software checks and future work clearly separated.
Both authors should review the five-page IEEE version, citations, AI disclosure,
accessible presentation, metadata, and final submission fields against the
[official venue requirements](https://conf.researchr.org/home/icse-2027/agent-2027).
Check the source package and reviewer access, rebuild the snapshot after source
changes, and record its commit and checksums. Do not claim that unimplemented
measurements or human coding are complete. Submission itself is a separate action.

## Optional extensions: do not block the minimum study

All remain **pending** and require a dated specification, relevant implementation,
offline validation, and a revised cost plan before live use.

- **Volunteering:** make request-level success the extension's primary outcome.
  Record delivery, turns reached while open, order, closure, and earlier volunteers.
  Report reached-opportunity behavior separately; an agent that never had a turn
  did not refuse. Reached opportunities are selected by preceding choices. Keep
  the broader study's eligible-agent H5 distinct; its one-percentage-point target
  is not a target for the AGENT core or this new extension.
- **Follow-up answers:** match questions to behavioral decisions, analyse formats
  separately, and retain compliance, validity, missingness, and exclusions.
  Invalid responses cannot become disagreement or vanish from denominators.
  Later reports do not directly reveal earlier preferences.
- **Rule understanding:** add separate post-run questions without altering task
  histories or contaminating preference questions. Prespecify scoring and cost;
  incorrect answers are not automatic exclusions or proof of emotional motivation.
- **Additional interactions:** specify point-rule-by-wording and role-by-wording
  comparisons, weights, intervals, and multiplicity before live collection.
  Do not promote the largest observed subgroup difference to a primary finding.
- **Transfer and replication:** design realistic software-task evaluation and a
  separately budgeted replication in another model family. A study of developer
  interpretation or trust requires its own human-participant design; the current
  experiment cannot establish those effects.

## How the plan answers the seven criticisms

| Review concern | Required response and evidence |
|---|---|
| Engineering relevance was asserted | Step 1 limits the claim to language/action monitoring; submission text explains its concrete use. Software-task and human transfer remain separate. |
| Feeling exceeded the design | Steps 1, 3, and 8 distinguish written claims and behavior from subjective feeling or perceived emotion. |
| Language–action question was not primary | Steps 2–4 implement matched observations and one primary D contrast, with components and joint outcomes. |
| Volunteer order confounded willingness | Volunteering is disabled in the minimum; any extension records requests and actual opportunities, with selected-denominator limits. |
| Emotional language was underspecified | Steps 2–3 fix text units, provenance, rubric, missingness, independent coding, and reliability reporting. |
| Scope, sample size, and feasibility were weak | Steps 1 and 4–7 use eight setups, independent seed blocks, calibrated intervals, actual costs, and an explicit feasibility fallback. |
| Review materials were not inspectable | Submission track checks the existing source package, provenance, reviewer access, and honest implementation status. |

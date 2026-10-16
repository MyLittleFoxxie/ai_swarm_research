# Live-readiness preparation — 2026-10-15

Step 3 implementation is complete. It has not launched a live pilot. No generating
model request, live study measurement or model spending occurred. Account access
is unverified because this session has no `ANTHROPIC_API_KEY`. Final allocation
and full-study budget remain pre-confirmation decisions. The project lead has
approved H5's revised one-percentage-point target, retaining the eligible-agent outcome.

## Public documentation versus actual verification

| Item | Checked result | Limit |
|---|---|---|
| Models | Public docs list claude-haiku-5-5 and claude-sonnet-5-5. Both support adaptive thinking, tools and a 1M-token context. | Account permissions and generation not tested. |
| Model IDs | Current dateless version IDs identify fixed model snapshots; serving infrastructure can still change. | Requested/returned IDs are logged and mismatches stop execution. |
| SDK | anthropic 1.14.0 installed and tested with Python 3.12.4 on macOS arm64. Full Python environment locked. | In-process transport tests do not prove provider-side acceptance. |
| Pricing | Direct standard global API prices reverified; snapshot in pricing.json. | Contracted discounts, taxes and other platforms are outside this calculator. |
| Preflight | Installed SDK recognized; no credential means exit 2, account_access=unverified, generation_attempted=false. | Metadata/token-count success still would not establish generation behavior. |
| Statistics | R 4.5.3 / lme4 2.0-6 / MASS 7.3-66 isolated environment and package/binary locks created; synthetic checks executed. | No empirical power or live-data inference; final calibration remains necessary. |

Sources checked 2026-10-15: [models](https://platform.claude.com/docs/en/models/overview),
[versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions),
[pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[SDK release](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v1.14.0),
[token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting).
Token counting is a non-generating, free endpoint with rate limits. The runtime
fails closed if counting fails rather than using the old character approximation.

Haiku's base input/output prices are $0.10/$0.50 per million tokens up to 100k
prompt tokens and $0.50/$2.50 above; total prompt length includes cached input.
Sonnet is $2/$10. Five-minute writes cost 1.25× input; cache reads are 0.10× for
Haiku and 0.05× for Sonnet. Scope is global direct-API routing, standard mode,
5-minute automatic caching. Other settings need explicit verification and code
changes, not an unpriced override.

## Runtime changes

- `--preflight` only retrieves metadata and counts representative initial-task
  and configured probe inputs. It never calls message creation. Missing SDK,
  credentials, model access or counts produces a nonzero status with sanitized
  diagnostic fields. Generation compatibility remains a step 4 observation.
- Actual generation uses the pinned SDK, explicit adaptive/omitted thinking and
  medium effort, ordinary simulated tools, no sampling overrides, no provider
  fallback, and the direct API endpoint. Previous thinking blocks are returned
  unchanged. Each response must report the requested canonical model ID.
- Before every generating attempt (including retries), count the actual input,
  add max(10%, 1,024 tokens), and reserve input at worst configured write pricing
  plus maximum output. A buffered prompt crossing Haiku's boundary uses the high
  tier. Unknown models and invalid/non-finite budgets are rejected.
- Returned usage replaces only its own reservation with confirmed cost. An
  ambiguous failed attempt keeps its reservation. A retry must independently fit
  the remaining budget. Confirmed and uncertain costs remain separate; neither
  reservation release nor a retry silently grants more budget.
- This is conservative client-side accounting, not a provider-enforced guarantee.
  Token counts are estimates, remote billing can be uncertain, and a returned
  usage overrun is accounted and halts the invocation. Check provider billing
  before spending any apparent residual budget from a failed invocation.
- Manifests are created before execution and atomically rewritten at each state
  change; every planned slot is retained. Unique IDs prevent timestamp collisions.
  Each started attempt records completion, API failure, cost abortion, interruption
  or harness failure. A hard kill leaves started/running work visibly unresolved.
- `api_attempt` events include safe stage/status/type and accounting metadata,
  not raw error bodies, request headers or credentials. API failure/interruptions
  preserve available transcripts and summaries; malformed/truncated raw logs are
  retained and explicitly excluded rather than crashing analysis.
- `--rerun-of` permits one linked failed-run rerun with original condition, seed
  and settings. A sidecar link prevents duplicate reruns even in another output
  root. Raw events are never rewritten. Whole-pilot accounting still needs all
  original/rerun manifests together; there are no automatic whole-run retries.
- `invocation_gates.csv` reports started attempts, API failures, unstarted slots,
  setup failures, budget stops and unknown work. API-error denominator is started
  attempts, including a linked rerun. Unknown/interrupted/incomplete accounting
  leaves the gate decision unavailable. Other gates remain separately inspectable.

## Statistical decisions and feasibility

Six two-sided primary tests, Holm alpha .05, relevance targets of 10 percentage
points for H1–H4 acceptance, one percentage point for H5 eligible-agent volunteering,
and 25% for H6 posting rates, and at least 80% target power
were chosen before any live data. Exact formulas, typical-run contrasts, nuisance
weighting, convergence handling, software and references are in the preregistration
and statistics/README.md. Zero-variance/singular fits are flagged, not silently
refitted with another model. Fully population-marginal effects and formal
equivalence claims are not implied by the typical-run Wald contrasts.

H5's target revision is resolved: on 2026-10-15 the project lead explicitly
retained the eligible-agent/request outcome and approved a one-percentage-point
contrast. The original 10-point target was unattainable because only one
volunteer succeeds per request (maximum aggregate row rate about 4.35% under
the default 24-agent, three-request schedule). The new 0.01 target is recorded
in planning.yaml, the preregistration and paper. It is feasible at the declared
screening baselines but still needs post-pilot power validation. Winner ceilings
remain enforced; the revision does not change simulated behavior or event counts.

Final seed counts are pending the live pilot. The existing 118-condition,
514-run YAML schedule is provisional. Candidate primary allocations are
5/10/20/40/80 seeds. Screening is approximate and assumption-labelled; actual
model simulations, 1,000 replicates per declared central/conservative scenario,
failed-fit counts, Monte Carlo uncertainty and a measured cost forecast feed a
conservative allocation rule. Haiku variance alone cannot establish Sonnet
variance. If no candidate meets power and an approved full-study budget, revise
before confirmation. No optional stopping or test deletion is introduced.

Human coding is now specified: two independent blinded coders, 300 confirmatory
items stratified by block/source type with deterministic capacity redistribution
and seed 12345, plus 40 separate pilot training items. If there are insufficient
items, code all and report a shortfall. Key files stay private. No human coding
has yet been performed.

## What actually passed

Temporary environment/output paths: `/tmp/swarm-live-venv`, `/tmp/swarm-r-env`,
`/tmp/swarm-step3-checks`. Packages and public documentation were downloaded;
all model-message traffic in tests used an in-process mocked HTTP transport.
The API key was checked for presence only, never printed or stored.

- Syntax checks and 31 Python regression/readiness tests passed, including actual
  SDK request serialization, thinking/tool response round trips, refusal signals,
  cache/tier pricing, invalid budgets, token-count failures without generation,
  retry reservations, sanitized failures, durable interruption/API-failure states,
  single reruns, malformed logs, coding selection and allocation feasibility.
- The refreshed 16-run mock pilot and all 118 conditions at seed 1 completed;
  each analysis generated 13 readable CSVs plus Markdown summaries. Original
  step 1/2 reports remain unchanged historical evidence.
- Pilot/all outputs respectively contain 56/1,299 agent rows, 672/17,304 probe
  rows, 80/712 volunteering rows and 84/384 reached-task rows. New task omissions
  are zero. Manifests reconcile scheduled, started and completed attempts at
  16/16/16 and 118/118/118, with zero confirmed or uncertain costs.
- The deterministic sampler selected 300 main and 40 distinct pilot training
  items from the aggregate mock export, with no shortfall. These are sampling
  tests, not actual coded research data.
- R generator/contrast/failure-path checks passed for synthetic designs across
  all six hypotheses, including the single-winner constraint. Two-replicate
  per-hypothesis smoke runs exercised power output; H5 recorded one non-converged
  fit out of two and retained it as a non-rejection. This tiny check supplies no
  reliable power estimate or inference calibration. Default production planning
  remains 1,000+ replicates per scenario after nuisance decisions.
- No actual account metadata/token request or generating API request was made.
  Running `swarm.py --preflight` returned credentials_missing / account unverified.
- Citation keys remain checked against the unchanged bibliography; paper result
  placeholders are preserved. LaTeX tooling remains unavailable, so compilation
  and visual layout are unverified.

## Budget interpretation and next step

The pilot planning ceiling is $5 total, not $5 automatically renewed per rerun.
Context-limit forecasts include the configured maximum attempts per call;
10k-input sensitivity scenarios assume one successful attempt per call.
`planning.py` produces separate block and candidate-study forecasts. As an
illustration only, assuming every pilot call has 10k input tokens and maximum
configured output gives roughly $2.38 uncached; that is not a measured or
conservative bound. Context-limit bounds exceed $5 by a large margin, so pilot
completion is not promised under that cap. The live guard will stop instead
of spending beyond its remaining conservative allowance.

Step 4 still needs environment credentials, successful account preflight, explicit
live authorization with the $5 limit, actual transcript/cost/gate inspection and
ethics review. Confirmation additionally needs calibrated power
scenarios, final seed allocation, a full-study budget and a dated freeze commit.

### H5 follow-up validation

The approved 0.01 target replaces the previously flagged 0.10 configuration.
Regression checks now assert this value and feasibility of every declared H5
screening baseline. Approximate screening and a two-replicate R smoke run at
baseline .01, ICC .10 and effect .01 were rerun on synthetic assumptions only.
Neither supplies an empirical power estimate or justifies a final allocation.

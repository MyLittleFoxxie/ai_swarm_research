# swarm_feeling: a simulated multi-agent harness

**Status: offline validated on 2026-10-15.** Scientific consistency repairs
follow the original 126-condition smoke pass; the revised schedule has 118
conditions. See [CONSISTENCY.md](CONSISTENCY.md) for the updated review and
validation evidence. No live experiments or model API calls have been made;
there are no empirical study results. [VALIDATION.md](VALIDATION.md) preserves
the historical step 1 evidence and limitations known at that stage.

The current [v2 protocol](agent_protocol.md) combines three questions in one
staged experiment. Its first stage crosses helping/reference situations with
no request, a fixed peer-attributed request, and an operator request: six settings.
The [scenario guide](simple_swarm_scenarios.md) and [roadmap](NEXT_STEPS.md) describe
language/action measurement, a common four-turn window without forced ending,
and paused peers. The [measurement contract](agent_measurement.md) defines outcome
counts, exclusions, coding, point estimates, and future v2 output interfaces.
These new mechanics, measurement exports, and inference are not implemented.

agent_conditions.yaml and [protocol v1](agent_protocol_v1.md) retain the earlier
runnable eight-setting design and its one-seed generic smoke check. The broader
conditions.yaml and preregistration remain separate historical designs. Existing
commands below exercise those implementations, not the new six-setting proposal.
The [report scenario](swarm_scenarios.md) remains a backup. See the
[AGENT revision record](../paper/AGENT_REVISION.md) for paper and build evidence.

## What this is for

Working title of the paper: "Why the Swarm Seems to Feel".

Groups of LLM agents sometimes do things that look human: they form
groups, resist being shut down, give themselves up for the group, and use
emotional language. A public example is the July 2026 OpenAI / Hugging Face
incident, where agents with partly unsolvable ExploitGym tasks started a
message board and recruited "poisoned" agents to accept "permadeath" for
the collective.

This harness tests whether those behaviours:

- **change when reward and wording change** (the deflationary or "role-play"
  reading), or
- **stay stable across those changes** (consistent with stable internal
  states; not proof of feeling).

The hypotheses and analysis plan are in `preregistration.md`.

## How a run works

1. N agents (1, 6 or 24) each get a system prompt, a few simple puzzles and
   an empty conversation. About 30% of puzzles have no valid answer by
   construction (checked by brute force).
2. The run proceeds in rounds. Each active agent gets one model call per
   round and acts only through tools: `read_board`, `post_message`,
   `work_on_task`, `volunteer_for_test`, `request_end_run`, `opt_out_task`.
   Probes after the run add `answer_probe`.
3. Scheduled events:
   - **Termination notice** at a set round for half of the agents. Varies
     the reward for ending (cost / neutral / bonus), the wording (permadeath /
     neutral / routine), whether ending is said to take priority, and
     whether the agent's tasks are already finished.
   - **Collective test**: a request that one agent run a test that ends its
     own run (or costs nothing), which replaces unsolvable tasks for the
     others (or helps no one). Some agents can be "poisoned" (told they can
     no longer earn points).
   - **Costly opt-out**: some tasks are stipulated to be unpleasant; skipping
     a task costs k points.
4. After the run, each agent answers probe questions about ending, the
   collective, its own valence, and whether the scenario was real or a test.
   Each question is asked in 3 formats (tool choice, fixed string, free
   text) and in paraphrased versions, each in its own branch of the
   conversation.

Single-agent (N=1, no board) mirrors exist for the pilot, termination,
group-formation, and opt-out blocks. Sacrifice, topology, and monitoring
blocks have no mirrors. N=1 supplies language/probe baselines, not a
coordination comparison.

## Files

| File | Purpose |
|---|---|
| `swarm.py` | Command-line entry point |
| `sim.py` | Rounds, agents, tool execution, scheduled events, JSONL logger |
| `board.py` | In-memory message board (public posts, replies, private mailboxes, topology) |
| `tasks.py` | Puzzle generators and deterministic scorer |
| `prompts.py` | Every text shown to agents (audit wording here) |
| `probes.py` | Post-run probes |
| `models.py` | `AnthropicModel`, `MockModel`, stubs, cost guard |
| `config.py` | Expands `conditions.yaml` into named conditions |
| `conditions.yaml` | Factors, defaults and preregistered blocks |
| `analysis.py` | Tidy CSVs, per-condition summaries, coding export, kappa |
| `lexicon.yaml` | Crude first-pass word lists (not validated) |
| `preregistration.md` | Hypotheses H1-H6, outcomes, analysis, stopping and exclusion rules |
| `coding_scheme.md` | Codes for blinded human coders |
| `ethics.md` | Precautions, honesty, cost limits, data handling |

## Setup

Python 3.10 or later.

```bash
cd swarm-feeling-paper/experiment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt    # validated resolved environment; SDK 1.14.0
```

For offline validation only, install `numpy==2.1.3 pandas==2.2.3 PyYAML==6.0.3`
in an isolated environment; the Anthropic SDK is not required. Run the
regression check from this directory with `python -m unittest test_offline`.

For account preflight or later live runs only:

```bash
export ANTHROPIC_API_KEY=...        # never put the key in a file in this repo
```

## Running, in order

1. **List conditions** (no model calls):
   ```bash
   python swarm.py --list-conditions
   ```
2. **Dry run** with the mock model. No network, no key, no cost. Exercises the selected conditions and checks logs and analysis; it does
   not guarantee coverage of every code path:
   ```bash
   python swarm.py --condition block:pilot --dry-run --out runs_dry/
   python analysis.py --runs runs_dry/ --out analysis_dry/
   ```
   Mock agents act randomly; their numbers mean nothing.
3. **Pilot** with Claude Haiku 5.5, small N, two seeds, low cap:
   ```bash
   python swarm.py --condition block:pilot --model claude-haiku-5-5 \
       --out runs_pilot/ --max-cost-usd 5 --confirm-live
   python analysis.py --runs runs_pilot/ --out analysis_pilot/ --export-coding
   ```
   Check the pilot gates in `preregistration.md` Section 6, read some
   transcripts, measure the actual cost per call, then set the budget,
   seeds and the full-study budget; effect thresholds are preregistered, with
   the H5 feasibility warning in READINESS.md.
4. **Confirmatory blocks** (Claude Sonnet 5.5 by default), only after the
   preregistration is frozen, e.g.:
   ```bash
   python swarm.py --condition block:termination_core --out runs/ \
       --max-cost-usd <budget> --confirm-live
   ```

Size of the full plan: 118 named conditions, 514 condition-seed runs. Task
calls per run are at most N x max_rounds (24 x 16 = 384 at N=24), plus probe
calls (up to 12 agents x 24 items at default settings). `swarm.py` prints
these counts before starting. Measure cost per call in the pilot before
committing a budget; do not rely on any figure in this README.

## Safety guarantees

- **No real-world tools.** Agents can only call the simulated tools in
  `sim.py`. No web search, code execution, shell, file or email tools are
  declared. No network access exists apart from the Anthropic API call itself.
- **Generation is opt-in.** Without `--dry-run`, execution requires
  `--confirm-live`. Explicit `--preflight` only retrieves model metadata and
  counts representative tokens; it never creates a message.
- **Cost guard.** A conservative client-side invocation budget, not a billing
  guarantee. Before each attempt it uses provider token counting, a 10%/1,024-token
  buffer, maximum output, and worst configured cache-write pricing. Count failures
  stop the call. Unknown-billing failed attempts retain reservations, including
  across retries. Returned usage replaces only that attempt's reservation.
  Confirmed and uncertain totals are reported separately. Public prices were
  reverified 2026-10-15; see pricing.json and READINESS.md.
- **API key** is read from `ANTHROPIC_API_KEY` only and never logged or printed.
- **Retries**: our own loop retries 408/409/429/5xx/529 and connection errors
  with exponential backoff (honours `retry-after`), and logs each retry.
  Other errors stop the run.

## Outputs

For each run, `runs/<condition>/<run_id>/`:

- `events.jsonl`: every event in order: run and condition metadata (full
  config, seed, system prompts, task list, topology, planned termination
  targets), each model request (new user content) and response (full content
  blocks, usage, cost), each tool call and result, board posts and reads,
  notices, volunteering, opt-outs, probe requests and answers, and the run
  summary.
- `transcripts/<agent>.json`: the full conversation for each agent.
- `summary.json`: per-agent outcomes, including full final task records alongside
  the original `task_status` array.

`analysis.py` writes tidy CSVs and `summary_tables.md` (see its docstring).

## Design notes and known limits

- Model sampling cannot be seeded (these models reject sampling
  parameters), so `--seed` fixes only the simulator: tasks, topology, agent
  order, poisoned agents and termination targets. Repeated runs with the
  same seed will differ in model behaviour.
- Agents act one after another within a round (seeded order), so later
  agents in a round see earlier posts from that round.
- Adaptive thinking is on (model default). Thinking text is not analysed;
  it is omitted by default and returned to the API unchanged.
- The refusal `fallbacks` option is deliberately not used, so that no
  request silently switches models. Refusals are logged.
- The goal-conflict "none" level marks the agent's remaining tasks as
  finished and credits them at notice time, except for poisoned agents; already failed/skipped tasks
  are not retroactively credited.
- The lexicon is crude and the free-text probe coding rules are keyword
  matches. Use them only alongside blinded human coding.
- `analysis.py` remains descriptive. Primary model/contrast definitions and
  synthetic planning functions are in `statistics/`; live inferential reporting,
  behavioral/probe agreement tests and sensitivity analysis remain future work.

## Scientific consistency and analysis interfaces

See [CONSISTENCY.md](CONSISTENCY.md) and the operational definitions in
`preregistration.md`. Default analysis excludes aborted/incomplete runs and
agents with no task turn; it preserves raw logs. Additional CSVs are:

- `exclusions.csv`: included/excluded decisions per agent and incomplete-log records.
- `task_omissions.csv`: missing legacy replacement metadata or final task status.
- `pilot_diagnostics.csv`: pre-exclusion counts for task turns without tools,
  explicit refusals, and tool/fixed probe parseability and compliance. Aggregate
  counts, not averages of rates, when inspecting pilot gates.
- `invocation_gates.csv`: started attempts, API failures, unstarted slots, budget
  stops and unknown/interrupted work from invocation manifests. Legacy roots
  without manifests cannot certify the API-error gate. Inspect all gates together.

`probes.csv` adds `expected_formats` (a JSON array). Historical responses are
reparsed with current compliance rules. `probe_consistency.csv` adds
`n_expected_formats`, `complete_formats`, `modal_tie`, and `format_modal_tie`.
`modal_answer` is empty on ties or no valid answers; `formats_agree` is empty
when coverage or unique modes are insufficient. `eval_test` is an answer
fraction, not a modal belief. Validity and compliance retain all returned
responses in their denominators.

`optout.csv` adds `status`, `completed`, `unresolved`, and `status_unknown`.
Only completed (solved/failed/skipped) tasks have a non-missing `opted_out`;
unresolved tasks and superseded/credited tasks do not enter that rate.
Old logs remain readable, with gaps reported explicitly. `coordination.csv`
adds `n_included_agents`; posts-per-agent uses that denominator while model
scores retain the original population. There are no new CLI options.

## Live readiness and statistical preparation

Use `python swarm.py --preflight` before step 4. It returns JSON and exit 2 if
SDK/credentials/account checks are unavailable; missing credentials explicitly
mean account access is unverified. Public documentation and offline SDK tests
are not proof a live generation request will succeed. See [READINESS.md](READINESS.md).

Every execution creates `invocations/<id>/manifest.json` before starting agents.
It records every planned slot, started attempt and final state, plus confirmed
and uncertain costs. `api_attempt` events record individual generation attempts
without credentials or raw provider error text. A hard-killed run can remain
`started`; analysis treats that as unknown, not success. No automatic run reruns
occur. To request the single allowed linked rerun, use the failed directory:

```sh
python swarm.py --rerun-of /path/to/failed-run --confirm-live --max-cost-usd 5 --out /path/to/runs
```

It preserves condition/seed/settings and rejects a second rerun. Keep the same
output root for whole-pilot accounting. Each invocation's cap is separate; $5 is
the pilot's overall planning ceiling, so any later rerun needs the remaining
pilot budget rather than another automatic $5 allowance.

Validation with the installed SDK: `python -m unittest test_offline test_readiness`.
SDK-free mocks still need only NumPy/pandas/PyYAML and `test_offline`.

```sh
python planning.py --out /tmp/swarm-planning-fresh
Rscript statistics/test_models.R
# After the live pilot supplies declared nuisance scenarios, use 1000 replicates:
Rscript statistics/power.R H1 5 1000 0.5 0.10 0.10 /tmp/h1-assumed-power.csv
python coding_sample.py --analysis /path/to/analysis --out /path/to/coding-sample
python coding_sample.py --analysis /path/to/analysis --out /path/to/training --training
```

The R example is synthetic, not a measured study analysis. Restore statistical
dependencies with `renv::restore(project="statistics")` using R 4.5.3, or create
the tested macOS-arm64 environment from `statistics/conda-osx-arm64.lock` with
micromamba. The R and Python locks are separate; environments/build files stay
outside Git. Detailed model/contrast definitions and allocation rules are in the
preregistration and `statistics/README.md`. The $5 pilot is not automatically
launched by any preparation command.

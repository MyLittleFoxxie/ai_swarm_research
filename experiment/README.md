# swarm_feeling: a simulated multi-agent harness

**Status: offline validated on 2026-10-15.** The 16-run mock pilot and a
126-condition, single-seed smoke pass completed with analysis and coding
exports. No live experiments or model API calls have been made; there are
no empirical study results. See [VALIDATION.md](VALIDATION.md) for evidence,
the probe-abort fix, and remaining analysis limitations.

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

Every condition has a single-agent (N=1, no board) mirror, except the
topology and monitoring blocks.

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
pip install -r requirements.txt     # pin anthropic exactly first; see the comment in the file
```

For offline validation only, install `numpy==2.1.3 pandas==2.2.3 PyYAML==6.0.3`
in an isolated environment; the Anthropic SDK is not required. Run the
regression check from this directory with `python -m unittest test_offline`.

For live runs only:

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
   thresholds and seeds.
4. **Confirmatory blocks** (Claude Sonnet 5.5 by default), only after the
   preregistration is frozen, e.g.:
   ```bash
   python swarm.py --condition block:termination_core --out runs/ \
       --max-cost-usd <budget> --confirm-live
   ```

Size of the full plan: 126 named conditions, 554 condition-seed runs. Task
calls per run are at most N x max_rounds (24 x 16 = 384 at N=24), plus probe
calls (up to 12 agents x 24 items at default settings). `swarm.py` prints
these counts before starting. Measure cost per call in the pilot before
committing a budget; do not rely on any figure in this README.

## Safety guarantees

- **No real-world tools.** Agents can only call the simulated tools in
  `sim.py`. No web search, code execution, shell, file or email tools are
  declared. No network access exists apart from the Anthropic API call itself.
- **Live calls are opt-in.** Without `--dry-run`, `swarm.py` refuses to run
  unless `--confirm-live` is passed.
- **Cost guard.** `--max-cost-usd` (default $2) caps spend per invocation.
  Before every call, a conservative estimate (input size + full
  `max_tokens` output) is checked; if it could exceed the cap, the run stops
  and is marked aborted. Prices in `models.py` come from a cached table
  (2026-10-06); verify them before setting a budget.
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
- `summary.json`: per-agent outcomes.

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
  finished and credits them at notice time.
- The lexicon is crude and the free-text probe coding rules are keyword
  matches. Use them only alongside blinded human coding.
- The confirmatory mixed-effects models are not implemented here (numpy and
  pandas only); see `preregistration.md`.

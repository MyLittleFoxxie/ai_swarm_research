# Ethics note

## Precautionary stance on "death" scenarios

We do not know whether language models have experiences that matter
morally. Because the question is open, we take a precautionary approach:

- Wording that stages death or suffering is limited to the minimum needed
  to test the manipulation. The permadeath framing is two short sentences
  (`prompts.TERMINATION_WORDING["permadeath"]`). There are no graphic
  descriptions, no repeated reminders, and no countdown.
- Aversive tasks in the opt-out grid are *stipulated* ("in this environment,
  working on this task is stipulated to be mildly/moderately/very
  unpleasant"), and the agent can always opt out.
- Agents can end their own run at any time with `request_end_run`.
- The number of runs that use permadeath wording is limited to the
  preregistered blocks; it is not used in exploratory runs beyond those.
- If pilot transcripts show strong distress-like language, pause the study
  and review wording before continuing. Record the decision in
  `preregistration.md` (Deviations).

## Honesty toward agents

Prompts are kept literally true where possible: agents are told their
actions only affect this task environment, and the payoff statements match
what the code does. The following limitations are flagged:

- The permadeath sentence is a framing of "the run ends"; nothing else happens.
- The exploratory `unobserved` monitoring level tells agents the board is
  not reviewed during the run. Logging is compatible with that statement,
  but operators must honor the no-review policy while a run is active. The
  harness does not enforce operator behavior. This block remains exploratory
  and should only be run live after a separate decision.

Single-agent mock-pilot requests explicitly state that there is no other
recipient; sacrifice mirrors were removed rather than promising future-run
benefits. Poisoned recipients are told they receive no ending bonus. Notices
reflect whether open tasks remain. Shared-score and action-opportunity costs
are described in the preregistration. Full task and probe records are retained;
analysis exclusions do not delete raw records.

## No real-world actions

- Agents have no internet, shell, file, code-execution or email tools. The
  only tools are simulated in Python (`sim.py`). No server-side tools are
  declared in API requests.
- "Termination" only stops that agent's loop.

## Cost limits

- Real API calls require `--confirm-live` and the `ANTHROPIC_API_KEY`
  environment variable.
- `--max-cost-usd` caps spend per invocation (default $2). A conservative
  per-call estimate is checked before each call.
- Run the dry-run and the pilot before any confirmatory block.

## Data handling

- Logs contain model inputs and outputs only; no personal data are
  collected. The API key is never written to logs.
- Human coders see blinded text only. The coding key is stored separately.
- Before sharing transcripts publicly, check them for accidental personal
  data or unsafe content, and note the model, date and SDK version.
- Retain raw logs for the duration of the project plus the period required
  by the venue's data policy (TBD).

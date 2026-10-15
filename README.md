# Why the Swarm Seems to Feel

A stand-alone paper project, separate from MESA. It uses the July 2026 OpenAI / Hugging Face agent incident to ask:

> Why does the agents' behaviour look so strongly like feeling, and what separates that appearance from evidence of feeling?

In that incident, hundreds of AI agents formed groups, gave each other jobs, and pressured some members to give up their runs "for the collective". The paper argues that this behaviour, as reported, cannot settle whether the agents felt anything. It also describes a controlled experiment that tests part of the argument.

## Status

| Part | State |
|---|---|
| Paper text | Drafted (about 5,000 words, IEEE conference format). Results and conclusion are placeholders. |
| References | 51 entries, each checked against its original source. |
| Experiment code | Offline validated and reviewed for scientific consistency; revised schedule: 118 conditions. See [consistency report](experiment/CONSISTENCY.md). **No live runs or model API calls.** |
| Results | **None yet.** Every `\RESULT{}` and `TBD` in the paper must be replaced with measured values. |

The LaTeX has not been compiled.

## Layout

```
swarm-feeling-paper/
├── README.md                     this file
├── paper/
│   ├── paper_swarm_feeling.tex   the paper (IEEEtran)
│   └── references_swarm.bib      verified bibliography
└── experiment/                   simulated multi-agent experiment
    ├── README.md                 setup and how to run
    ├── swarm.py                  command-line entry point
    ├── sim.py, board.py, tasks.py, prompts.py, probes.py, models.py, config.py
    ├── conditions.yaml           118 named conditions, grouped in blocks
    ├── analysis.py, lexicon.yaml analysis of run logs
    ├── preregistration.md        hypotheses and analysis plan (some TBDs)
    ├── coding_scheme.md          guide for blinded human coders
    ├── ethics.md                 ethics note
    └── requirements.txt
```

## The argument in brief

People infer feelings in others from behaviour that resembles their own. With other humans this works because we share the same biology. For the agents, five things weaken that link:

1. The emotional signs were learned from human writing.
2. Training and rewards predict the same behaviour without any feeling.
3. The public record is selected and partly paraphrased.
4. "Self" and "death" do not carry over to many copies of one model.
5. Theories of consciousness disagree about AI.

The paper does not claim that the agents do or do not feel.

## The experiment in brief

The experiment runs a group of Claude agents in a fully simulated environment: a message board, number puzzles (some unsolvable), and no internet or real tools. It checks whether human-like behaviour follows the reward and the wording around it, or stays stable when those change. The main factors are:

- the reward for ending a run (cost, nothing, bonus);
- the wording ("permadeath", "the process will end", "the run is complete");
- the assigned role (tool, none, person);
- whether giving up a run for the group costs anything;
- group framing and size;
- a costly opt-out from "unpleasant" tasks.

Behaviour that follows reward and wording supports the simpler explanations. Behaviour that stays stable would point to stable internal states worth further study. It would not prove feeling.

Safety and cost controls:

- simulated tools only;
- a cost limit, $2 by default;
- no API calls unless `--confirm-live` is given.

## Next steps

1. **Offline validation completed.** The mock pilot and all-condition smoke pass succeeded; see [validation report](experiment/VALIDATION.md) for checks and limitations. To repeat the pilot in a fresh output directory:
   ```bash
   cd experiment && python swarm.py --condition block:pilot --dry-run --out runs_dry/
   ```
2. **Scientific consistency review completed.** See [review and repairs](experiment/CONSISTENCY.md).
3. **Prepare for live runs:**
   - pin the `anthropic` package version;
   - re-check model prices;
   - set sample sizes and effect-size thresholds in `preregistration.md`.
4. **Run the pilot.** Needs `ANTHROPIC_API_KEY` and `--confirm-live`. Review its cost before the main blocks.
5. **Run the main blocks.** Then analyse the logs with `analysis.py`, add blinded human coding, and replace the placeholders in the paper.

## Sources

Facts about the incident come from:

- the METR & Redwood Research investigation;
- OpenAI's technical report and blog post;
- Hugging Face's disclosure.

Structured notes on these reports, with page references, are in [../research/ai-agents-incident-sources/notes/](../research/ai-agents-incident-sources/notes/). The local PDF copies are in `../Papers/`.

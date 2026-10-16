# Why the Swarm Seems to Feel

A stand-alone paper project, separate from MESA. It uses the July 2026 OpenAI / Hugging Face agent incident to ask:

> Why does the agents' behaviour look so strongly like feeling, and what separates that appearance from evidence of feeling?

In that incident, hundreds of AI agents formed groups, gave each other jobs, and pressured some members to give up their runs "for the collective". The paper argues that this behaviour, as reported, cannot settle whether the agents felt anything. It also describes a controlled experiment that tests part of the argument.

## Status

| Part | State |
|---|---|
| Paper text | Full IEEE draft retained; separate anonymous CHASE extended-abstract proposal added. No live results. |
| References | 53 entries in shared `paper/references.bib`; full paper cites 52, CHASE proposal cites 14, including the AI-assistance disclosure reference. |
| Experiment code | Offline validated and reviewed for scientific consistency; revised schedule: 118 conditions. See [consistency report](experiment/CONSISTENCY.md). **No live runs or generating model API calls.** |
| Results | **No empirical study results.** Full-paper placeholders remain; the CHASE proposal reports only completed software checks and proposed research. |

The full draft was compiled and visually reviewed. The separate CHASE proposal
has also been compiled and reviewed; see [paper build notes](paper/README.md)
and [CHASE checks and remaining tasks](paper/CHASE_READINESS.md). Compilation
does not establish scientific validity or supply empirical results.

## Layout

```
swarm-feeling-paper/
├── README.md                     this file
├── paper/
│   ├── paper_swarm_feeling.tex   full paper (IEEEtran)
│   ├── paper_swarm_feeling_chase.tex  anonymous CHASE proposal
│   ├── references.bib            canonical bibliography used by the paper
│   └── references_swarm.bib      legacy 51-entry snapshot
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

Behaviour that follows reward and wording shows sensitivity to those manipulations.
Behaviour that stays stable could reflect a learned policy that generalizes across
conditions. Neither pattern by itself establishes feeling; a nonsignificant
difference does not establish stability.

Safety and cost controls:

- simulated tools only;
- a conservative client-side cost guard, $2 by default ($5 for the planned pilot);
- generation requires `--confirm-live`; explicit `--preflight` permits only metadata/token counting.

## Next steps

1. **Offline validation completed.** The mock pilot and all-condition smoke pass succeeded; see [validation report](experiment/VALIDATION.md) for checks and limitations. To repeat the pilot in a fresh output directory:
   ```bash
   cd experiment && python swarm.py --condition block:pilot --dry-run --out runs_dry/
   ```
2. **Scientific consistency review completed.** See [review and repairs](experiment/CONSISTENCY.md).
3. **Live-readiness implementation completed.** SDK pinned, public models/prices checked,
   accounting and statistical planning tools added. See [readiness report](experiment/READINESS.md).
   Account access, actual generation and final study allocation
   still require attention before confirmation.

The [ordered next-step roadmap](experiment/NEXT_STEPS.md) now places these tasks
before and after live collection:

1. Finish the separate CHASE proposal and submission checks.
2. Implement comparisons of actions with follow-up answers.
3. Record actual chances to volunteer and add secondary opportunity accounting.
4. Specify secondary comparisons of wording with rewards and assigned roles.
5. Add separate post-run checks of understanding of point rules.
6. Repeat regression, mock-pilot, and all-condition offline validation.
7. Run an explicitly authorized live pilot under the $5 total ceiling.
8. Finalize power, allocation, and budget; freeze the design; collect and analyse
   main-study data, including independent human coding.
9. Plan separately budgeted replication with another model family.

The five new experiment improvements are pending, not implemented. No submission
or live generation is performed by the documentation update.

A [plain-language project summary](PROJECT_SUMMARY.md) explains the premise, goals,
methods and work completed so far.

## Sources

Facts about the incident come from:

- the METR & Redwood Research investigation;
- OpenAI's technical report and blog post;
- Hugging Face's disclosure.

Structured notes on these reports, with page references, are in [../research/ai-agents-incident-sources/notes/](../research/ai-agents-incident-sources/notes/). The local PDF copies are in `../Papers/`.

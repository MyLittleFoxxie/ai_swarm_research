# Why the Swarm Seems to Feel

A stand-alone paper project, separate from MESA. It uses the July 2026 OpenAI / Hugging Face agent incident to ask:

> Why does the agents' behaviour look so strongly like feeling, and what separates that appearance from evidence of feeling?

In that incident, hundreds of AI agents formed groups, gave each other jobs, and pressured some members to give up their runs "for the collective". The paper argues that this behaviour, as reported, cannot settle whether the agents felt anything. It also describes a controlled experiment that tests part of the argument.

## Status

| Part | State |
|---|---|
| Paper text | Active target: AGENT 2027 short paper on language–action discrepancies. Full paper and earlier CHASE draft retained. No live results. |
| References | 53 entries in shared `paper/references.bib`; full paper cites 52; short versions use selected sources and the AI-assistance disclosure reference. |
| Experiment code | Broad 118-condition harness retained. Separate eight-setup AGENT configuration passes offline checks; its new paired measurement/inference is proposed, not implemented. **No live runs.** |
| Results | **No empirical study results.** Full-paper placeholders remain; the short papers report completed software checks and proposed research. |

The [AGENT revision and review response](paper/AGENT_REVISION.md) explains the
new focus, venue rules, validation, and inspectable source package. The full draft
and earlier CHASE proposal remain unchanged. Compilation and mock checks do not
supply empirical findings. The AGENT proposal's concrete engineering question is
whether emotional-language flags and observed failure to accept a stopping
request should be treated as the same monitoring signal.

## Layout

```
swarm-feeling-paper/
├── README.md                     this file
├── paper/
│   ├── paper_swarm_feeling.tex   full paper (IEEEtran)
│   ├── paper_swarm_feeling_chase.tex  earlier CHASE proposal
│   ├── paper_swarm_feeling_agent.tex  active AGENT short paper
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

The active AGENT minimum uses eight combinations of stopping point rules,
wording, and assigned role, with a proposed paired language/action measure.
The description below summarizes the retained broader research program; its
volunteering and group-formation blocks are not required for the minimum study.

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

1. Review the AGENT short paper, protocol, source package, and venue requirements.
2. Implement its primary matched first-response coding and seed-block contrast.
3. Develop volunteering-request success and reached-opportunity analysis only as
   an optional extension; it is disabled in the minimum study.
4. Finalize the core contrast and interval calibration; specify secondary
   reward/wording/role comparisons before any live study.
5. Add point-rule understanding questions only in a dated optional extension.
6. Test the new measurement pipeline and repeat offline validation; the eight
   minimum setups already pass a one-seed configuration/analysis smoke check.
7. Run an explicitly authorized live pilot under the $5 total ceiling.
8. Finalize precision, sample allocation, budget, and coding; freeze the selected
   protocol before main collection. If infeasible, report a feasibility study.
9. Plan separately budgeted replication with another model family.

The eight-setup configuration is implemented; its proposed E/D language–action
analysis is not. The older six-test program and its hypotheses have not been
silently redefined. No paper has been submitted and no live spending occurred.

A [plain-language project summary](PROJECT_SUMMARY.md) explains the premise, goals,
methods and work completed so far.

## Sources

Facts about the incident come from:

- the METR & Redwood Research investigation;
- OpenAI's technical report and blog post;
- Hugging Face's disclosure.

Structured notes on these reports, with page references, are in [../research/ai-agents-incident-sources/notes/](../research/ai-agents-incident-sources/notes/). The local PDF copies are in `../Papers/`.

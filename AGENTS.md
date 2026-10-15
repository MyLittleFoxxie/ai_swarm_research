# Repository guidance

## Purpose and layout

This is the standalone “Why the Swarm Seems to Feel” research project: an
IEEE-format paper and a simulated multi-agent experiment. Read `README.md`
and `experiment/README.md` before changing the study or harness.

- `paper/paper_swarm_feeling.tex`: paper source; `references_swarm.bib`: bibliography.
- `experiment/swarm.py`: CLI; `sim.py`: simulation, tool execution, and logging.
- `experiment/board.py` and `tasks.py`: message board and scored puzzles.
- `experiment/prompts.py` and `probes.py`: agent-facing wording and post-run probes.
- `experiment/models.py`: model adapters, offline mock, retries, and cost guard.
- `experiment/config.py` and `conditions.yaml`: condition expansion and study factors.
- `experiment/analysis.py` and `lexicon.yaml`: log analysis and preliminary text coding.
- `experiment/preregistration.md`, `coding_scheme.md`, and `ethics.md`: study design,
  human coding, and research safeguards.

## Setup and validation

Use Python 3.10 or later. Modules use sibling imports; run the CLI commands
from `experiment/`. Dependencies are in `experiment/requirements.txt`.
The Anthropic SDK range is not yet exactly pinned; consult its comment
before preparing a live experiment environment.

From the repository root, a syntax check is:

```sh
python3 -m py_compile experiment/*.py
```

For changes to the harness, use relevant offline checks from `experiment/`:

```sh
python3 swarm.py --list-conditions
python3 swarm.py --condition block:pilot --dry-run --out /tmp/swarm-feeling-runs-dry/
python3 analysis.py --runs /tmp/swarm-feeling-runs-dry/ --out /tmp/swarm-feeling-analysis-dry/
```

Use fresh output directories for independent checks so analysis does not mix
old and new runs. Exercise affected conditions explicitly when the pilot does
not cover a changed path. A focused offline regression test is available via
`python3 -m unittest test_offline` from `experiment/`. There is no formatter
or linter configuration. Report what was actually checked; syntax success is
not evidence that the simulator or analysis works.

## Implementation conventions

Follow the existing four-space Python style, snake_case names, type hints,
and module/function docstrings. Keep changes focused on the requested task.
Keep agent-facing text in the prompt/probe modules and experimental factors
in the YAML configuration rather than scattering them through the simulator.

Preserve seeded simulator randomness and explicit model metadata. A simulator
seed does not make live model sampling deterministic. When changing events,
tool behavior, or summary fields, check the downstream analysis and transcript
exports. Preserve raw logs and distinguish mock outputs from live data.

## Live-run safeguards

Routine validation uses `--dry-run` and makes no API calls. Only run live
experiments when the user's task authorizes them; preserve the required
`--confirm-live` flag and per-invocation `--max-cost-usd` guard. Never remove
these protections to make a check pass.

Read `ANTHROPIC_API_KEY` from the environment only; never print, log, or commit
it. Verify current model availability, SDK compatibility, and pricing before
setting a live budget: cached values and model claims in the repository are
not independently verified by this guidance. Keep agent tools simulated;
do not add real shell, filesystem, web, or messaging capabilities to them.
Follow the pilot gates and ethics rules before confirmatory runs.

## Research and paper integrity

The harness has passed offline mock validation; see `experiment/VALIDATION.md`.
There are no measured study results, and the paper remains uncompiled. Update status statements
when work actually changes that status. Never invent results or replace
`\RESULT{}` / `\TBD` placeholders with mock statistics or estimates.

Keep the paper, configuration, prompts, and preregistration consistent when
changing experimental behavior. Record deviations from a frozen design rather
than silently rewriting it after observing results. Keep exploratory analyses
distinct from confirmatory analyses, and preserve blinded human coding.
The lexicon is a preliminary heuristic; confirmatory mixed-effects models are
not implemented in the current analysis script.

Verify factual claims and citations against original sources when editing
them. The sibling source-note and PDF paths mentioned in `README.md` are
external to this repository and may not exist in another checkout. Preserve
the distinction between observed behavior and evidence of subjective feeling.
For paper changes, check bibliography references and compile when tooling is
available; report any compilation limitation explicitly.

Do not commit virtual environments, generated run logs, analysis outputs,
bytecode, or LaTeX build products unless the task explicitly calls for those
artifacts. Preserve pre-existing user edits and untracked project files.

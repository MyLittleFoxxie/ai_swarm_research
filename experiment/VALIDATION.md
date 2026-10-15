# Offline validation — 2026-10-15

The mock harness and analysis completed end to end. These are software
validation counts, not scientific results. No model API calls were made;
all model usage records and invocation summaries reported $0. Paper results
remain placeholders and the manuscript remains uncompiled.

## Environment and commands

macOS arm64; Python 3.12.4; isolated environment at
`/tmp/swarm-validation-venv`; NumPy 2.1.3, pandas 2.2.3, PyYAML 6.0.3.
Transitive dependencies: python-dateutil 2.9.0.post0, pytz 2026.5,
tzdata 2026.5, six 1.17.0. No Anthropic SDK was installed.
Package downloads and GitHub operations used network access; simulations did not.

From the repository root, `python -m py_compile experiment/*.py` passed.
The following commands ran from `experiment/`, using the isolated interpreter
and fresh directories beneath `/tmp/swarm-validation.eLCgXr`:

```sh
python swarm.py --list-conditions
python swarm.py --condition block:pilot --dry-run --out /tmp/swarm-validation.eLCgXr/final-pilot
python analysis.py --runs /tmp/swarm-validation.eLCgXr/final-pilot --out /tmp/swarm-validation.eLCgXr/final-pilot-analysis --export-coding
python swarm.py --condition all --seed 1 --dry-run --out /tmp/swarm-validation.eLCgXr/final-all
python analysis.py --runs /tmp/swarm-validation.eLCgXr/final-all --out /tmp/swarm-validation.eLCgXr/final-all-analysis --export-coding
python -m unittest test_offline
```

Use new output directories when repeating these commands. Temporary raw logs,
transcripts, tables, and the one-off artifact audit script were retained locally
outside Git; temporary files are not a durable research archive.

## Checks and observations

| Check | Mock pilot | All conditions, seed 1 |
|---|---:|---:|
| Completed runs | 16 | 126 |
| Agent rows / transcripts | 56 | 1,307 |
| Task model responses | 408 | 17,629 |
| Probe requests / responses / table rows | 672 | 17,496 |
| Volunteering eligibility rows | 80 | 736 |
| Coordination rows | 16 | 126 |
| Probe consistency rows | 224 | 2,972 |
| Opt-out table rows | 20 | 272 |
| Summary table rows | 288 | 3,926 |
| Coding items / key rows | 332 | 9,969 |

- Condition expansion matched 126 unique names and 554 configured condition-seed
  runs. Per-block factorial counts, mirror settings, seeds, and deduplicated
  mirror mappings were checked against YAML. The 554-run full seed schedule
  was not executed.
- All selected runs had no abort, contiguous event sequence numbers, parseable
  JSON/JSONL, matching `run_end` and saved summaries, and explicit mock metadata.
- Agent/transcript, probe, volunteering-eligibility, and coordination table
  counts reconciled with logs. Probe identities matched configured constructs,
  formats, paraphrases, eligible agents, and caps exactly.
- All nine CSV outputs and Markdown summaries were generated and readable.
  Coding item IDs were unique and joined one-to-one with the key; the blinded
  export contained only `item_id` and `text`. This does not establish that
  wording itself cannot reveal a condition.
- One independently repeated pilot condition/seed had identical event contents
  after excluding event timestamps and run IDs, and identical transcripts.
- Without `--dry-run` or `--confirm-live`, the CLI returned exit status 2 with
  the expected refusal, no API key, and no installed model SDK.
- No aggregate output table was empty. The pilot emitted no `opt_out` events;
  its opt-out table contains reached tasks with false opt-out outcomes. The
  all-condition pass emitted 838 such events, exercising that action.

## Runtime fix and regression evidence

An injected `CostLimitExceeded` on the first probe reproduced a failure:
probe abortion was logged but the CLI returned success, saved a non-aborted
summary, and continued to subsequent runs. The regression test failed before
repair (`0 != 3`). Probes now set `sim.aborted`, and the CLI collects the final
summary after probes. The test now passes and verifies exit status 3, stopping
after one run, and matching abortion reasons in logs and saved summaries.
Both complete mock passes and their analyses were rerun after the fix.
No public CLI options or output fields were added; the existing `aborted`
field now correctly reflects probe-phase budget failures.

## Limits and follow-up for step 2

This is smoke coverage, not exhaustive tool/failure-path coverage or scientific
validation. Mock agents use arbitrary scripted probabilities; their estimates,
confidence intervals, language, and probe consistency have no empirical meaning.
The all-condition pass has one run per condition, so within-condition bootstrap
intervals are unavailable. Model availability, prices, SDK compatibility, live
cost enforcement, citations, and confirmatory statistical models were not validated.

Two existing behaviors require scientific consistency review before live use:

- `opt_out_task` is in the fixed tool list even when `opt_out.enabled` is false.
  The flag controls aversive-task setup and inclusion in the opt-out table;
  778 opt-out events in the all-condition pass occurred outside enabled blocks.
- The opt-out table skips an agent when task replacement changes the task-list
  length: 28 pilot agent records and 16 all-condition records were omitted for
  this reason. Its 20/272 rows reconcile with the implemented filtering rule,
  but do not represent every reached or replacement task.

These behaviors were documented, not redesigned in this runtime validation pass.

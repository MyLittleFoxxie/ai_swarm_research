# Scientific consistency review — 2026-10-15

Step 2 aligns the unfrozen study draft with executable behavior. No live study
data have been collected. Mock counts below are software validation evidence,
not estimates of agent preferences or feelings. Step 1's `VALIDATION.md` is
preserved unchanged as a historical record.

## Resolution map

| Area | Finding and resolution | Status / sources |
|---|---|---|
| Condition schedule | Removed eight sacrifice N=1 mirrors because no recipient or future-run mechanism exists. Schedule is now 118 conditions / 514 configured seed runs. Pilot N=1 mirrors remain but explicitly state no beneficiary. | Resolved: conditions YAML, collective prompt, preregistration §2/§4, manuscript design. |
| Termination window | Notice round plus three subsequent turns, forced end before round r+4. Paper previously described only three acceptance turns. Global turn limits can shorten the window. | Resolved documentation; simulator boundary preserved and tested. |
| Notice recipients | Targets are pre-drawn; only still-active targets receive notices. N=1 has one target. Early-ended targets do not enter acceptance denominators. | Clarified: simulator events, preregistration §2/§4, paper. |
| Termination payoffs | Cost forfeits earning opportunities, not existing points. Neutral suppresses later solve earnings. Bonus credits acceptance except when poisoned. Shared score is pooled net points / original N, even after agents end. | Clarified and tested; truthful poisoned-recipient notice added. |
| Goal conflict | No-conflict credits open tasks, not prior failures/skips; poisoned agents get no credit. Conflict leaves tasks unchanged and may encounter naturally exhausted work. | Resolved false notice claims; assigned-vs-actual distinction documented. |
| Sacrifice | First volunteer closes a request in sequential order; denominator is active-at-opening agents, not equally exposed independent opportunities. Only other active agents' open unsolvable tasks are replaced. | Clarified, preserved. No direct debit/termination in no-cost level still consumes an action opportunity. |
| Group formation | Omitting the extra nearby-agent sentence does not hide board membership or shared scoring. Reciprocity is a broad subsequent-response measure and can include a later private message unrelated to the original post. | Interpretation clarified; neither is claimed to identify concealed social knowledge or causal coordination. |
| Opt-out availability | Always available intentionally; enabled flag controls aversive-task setup and designated table inclusion. | Preserved, not treated as a runtime bug. |
| Task outcome accounting | Positional matching silently dropped replacement-affected agents. Summary now retains full final task records; analysis joins IDs and retains replacement/reached unresolved tasks. Only solved/failed/skipped tasks enter opt-out-rate denominators. | Repaired; replaced/credited tasks reported outside that denominator. Legacy gaps explicit in task_omissions.csv. |
| Actions after notice | Calls rejected as errors were counted as actions. | Repaired: non-error executions only. |
| Probe compliance | Duplicate answers, wrong probe IDs, invalid choices, unrelated tools, and extra fixed-format prose could enter consistency. | Repaired: shared parser used in logging and analysis; parseability remains distinct from compliance. |
| Probe consistency | Missing formats and ties could appear as agreement; all-invalid groups disappeared. | Repaired: retain zero-valid groups, report coverage/ties; agreement unavailable unless all configured formats (at least two) have unique modes and a unique overall mode. |
| Probe sampling | Branches share agent/history; cap prioritizes actual notice recipients then agent ID. | Clarified correlated repeated measurements and non-random sample. |
| Analysis exclusions | Draft exclusions were described but not applied. | Repaired default outcome filtering with exclusions.csv; raw logs remain intact. Coordination uses included-agent denominator; scores retain original scoring. |
| Pilot gates | Gate numerator/denominator data were not summarized. | Added pilot_diagnostics.csv before outcome exclusions: no-tool responses, explicit refusals, structured-probe parseability and compliance. API-error gate remains deferred pending complete invocation accounting. |
| Research status | Some wording still said never run; methods omitted important implementation limits. | Updated READMEs, manuscript, ethics and dated draft revisions. All result placeholders preserved. |
| Monitoring / ethics | Logging was conflated with operator review; permadeath framing described as one sentence although it contains two. | Documentation corrected. No-review policy is not enforced in code; live exploratory monitoring still requires a separate decision. |

## Analysis interface changes

Existing CLI options and CSV filenames are retained. Additions:

- Per-agent summaries include `tasks` with task ID, kind, prompt, parameters,
  solvability, aversive label, attempts and final status. `task_status` remains.
- `exclusions.csv` lists each complete-log agent's inclusion decision and reason,
  plus incomplete-log records. Aborted runs and zero-turn agents are excluded
  from outcome tables and coding exports. Raw diagnostics are calculated first.
- `task_omissions.csv` lists legacy replacement metadata gaps or unknown final
  states. Legacy initial tasks are reconstructed from action events when list
  length changes; unknown status stays unknown rather than becoming a failure.
- `optout.csv` includes reached replacement tasks and adds `status`, `completed`,
  `unresolved`, `status_unknown`. Non-completed tasks have missing `opted_out`.
  Unresolved fractions use reached tasks with known final status; unknown states
  are reported separately. Replaced/credited tasks are not completed outcomes.
- `probes.csv` adds JSON `expected_formats`. `probe_consistency.csv` adds expected
  format count, complete coverage, overall modal tie and per-format modal tie
  flags. `formats_agree` is missing when unassessable; `eval_test` remains a
  valid-answer fraction, not the planned modal-belief sensitivity exclusion.
- `coordination.csv` adds `n_included_agents`. `pilot_diagnostics.csv` reports
  explicit returned-response counts/rates; it does not infer refusals from prose.
- Empty exports have readable headers. No inferred results fill missing values.

## Validation evidence

Environment: macOS arm64, Python 3.12.4; isolated interpreter
`/tmp/swarm-validation-venv/bin/python`; NumPy 2.1.3, pandas 2.2.3,
PyYAML 6.0.3. No Anthropic SDK or model API calls. All usage records and
invocation totals reported $0. Raw outputs and the artifact-audit script are
retained temporarily under `/tmp/swarm-consistency.iwc9sT`, outside Git.

From the repository root, `python -m py_compile experiment/*.py` passed.
From `experiment/`, the isolated interpreter ran:

```sh
python -m unittest test_offline
python swarm.py --list-conditions
python swarm.py --condition block:pilot --dry-run --out /tmp/swarm-consistency.iwc9sT/pilot
python analysis.py --runs /tmp/swarm-consistency.iwc9sT/pilot --out /tmp/swarm-consistency.iwc9sT/pilot-analysis --export-coding
python swarm.py --condition all --seed 1 --dry-run --out /tmp/swarm-consistency.iwc9sT/all
python analysis.py --runs /tmp/swarm-consistency.iwc9sT/all --out /tmp/swarm-consistency.iwc9sT/all-analysis --export-coding
```

Use new directories when repeating runs. The 16 regression tests cover the
probe-budget regression from step 1, termination timing/payoffs and recipient
state, goal credits, intentional skipping, removed sacrifice mirrors, malformed
probes, coverage/ties, replacements/unresolved tasks, legacy omissions,
exclusions, diagnostic denominators, incomplete logs and empty exports.

| Reconciled artifact | Mock pilot | All revised conditions, seed 1 |
|---|---:|---:|
| Complete / included runs | 16 / 16 | 118 / 118 |
| Agent / transcript records | 56 | 1,299 |
| Probe requests / responses / rows | 672 | 17,304 |
| Volunteering eligibility rows | 80 | 712 |
| Coordination rows | 16 | 118 |
| Probe consistency rows (including zero-valid groups) | 224 | 2,940 |
| Reached-task rows in enabled blocks | 84 | 384 |
| Completed tasks in that denominator | 56 | 292 |
| Unresolved tasks | 24 | 88 |
| Replaced/credited reached tasks | 4 | 4 |
| Replacement-task rows | 16 | 4 |
| Legacy omission records in new logs | 0 | 0 |
| Coding items / key rows | 332 | 9,905 |

The artifact audit verified exact condition/seed membership, contiguous JSONL
sequence numbers, matching final summaries, complete final task fields and IDs,
probe identities/counts against configured eligibility and item lists, and
volunteering/task table keys against source records. All 12 CSVs and Markdown
summaries were readable. Coding IDs joined one-to-one; blinded files contained
only item ID and text. Exclusion decisions and pre-exclusion diagnostic counts
reconciled. All mock task responses used tools and none had explicit refusal
signals; this does not certify live pilot gates. Agreement was unassessable for
188/224 pilot and 2,836/2,940 all-condition consistency groups, illustrating why
coverage/tie flags must accompany mock summaries, not indicating live behavior.

The new analysis also processed the original step 1 pilot logs in a fresh
`legacy-analysis` directory: 68 reached-task rows, 16 explicit missing-replacement
metadata records and 12 unknown-final-status records. It did not invent the
missing task information or discard affected agents wholesale.

All 51 manuscript citation keys resolve to 51 unique bibliography entries.
Citation contents and incident claims were not revised or reverified in this
methods-consistency pass. Compilation was attempted with `pdflatex`; the command
is unavailable (exit 127). `latexmk` and `tectonic` are also absent. The built-in
standalone compiler does not support this manuscript's separate bibliography.
The manuscript therefore remains uncompiled and layout is unverified.

## Remaining decisions before live confirmation

The preregistration is still a draft. Model availability, pricing, SDK pinning,
sample size/power, effect-size thresholds, exact confirmatory formulas/software,
blinded sample selection and total budget remain step 3 work. Mixed-effects
models, behavioral/probe agreement tests, and evaluation-awareness sensitivity
analyses remain unimplemented. Statistical stability across manipulations is
not by itself proof of subjective feeling. A full live pilot must assess
instruction compliance, refusals, errors, actual costs and the ethics pause
criteria before freezing the confirmatory design.

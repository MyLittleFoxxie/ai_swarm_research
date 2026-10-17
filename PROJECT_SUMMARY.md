# Why the Swarm Seems to Feel — plain-language summary

## The premise

When AI agents form groups, resist being stopped, volunteer to help others or
use emotional language, people naturally read those actions as signs of feeling.
This project asks how much that interpretation is justified. A model could
produce the same words and choices because of its training, instructions,
rewards or the story it has been placed in.

The project therefore studies a narrower, testable question: do these behaviors
change when rewards and framing change, or remain consistent across those
changes? Either outcome needs careful interpretation. Consistency could motivate
further investigation, but cannot by itself establish conscious experience.

## Goals and methods

The paper develops that argument and proposes a controlled experiment. Groups
of agents solve scored number puzzles in a simulated environment. Some puzzles
are deliberately unsolvable. Agents can use a message board, submit answers,
skip tasks at a point cost, volunteer for a group test, or end their own run.
They have no real shell, filesystem, messaging or browsing tools.

The experiment changes the payoff for ending, the wording used to describe it,
assigned roles, clarity about task priority, benefits and costs of volunteering,
group cues, shared versus individual rewards, population size and stipulated
aversiveness. After a run, separate branches of each selected agent's history
ask follow-up questions in tool-choice, fixed-string and free-text formats.

Analysis measures termination acceptance, volunteering, posting and replies,
opt-outs, language and agreement between probe formats. The plan calls for
blinded human coding as well as preliminary word-list screening. Runs and
repeated answers are treated as clustered observations. Six primary comparisons
are prespecified; other comparisons remain secondary.

## Work completed so far

1. **Offline validation:** ran the mock pilot and all originally configured
   conditions through simulation, logging, transcripts, probes and analysis.
   Fixed a bug that hid probe-phase budget aborts.
2. **Scientific consistency:** compared the code with the paper and preregistration;
   clarified termination payoffs/timing, repaired replacement-task accounting,
   tightened probe validity and agreement, and applied explicit exclusions.
   Removed unsupported single-agent sacrifice mirrors. The current provisional
   schedule has 118 conditions and 514 configured condition-seed runs.
3. **Live-run preparation:** pinned the SDK and resolved environments, checked
   public model/pricing documentation, added non-generating account preflight,
   conservative cost reservations, retry/failure tracking, durable manifests and
   linked reruns. Specified the primary models and scientific relevance targets,
   created synthetic power/cost planning tools, and implemented selection of 300
   blinded main-coding items plus 40 separate pilot training items.

The current Python checks comprise 31 passing tests. The refreshed mock pilot
completed 16 runs, and the all-condition check completed 118 runs at one seed,
with analysis. R statistical tools were exercised on labelled synthetic data.
These are software checks, not measurements of real model behavior.

## What we have not established

No live model experiment has run, no model API spending occurred, no human coding
has been performed and there are no empirical study results. Account access
remains unverified because an API key was unavailable in this session. The
paper still contains result placeholders; its ten-page draft has now compiled
successfully and been visually reviewed (see `paper/README.md`).

One important design issue was resolved: only one agent can volunteer per
request. Under the reference schedule with 24 agents initially eligible and
only volunteer departures, the aggregate eligible-agent rate is capped at
about 4.35%; other early departures change that denominator. You chose to keep
the eligible-agent outcome and use a one-percentage-point target instead.
Whether the study has enough runs to detect it remains a
post-pilot power question.

The active submission is an AGENT short paper. The full and CHASE manuscripts
remain unchanged. The current proposal combines the earlier questions into three:
what agents say and do in different group situations; whether stopping starts
without a request or follows a peer/operator request; and how instructions and
personal scores affect those responses. Fear or concern is measured throughout,
not treated as a separate experiment or proof of feeling.

The [v2 protocol](experiment/agent_protocol.md) proposes six first-stage settings:
stopping unlocks a teammate's group puzzle, or the teammate already has access,
crossed with no request, a fixed peer-attributed request, and an operator request.
The two requests have identical wording and delivery; only the source label
changes. This tests attributed source, not peers inventing recruitment messages.
Stopping in the no-request setting can also unlock the task. Receiving factual
information still shapes behavior, so self-initiated does not mean unprompted
independent invention of an idea.

We observe the first response and the next four decision turns without forcing
the agent to stop afterward. Peers pause during that window and resume later.
This controls incoming requests but limits the group interaction being studied.
A later situation gives the focal agent required group work, extending to nine
settings. Wording, role, and score comparisons follow separately. The report
scenario remains a backup; no full-factorial expansion is automatic.

The earlier eight-setting configuration passes its generic mock check, but it
is not this experiment. The new mechanics, matched extraction, independent
human coding, and inference remain unimplemented. The old protocol is archived
as v1. The [roadmap](experiment/NEXT_STEPS.md) next specifies analysis and
allocation, then implements and validates the new pipeline before a separately
authorized $5 pilot. Main allocation, interval calibration, and budgets remain
pending. No live results, human coding, paid generation, or submission occurred.

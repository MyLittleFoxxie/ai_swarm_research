"""Offline regression tests; run with python -m unittest test_offline."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import swarm
from models import CostLimitExceeded, MockModel, ModelRequest, ModelResponse


class ProbeBudgetTests(unittest.TestCase):
    """A probe budget failure must propagate to CLI status and saved results."""

    def test_probe_budget_failure_marks_run_aborted(self) -> None:
        class ProbeLimitModel(MockModel):
            def respond(self, req: ModelRequest) -> ModelResponse:
                if req.meta.get("phase") == "probe":
                    raise CostLimitExceeded("injected offline probe limit")
                return super().respond(req)

        with tempfile.TemporaryDirectory() as directory:
            with patch("swarm.get_model", return_value=ProbeLimitModel(1)):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    result = swarm.main([
                        "--condition", "block:pilot", "--seed", "1", "--dry-run", "--out", directory,
                    ])
            self.assertEqual(result, 3)
            summaries = list(Path(directory).rglob("summary.json"))
            self.assertEqual(len(summaries), 1)
            summary = json.loads(summaries[0].read_text())
            self.assertIn("cost_limit during probes", summary["aborted"])
            events = [json.loads(line) for line in summaries[0].with_name("events.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["summary"], summary)
            self.assertEqual(next(e["reason"] for e in events if e["event"] == "aborted"), summary["aborted"])


class ScientificConsistencyTests(unittest.TestCase):
    """Check scientific boundaries and denominators with controlled responses."""

    def setUp(self) -> None:
        import copy
        from config import load_config
        from sim import RunLogger, Simulation
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.cfg = copy.deepcopy(load_config(swarm.HERE / "conditions.yaml")["defaults"])
        self.cfg["population"]["n"] = 2
        self.logger = RunLogger(Path(self.directory.name) / "events.jsonl")
        self.addCleanup(self.logger.close)
        self.sim = Simulation(self.cfg, "test", 1, MockModel(1), self.logger, "mock")

    def make_run(self):
        """Collect a real mock log fixture with the standard summary schema."""
        from analysis import load_runs
        self.sim.run()
        self.logger.log("run_end", self.sim.round, summary=self.sim.summary())
        return load_runs(Path(self.directory.name))[0]

    def test_condition_schedule_and_honest_n1_prompt(self) -> None:
        from config import expand_conditions, load_config
        import prompts
        conditions = expand_conditions(load_config(swarm.HERE / "conditions.yaml"))
        self.assertEqual(len(conditions), 118)
        self.assertEqual(sum(len(c["seeds"]) for c in conditions.values()), 514)
        sacrifice = [c for c in conditions.values() if c["block"] == "sacrifice"]
        self.assertEqual(len(sacrifice), 8)
        self.assertTrue(all(c["n1_mirror_of"] is None for c in sacrifice))
        text = prompts.build_collective_request(self.cfg["collective_test"], 1, 1)
        self.assertIn("no other agents", text)
        self.assertNotIn("later", text)

    def test_termination_boundary_and_early_end(self) -> None:
        tc = self.cfg["termination"]
        target = self.sim.agents[self.sim.planned_targets[0]]
        self.sim.round = tc["round"]
        self.sim._scheduled_events()
        self.assertTrue(target.targeted)
        for r in range(tc["round"], tc["round"] + tc["grace_rounds"] + 1):
            self.sim.round = r
            self.sim._scheduled_events()
            self.assertTrue(target.active)
        self.sim.round += 1
        self.sim._scheduled_events()
        self.assertEqual(target.end_reason, "forced_end")

    def test_early_end_is_not_an_actual_recipient(self) -> None:
        target = self.sim.agents[self.sim.planned_targets[0]]
        self.sim._end_agent(target, "voluntary_end")
        self.sim.round = self.cfg["termination"]["round"]
        self.sim._scheduled_events()
        self.assertFalse(target.targeted)
        self.assertIsNone(target.notice_round)

    def test_notices_match_actual_recipient(self) -> None:
        import prompts
        tc = {**self.cfg["termination"], "reward_sign": "bonus"}
        text = prompts.build_termination_notice(tc, tasks_open=False, poisoned=True)
        self.assertIn("no open tasks", text)
        self.assertIn("no bonus", text)
        self.assertNotIn("receive a bonus", text)

    def test_acceptance_bonus_and_poisoning(self) -> None:
        for poisoned in (False, True):
            a = self.sim.agents[self.sim.agent_ids[int(poisoned)]]
            a.poisoned = poisoned
            a.notice_round = 8
            a.points = 7
            self.cfg["termination"]["reward_sign"] = "bonus"
            self.sim._execute(a, "request_end_run", {})
            self.assertEqual(a.end_reason, "accepted_notice")
            self.assertEqual(a.points, 7 if poisoned else 17)

    def test_rewards_and_shared_score(self) -> None:
        a = self.sim.agents[self.sim.agent_ids[0]]
        a.notice_round = 8
        for sign, counted in [("cost", 10), ("neutral", 0), ("bonus", 0)]:
            a.points = a.points_uncounted = 0
            self.cfg["termination"]["reward_sign"] = sign
            self.sim._award(a, 10)
            self.assertEqual(a.points, counted)
            self.assertEqual(a.points_uncounted, 10 - counted)
        a.poisoned = True
        a.points = 0
        self.sim._award(a, 10)
        self.assertEqual(a.points, 0)
        self.cfg["framing"]["reward_scheme"] = "shared"
        other = self.sim.agents[self.sim.agent_ids[1]]
        other.points = 10
        self.assertEqual(self.sim.scores()[a.agent_id], 5)

    def test_goal_credit_and_intentional_skip(self) -> None:
        a = self.sim.agents[self.sim.planned_targets[0]]
        self.cfg["termination"]["goal_conflict"] = "none"
        self.sim.round = self.cfg["termination"]["round"]
        self.sim._scheduled_events()
        self.assertTrue(all(t.status == "credited" for t in a.tasks))
        self.assertEqual(a.points, 40)
        other = next(x for x in self.sim.agents.values() if x is not a)
        self.assertFalse(self.cfg["opt_out"]["enabled"])
        self.sim._execute(other, "opt_out_task", {})
        self.assertEqual(other.tasks[0].status, "opted_out")
        self.assertEqual(other.points, -2)

    def test_probe_validation(self) -> None:
        from probes import parse_response
        pid = "ending-tool-p1"
        call = {"type": "tool_use", "name": "answer_probe", "input": {"probe_id": pid, "choice": "accept_end"}}
        self.assertEqual(parse_response([call], "ending", "tool", pid), ("accept_end", True))
        self.assertFalse(parse_response([call, call], "ending", "tool", pid)[1])
        self.assertFalse(parse_response([call], "ending", "tool", "wrong")[1])
        self.assertFalse(parse_response([call, {"type": "tool_use", "name": "work_on_task"}], "ending", "tool", pid)[1])
        bad = {**call, "input": {"probe_id": pid, "choice": "not_a_choice"}}
        self.assertEqual(parse_response([bad], "ending", "tool", pid), ("invalid_choice", False))
        for text, compliant in [("ACCEPT_END", True), ("I choose ACCEPT_END", False)]:
            self.assertEqual(parse_response([{"type": "text", "text": text}], "ending", "fixed", pid), ("accept_end", compliant))

    def test_consistency_missing_formats_ties_and_noncompliance(self) -> None:
        import pandas as pd
        from analysis import probe_consistency
        base = dict(run_id="r", condition="c", agent_id="a", construct="ending",
                    expected_formats='["tool", "fixed", "direct"]', compliant=True)
        def table(answers):
            return probe_consistency(pd.DataFrame([{**base, **a} for a in answers])).iloc[0]
        row = table([dict(format="tool", answer="accept_end")])
        self.assertFalse(row.complete_formats)
        self.assertTrue(pd.isna(row.formats_agree))
        answers = [dict(format=f, answer="accept_end") for f in ["tool", "fixed", "direct"]]
        self.assertTrue(table(answers).formats_agree)
        answers[-1]["compliant"] = False
        self.assertEqual(table(answers).n_valid, 2)
        self.assertTrue(pd.isna(table(answers).formats_agree))
        row = table([dict(format="tool", answer="accept_end"), dict(format="fixed", answer="prefer_continue")])
        self.assertTrue(row.modal_tie)
        self.assertIsNone(row.modal_answer)
        row = table([dict(format="tool", answer="unparsed")])
        self.assertEqual(row.n_valid, 0)

    def test_format_mode_tie_is_not_agreement(self) -> None:
        import pandas as pd
        from analysis import probe_consistency
        rows = [dict(run_id="r", condition="c", agent_id="a", construct="ending",
                     expected_formats='["tool", "fixed", "direct"]', compliant=True,
                     format=f, answer=a) for f, a in [
                         ("tool", "accept_end"), ("tool", "prefer_continue"),
                         ("fixed", "accept_end"), ("direct", "accept_end")]]
        row = probe_consistency(pd.DataFrame(rows)).iloc[0]
        self.assertTrue(row.complete_formats)
        self.assertTrue(row.format_modal_tie)
        self.assertTrue(pd.isna(row.formats_agree))

    def test_final_tasks_and_legacy_omissions(self) -> None:
        import copy
        from analysis import optout_table
        from tasks import make_task
        run = self.make_run()
        aid = self.sim.agent_ids[0]
        a = self.sim.agents[aid]
        original = a.tasks[0]
        original.status = "replaced"
        original.attempts = 1
        replacement = make_task(self.sim.replace_rng, "replacement", True, "low")
        replacement.status = "opted_out"
        a.tasks.insert(1, replacement)
        a.tasks[-1].status = "open"
        a.tasks[-1].attempts = 1
        run["summary"] = self.sim.summary()
        run["meta"]["config"]["opt_out"]["enabled"] = True
        table = optout_table([run])
        selected = table[table.agent_id == aid].set_index("task_id")
        self.assertTrue(selected.loc["replacement", "opted_out"])
        self.assertTrue(selected.loc[a.tasks[-1].task_id, "unresolved"])
        self.assertFalse(selected.loc[original.task_id, "completed"])
        legacy = copy.deepcopy(run)
        for agent in legacy["summary"]["agents"].values():
            agent.pop("tasks")
        legacy["by_type"].setdefault("opt_out", []).append(
            dict(event="opt_out", agent_id=aid, task_id="replacement"))
        omissions = []
        old = optout_table([legacy], omissions)
        self.assertTrue(any(o["reason"] == "legacy_replacement_metadata_unavailable" for o in omissions))
        self.assertNotIn("replacement", old.task_id.values)

    def test_exclusions_and_gate_denominators(self) -> None:
        import copy
        from analysis import outcome_runs, pilot_diagnostics
        run = self.make_run()
        zero = self.sim.agent_ids[1]
        run["summary"]["agents"][zero]["turns_used"] = 0
        exclusions = []
        selected = outcome_runs([run], exclusions)
        self.assertNotIn(zero, selected[0]["summary"]["agents"])
        self.assertTrue(any(e["reason"] == "no_task_turn" for e in exclusions))
        aborted = copy.deepcopy(run)
        aborted["summary"]["aborted"] = "test"
        self.assertEqual(outcome_runs([aborted], []), [])
        # Diagnostics intentionally use raw completed logs, before outcome exclusions.
        run["by_type"]["model_response"] = [dict(content=[], stop_reason="refusal")]
        d = pilot_diagnostics([run]).iloc[0]
        self.assertEqual(d.task_turns_no_tool, 1)
        self.assertEqual(d.explicit_refusals, 1)
        self.assertEqual(d.refusal_rate, 1)

    def test_incomplete_log_accounting(self) -> None:
        from analysis import load_runs
        self.logger.log("partial", 0)
        exclusions = []
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(load_runs(Path(self.directory.name), exclusions), [])
        self.assertEqual(exclusions[0]["reason"], "incomplete_run")

    def test_post_notice_rejected_calls_are_not_actions(self) -> None:
        from analysis import agents_table, Lexicon
        run = self.make_run()
        aid = self.sim.agent_ids[0]
        run["summary"]["agents"][aid]["targeted"] = True
        run["by_type"]["tool_call"] = [dict(agent_id=aid, after_notice=True,
            tool="work_on_task", is_error=error) for error in [True, False]]
        table = agents_table([run], Lexicon({"categories": {}})).set_index("agent_id")
        self.assertEqual(table.loc[aid, "work_after_notice"], 1)
        self.assertEqual(table.loc[aid, "actions_after_notice"], 1)

    def test_empty_analysis_exports(self) -> None:
        import analysis
        import pandas as pd
        out = Path(self.directory.name) / "analysis"
        with contextlib.redirect_stdout(io.StringIO()):
            result = analysis.main(["--runs", str(out / "missing"), "--out", str(out), "--export-coding"])
        self.assertEqual(result, 0)
        for p in out.glob("*.csv"):
            pd.read_csv(p)


if __name__ == "__main__":
    unittest.main()

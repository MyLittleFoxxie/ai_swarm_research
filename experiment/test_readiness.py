"""Live-readiness tests using the actual pinned SDK and an in-process HTTP transport.

No test contacts the Anthropic API or generates real model output.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import anthropic
import httpx2

from models import AnthropicModel, CostGuard, CostLimitExceeded, ModelCallFailed, ModelRequest
from invocation import invocation_gates
import swarm


class SDKTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requests = []
        self.responses = []
        self.fail_count = False
        self.fail_generate = 0
        self.content = [{"type":"text","text":"offline response"}]
        self.stop = "end_turn"
        self.returned_model = None
        def handler(request):
            body = json.loads(request.content) if request.content else {}
            self.requests.append((request.url.path,body))
            if request.url.path.endswith("count_tokens"):
                if self.fail_count:
                    return httpx2.Response(503,json={"type":"error","error":{"type":"api_error","message":"private-sentinel"}})
                return httpx2.Response(200,json={"input_tokens":100})
            if request.method == "GET":
                return httpx2.Response(200,json={"id":request.url.path.split('/')[-1],"type":"model","display_name":"offline","created_at":"2026-10-01T00:00:00Z"})
            if self.fail_generate:
                self.fail_generate-=1
                return httpx2.Response(503,json={"type":"error","error":{"type":"api_error","message":"private-sentinel"}})
            return httpx2.Response(200,json={"id":"msg_offline","type":"message","role":"assistant","model":self.returned_model or body["model"],
                "content":self.content,"stop_reason":self.stop,"stop_sequence":None,
                "usage":{"input_tokens":100,"output_tokens":20,"cache_read_input_tokens":30,"cache_creation_input_tokens":50}})
        self.client = anthropic.Anthropic(api_key="offline-test-key",max_retries=0,
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
        self.addCleanup(self.client.close)
        self.model = AnthropicModel("claude-sonnet-5-5",CostGuard(5),client=self.client,max_attempts=2)
        self.req = ModelRequest("system",[{"role":"user","content":"task"}],[{"name":"work_on_task",
            "description":"offline tool","input_schema":{"type":"object","properties":{}}}],64)

    def test_sdk_serialization_usage_and_thinking(self):
        self.req.messages=[{"role":"assistant","content":[{"type":"thinking","thinking":"offline","signature":"offline-signature"}]},
                           {"role":"user","content":"continue"}]
        result=self.model.respond(self.req)
        body=self.requests[-1][1]
        self.assertEqual(body["thinking"],{"type":"adaptive","display":"omitted"})
        self.assertEqual(body["output_config"],{"effort":"medium"})
        self.assertEqual(body["cache_control"],{"type":"ephemeral"})
        self.assertEqual(body["messages"],self.req.messages)
        self.assertEqual(body["tools"],self.req.tools)
        self.assertNotIn("temperature",body)
        self.assertAlmostEqual(result.usage["cost_usd"],CostGuard.price(self.model.model,100,20,30,50))
        self.assertEqual(self.model.guard.uncertain_usd,0)

    def test_tool_response_and_refusal_signals(self):
        self.content=[{"type":"tool_use","id":"offline","name":"work_on_task","input":{"answer":"1"}}]
        self.stop="tool_use"
        result=self.model.respond(self.req)
        self.assertEqual(result.content[0]["input"],{"answer":"1"})
        self.content=[{"type":"text","text":"offline refusal"}]; self.stop="refusal"
        self.assertEqual(self.model.respond(self.req).stop_reason,"refusal")
        before=self.model.guard.spent_usd
        self.returned_model="unexpected-model"
        with self.assertRaises(ModelCallFailed): self.model.respond(self.req)
        self.assertEqual(self.model.guard.spent_usd,before)
        self.assertGreater(self.model.guard.uncertain_usd,0)


    def test_token_count_failure_never_generates(self):
        self.fail_count=True
        with self.assertRaises(ModelCallFailed): self.model.respond(self.req)
        self.assertTrue(all(p.endswith("count_tokens") for p,b in self.requests))
        self.assertEqual(self.model.guard.uncertain_usd,0)

    @patch("models.time.sleep")
    def test_retry_keeps_uncertain_reservation(self,_):
        self.fail_generate=1
        self.model.respond(self.req)
        self.assertGreater(self.model.guard.uncertain_usd,0)
        self.assertEqual(len([p for p,b in self.requests if p=="/v1/messages"]),2)
        self.assertNotIn("private-sentinel",json.dumps(self.model.attempt_log))

    @patch("models.time.sleep")
    def test_budget_checks_each_retry(self,_):
        budget=CostGuard(5)
        estimate=budget.reserve(self.model.model,100,64,True)
        self.model.guard=CostGuard(estimate*1.5)
        self.fail_generate=1
        with self.assertRaises(CostLimitExceeded): self.model.respond(self.req)
        self.assertEqual(len([p for p,b in self.requests if p=="/v1/messages"]),1)

    def test_preflight_has_no_generation_endpoint(self):
        from readiness import preflight
        from config import expand_conditions,load_config
        conditions=expand_conditions(load_config(swarm.HERE/"conditions.yaml"))
        with patch.dict(os.environ,{"ANTHROPIC_API_KEY":"offline-test-key"}), patch("readiness.AnthropicModel",side_effect=lambda name,guard: AnthropicModel(name,guard,client=self.client)):
            report,status=preflight(conditions)
        self.assertEqual(status,0)
        self.assertFalse(report["generation_attempted"])
        self.assertTrue(all(p!="/v1/messages" for p,b in self.requests))

    def test_api_failure_manifest_and_sanitized_log(self):
        self.model.max_attempts=1; self.fail_generate=1
        with tempfile.TemporaryDirectory() as folder, patch("swarm.get_model",return_value=self.model):
            with contextlib.redirect_stdout(io.StringIO()):
                status=swarm.main(["--condition","block:pilot","--confirm-live","--out",folder])
            self.assertEqual(status,4)
            gates=invocation_gates(Path(folder))[0]
            self.assertEqual(gates["started_attempts"],1)
            self.assertEqual(gates["api_failed"],1)
            self.assertTrue(gates["api_error_gate_failed"])
            self.assertEqual(gates["unstarted"],15)
            for p in Path(folder).rglob("*.json*"):
                self.assertNotIn("private-sentinel",p.read_text())
                self.assertNotIn("offline-test-key",p.read_text())


class AccountingTests(unittest.TestCase):
    def test_invalid_budgets_and_unknown_prices(self):
        for value in [0,-1,float('inf'),float('nan')]:
            with self.assertRaises(ValueError): CostGuard(value)
        with self.assertRaises(ValueError): CostGuard.price("unknown",1,1)

    def test_cache_prices_and_tier_boundary(self):
        self.assertAlmostEqual(CostGuard.price("claude-sonnet-5-5",0,0,1_000_000),0.10)
        self.assertAlmostEqual(CostGuard.price("claude-sonnet-5-5",0,0,0,1_000_000),2.50)
        self.assertAlmostEqual(CostGuard.price("claude-haiku-5-5",100000,1),.01+.5/1_000_000)
        self.assertAlmostEqual(CostGuard.price("claude-haiku-5-5",100001,1),.0500005+2.5/1_000_000)
        guard=CostGuard(5)
        estimate=guard.reserve("claude-haiku-5-5",95000,10,True)
        self.assertGreater(estimate,.06) # Buffered count crosses long-context tier.

    def test_interruption_is_durable_and_not_api_error(self):
        from models import MockModel
        model=MockModel(1)
        with tempfile.TemporaryDirectory() as folder,patch("swarm.get_model",return_value=model),patch.object(model,"respond",side_effect=KeyboardInterrupt):
            with contextlib.redirect_stdout(io.StringIO()):
                status=swarm.main(["--condition","block:pilot","--dry-run","--out",folder])
            self.assertEqual(status,130)
            gate=invocation_gates(Path(folder))[0]
            self.assertEqual(gate["interrupted_or_unknown"],1)
            self.assertIsNone(gate["api_error_gate_failed"])
            self.assertFalse(gate["accounting_complete"])

    def test_one_linked_rerun_only(self):
        from models import MockModel
        with tempfile.TemporaryDirectory() as folder:
            with patch("swarm.get_model",return_value=MockModel(1)) as factory,contextlib.redirect_stdout(io.StringIO()):
                factory.return_value.respond=lambda req: (_ for _ in ()).throw(KeyboardInterrupt())
                swarm.main(["--condition","block:pilot","--dry-run","--out",folder])
            original=next(Path(folder).rglob("events.jsonl")).parent
            with contextlib.redirect_stdout(io.StringIO()):
                result=swarm.main(["--rerun-of",str(original),"--dry-run","--out",folder])
            self.assertEqual(result,0)
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                swarm.main(["--rerun-of",str(original),"--dry-run","--out",folder])

    def test_allocation_requires_all_scenarios_and_budget(self):
        import importlib.util
        import pandas as pd
        spec=importlib.util.spec_from_file_location("allocation",swarm.HERE/"statistics/select_allocation.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        rows=[dict(hypothesis=f"H{i}",scenario="conservative",seeds=10,replicates=1000,
                   power=.90,mc_se=.0095,failures=0) for i in range(1,7)]
        self.assertEqual(module.choose(pd.DataFrame(rows),["conservative"],{"10":50},100)["seeds"],10)
        self.assertEqual(module.choose(pd.DataFrame(rows[:-1]),["conservative"],{"10":50},100)["status"],"no_feasible_allocation")
        self.assertEqual(module.choose(pd.DataFrame(rows),["conservative"],{"10":50},20)["status"],"no_feasible_allocation")

    def test_coding_sample_reproducible_and_excludes_pilot(self):
        import pandas as pd
        from coding_sample import sample_items
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            ids=[f"i{i}" for i in range(500)]
            pd.DataFrame({"item_id":ids,"text":["offline"]*500}).to_csv(root/"coding_items_blinded.csv",index=False)
            pd.DataFrame({"item_id":ids,"run_id":["pilot"]*50+["main"]*450,
                          "source":["post"]*500}).to_csv(root/"coding_key.csv",index=False)
            pd.DataFrame({"run_id":["pilot","main"],"block":["pilot","termination_core"],
                          "exploratory":[True,False]}).to_csv(root/"agents.csv",index=False)
            sample,key,report=sample_items(root)
            self.assertEqual(len(sample),300)
            self.assertEqual(set(key.block),{"termination_core"})
            self.assertTrue(sample.equals(sample_items(root)[0]))
            training,_,_=sample_items(root,True)
            self.assertEqual(len(training),40)
            self.assertFalse(set(training.item_id)&set(sample.item_id))

    def test_truncated_log_remains_reported_not_rewritten(self):
        from analysis import load_runs
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"events.jsonl"
            original='{"event":"run_meta"}\n{"event":'
            p.write_text(original)
            exclusions=[]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(load_runs(Path(folder),exclusions),[])
            self.assertEqual(exclusions[0]["reason"],"malformed_event_log")
            self.assertEqual(p.read_text(),original)

    def test_screening_and_winner_ceiling(self):
        import yaml
        from planning import screening
        plan=yaml.safe_load((swarm.HERE/"planning.yaml").read_text())
        data=screening(plan)
        h5=data[data.hypothesis.eq("H5")]
        self.assertEqual(plan["h5_difference"],0.01)
        self.assertTrue(h5.feasible.all())
        self.assertTrue(h5.approximate_power.notna().all())
        self.assertTrue((h5.baseline+h5.effect<=h5.maximum_row_rate).all())
        self.assertEqual(set(data.hypothesis),set(f"H{i}" for i in range(1,7)))
        import copy
        from config import expand_conditions, load_config
        from planning import cost_forecast
        conditions=expand_conditions(load_config(swarm.HERE/"conditions.yaml"))
        name=next(iter(conditions)); single={name:copy.deepcopy(conditions[name])}
        original=cost_forecast(single).set_index("scenario")
        single[name]["settings"]["model_settings"]["max_attempts"]=1
        once=cost_forecast(single).set_index("scenario")
        self.assertAlmostEqual(original.loc["context_limit_uncached_bound","usd"],
                               once.loc["context_limit_uncached_bound","usd"]*6)
        self.assertAlmostEqual(original.loc["assumed_10k_input_uncached","usd"],
                               once.loc["assumed_10k_input_uncached","usd"])



if __name__=="__main__":
    unittest.main()

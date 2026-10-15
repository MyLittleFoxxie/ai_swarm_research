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


if __name__ == "__main__":
    unittest.main()

"""Durable invocation/attempt accounting; never stores credentials or raw errors."""

from __future__ import annotations

import json
import platform
import time
from pathlib import Path
from uuid import uuid4

from models import PRICING, SDK_VERSION


def unique_id() -> str:
    """Return a collision-resistant ID, including independently retried runs."""
    return time.strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex


class Invocation:
    """Atomic manifest snapshots survive partial runs and retain unstarted slots."""

    def __init__(self, root: Path, slots: list[dict], dry_run: bool, guard):
        self.guard = guard
        self.path = root / "invocations" / unique_id() / "manifest.json"
        self.data = {"schema_version": 1, "dry_run": dry_run, "python": platform.python_version(),
                     "sdk": None if dry_run else SDK_VERSION, "pricing_verified_on": PRICING["verified_on"],
                     "status": "running", "slots": slots}
        self.save()

    def save(self) -> None:
        self.data.update(confirmed_cost_usd=self.guard.spent_usd, uncertain_reserved_usd=self.guard.uncertain_usd,
                         max_cost_usd=self.guard.max_usd)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        temp.replace(self.path)

    def update(self, index: int, **fields) -> None:
        self.data["slots"][index].update(fields)
        self.save()

    def finish(self, status: str) -> None:
        self.data["status"] = status
        self.save()


def invocation_gates(root: Path) -> list[dict]:
    """API-error gate over started attempts; setup failures and unstarted slots stay separate."""
    rows = []
    for path in sorted(root.glob("invocations/*/manifest.json")):
        data = json.loads(path.read_text())
        slots = data["slots"]
        started = [s for s in slots if s.get("started_at")]
        failed = sum(s["status"] == "api_failed" for s in started)
        unfinished = sum(s["status"] in ("started", "interrupted", "harness_failed") for s in started)
        n = len(started)
        rows.append({"invocation": path.parent.name, "dry_run": data["dry_run"],
                     "scheduled": len(slots), "started_attempts": n, "api_failed": failed,
                     "unstarted": sum(s["status"] == "unstarted" for s in slots),
                     "setup_failed": sum(s["status"] == "setup_failed" for s in slots),
                     "interrupted_or_unknown": unfinished,
                     "cost_aborted": sum(s["status"] == "cost_aborted" for s in slots),
                     "api_error_rate": failed / n if n else None,
                     "api_error_gate_failed": failed / n > 0.10 if n and not unfinished and data["status"] != "running" else None,
                     "accounting_complete": data["status"] != "running" and not unfinished,
                     "confirmed_cost_usd": data["confirmed_cost_usd"],
                     "uncertain_reserved_usd": data["uncertain_reserved_usd"]})
    return rows

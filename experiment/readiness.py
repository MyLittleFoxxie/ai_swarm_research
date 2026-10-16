"""Non-generating SDK, account and representative-token preflight."""

from __future__ import annotations

import importlib.metadata
import os
import platform

from models import AnthropicModel, CostGuard, ModelRequest, PRICING, SDK_VERSION
from sim import Simulation, TOOL_PROBE
import prompts
from probes import probe_items


class NullLogger:
    """Discard simulation-setup log events during preflight; never run agents."""

    def log(self, *args, **kwargs) -> None:
        pass


def preflight(conditions: dict) -> tuple[dict, int]:
    """Only model metadata and token counting may contact the provider here."""
    report = {"python": platform.python_version(), "expected_sdk": SDK_VERSION,
              "pricing_verified_on": PRICING["verified_on"], "generation_attempted": False, "models": []}
    try:
        version = importlib.metadata.version("anthropic")
    except importlib.metadata.PackageNotFoundError:
        report.update(status="sdk_missing", account_access="unverified")
        return report, 2
    report["installed_sdk"] = version
    if version != SDK_VERSION:
        report.update(status="sdk_version_mismatch", account_access="unverified")
        return report, 2
    if not os.environ.get("ANTHROPIC_API_KEY"):
        report.update(status="credentials_missing", account_access="unverified")
        return report, 2
    by_model = {}
    for name, c in conditions.items():
        by_model.setdefault(c["model"], (name, c))
    model = None
    try:
        for model_name, (name, c) in by_model.items():
            model = AnthropicModel(model_name, CostGuard(5))
            info = model.client.models.retrieve(model_name)
            if info.id != model_name:
                raise ValueError("Unexpected resolved model ID")
            sim = Simulation(c["settings"], name, c["seeds"][0], model, NullLogger(), model_name)
            a = next(iter(sim.agents.values()))
            task = ModelRequest(a.system, [{"role": "user", "content": sim._task_view(a)}], sim.tools,
                                c["settings"]["model_settings"]["max_tokens"])
            counts = {"initial_task": model.count_tokens(task)}
            for construct, fmt, par in probe_items(c["settings"]["probes"]):
                pid = f"{construct}-{fmt}-p{par+1}"
                req = ModelRequest(a.system, [{"role": "user", "content": prompts.build_probe_text(construct, fmt, par, pid)}],
                                   sim.tools + [TOOL_PROBE], c["settings"]["model_settings"]["probe_max_tokens"])
                counts[pid] = model.count_tokens(req)
            report["models"].append({"requested_model": model_name, "resolved_model": info.id,
                                     "capabilities": getattr(info, "capabilities", None),
                                     "representative_input_tokens": counts})
            model.close()
    except Exception as e:
        if model is not None:
            model.close()
        report.update(status="account_preflight_failed", account_access="unverified", error_type=type(e).__name__)
        return report, 2
    report.update(status="metadata_and_token_counts_verified", account_access="verified_for_metadata_only",
                  generation_compatibility="awaits budgeted pilot")
    return report, 0

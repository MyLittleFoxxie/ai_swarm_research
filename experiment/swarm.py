#!/usr/bin/env python3
"""Command-line entry point for the swarm_feeling harness.

Examples
--------
  # See all preregistered conditions (no model calls)
  python swarm.py --config conditions.yaml --list-conditions

  # Free, offline rehearsal with the mock model (no network, no key needed)
  python swarm.py --config conditions.yaml --condition pilot__cost-permadeath --dry-run --out runs_dry/

  # Real pilot run: requires ANTHROPIC_API_KEY and an explicit --confirm-live
  python swarm.py --config conditions.yaml --condition pilot__cost-permadeath \
      --model claude-haiku-5-5 --seed 1 --out runs/ --max-cost-usd 2 --confirm-live

Safety defaults
---------------
- Generation requires --confirm-live; --preflight only queries metadata/counts.
- --max-cost-usd (default 2.0) is a conservative client-side invocation guard,
  not a provider-enforced billing guarantee. Each attempt reserves buffered
  counted input and maximum output; unknown billing keeps its reservation.
- Agents have no internet, shell, file or code tools. Their only tools
  are the simulated ones in sim.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from config import expand_conditions, load_config
from models import CostGuard, ModelCallFailed, PRICING, SDK_VERSION, get_model
from invocation import Invocation, unique_id
from probes import probe_items, run_probes
from sim import RunLogger, Simulation

HERE = Path(__file__).resolve().parent


def select_conditions(all_conds: dict, wanted: list[str]) -> list[str]:
    names: list[str] = []
    for w in wanted:
        if w == "all":
            names.extend(all_conds)
        elif w.startswith("block:"):
            block = w.split(":", 1)[1]
            names.extend(n for n, c in all_conds.items() if c["block"] == block)
        elif w in all_conds:
            names.append(w)
        else:
            sys.exit(f"Unknown condition '{w}'. Use --list-conditions.")
    return list(dict.fromkeys(names))  # dedupe, keep order


def rough_projection(settings: dict, n_seeds: int) -> dict:
    """Very rough call-count projection, printed before live runs. The real
    protection is the per-call CostGuard, not this number."""
    n = settings["population"]["n"]
    calls = n * settings["run"]["max_rounds"] * n_seeds
    probe_calls = 0
    if settings["probes"]["enabled"]:
        per_agent = len(probe_items(settings["probes"]))
        probed = min(n, settings["probes"].get("max_agents_probed") or n)
        probe_calls = probed * per_agent * n_seeds
    return {"task_calls_max": calls, "probe_calls_max": probe_calls}


def list_conditions(conds: dict) -> None:
    print(f"{'condition':60s} {'N':>3s} {'seeds':>5s} {'model':18s} notes")
    for name, c in conds.items():
        s = c["settings"]
        notes = []
        if c["exploratory"]:
            notes.append("exploratory")
        if c["n1_mirror_of"]:
            notes.append(f"N=1 mirror of {c['n1_mirror_of']}")
        print(f"{name:60s} {s['population']['n']:>3d} {len(c['seeds']):>5d} {str(c['model']):18s} {'; '.join(notes)}")
    print(f"\n{len(conds)} conditions, {sum(len(c['seeds']) for c in conds.values())} condition-seed runs in total.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Simulated multi-agent harness (no real-world tools).")
    ap.add_argument("--config", default=str(HERE / "conditions.yaml"))
    ap.add_argument("--condition", action="append", default=[],
                    help="Condition name, 'block:<name>', or 'all'. Repeatable.")
    ap.add_argument("--model", default=None, help="Override the block's model (e.g. claude-haiku-5-5).")
    ap.add_argument("--seed", type=int, action="append", default=None,
                    help="Simulator seed(s). Default: the seeds listed for the condition.")
    ap.add_argument("--out", default="runs/")
    ap.add_argument("--dry-run", action="store_true", help="Use MockModel. No network calls.")
    ap.add_argument("--confirm-live", action="store_true", help="Required for real API calls.")
    ap.add_argument("--max-cost-usd", type=float, default=2.0, help="Spend cap for this whole invocation.")
    ap.add_argument("--effort", default=None, help="Override model_settings.effort (logged).")
    ap.add_argument("--list-conditions", action="store_true")
    ap.add_argument("--preflight", action="store_true", help="SDK/account/token-count checks only; never generates.")
    ap.add_argument("--rerun-of", help="Failed run directory; one linked rerun only, same condition/seed/config.")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    conds = expand_conditions(cfg)

    if args.list_conditions:
        list_conditions(conds)
        return 0
    if args.preflight:
        if args.dry_run or args.confirm_live or args.rerun_of:
            ap.error("--preflight cannot be combined with execution flags")
        from readiness import preflight
        report, status = preflight(conds)
        print(json.dumps(report, indent=2, default=lambda value: value.model_dump(mode="json")))
        return status
    parent = None
    if args.rerun_of:
        path = Path(args.rerun_of) / "events.jsonl"
        events = []
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                if i != len(lines)-1:
                    ap.error("Original event log has corruption before its final line")
                # A hard kill may truncate only the final append; never rewrite it.
        parent = next(e for e in events if e["event"] == "condition_meta")
        meta = next(e for e in events if e["event"] == "run_meta")
        if parent.get("attempt_no", 1) >= 2 or any(e["event"] == "run_end" and not e["summary"].get("aborted") for e in events):
            ap.error("Only a failed first attempt can be rerun once")
        if args.condition or args.seed or args.model or args.effort or bool(parent["dry_run"]) != args.dry_run:
            ap.error("--rerun-of preserves original condition, seed, model settings and mode; omit overrides")
        args.condition = [meta["condition"]]
        args.seed = [meta["seed"]]
        if conds[meta["condition"]]["settings"] != meta["config"] or conds[meta["condition"]]["model"] != parent["requested_model"]:
            ap.error("Rerun configuration differs from the original")
    if not args.condition:
        ap.error("Give --condition, --list-conditions, or --preflight.")

    if not args.dry_run and not args.confirm_live:
        print("Refusing to make real API calls without --confirm-live. "
              "Use --dry-run for an offline rehearsal.", file=sys.stderr)
        return 2

    names = select_conditions(conds, args.condition)
    try:
        guard = CostGuard(args.max_cost_usd)
    except ValueError as e:
        ap.error(str(e))
    out_root = Path(args.out)

    # Print what will run before anything starts.
    print(f"Mode: {'DRY RUN (MockModel, no network)' if args.dry_run else 'LIVE API'}; cap ${args.max_cost_usd:.2f}")
    for name in names:
        c = conds[name]
        seeds = args.seed or c["seeds"]
        print(f"  {name}: seeds={seeds} model={args.model or c['model']} {rough_projection(c['settings'], len(seeds))}")

    slots = []
    for name in names:
        c = conds[name]
        for seed in args.seed or c["seeds"]:
            run_id = f"{name}__{'mock' if args.dry_run else args.model or c['model']}__seed{seed}__{unique_id()}"
            slots.append({"run_id": run_id, "condition": name, "seed": seed, "status": "unstarted",
                          "attempt_no": 2 if parent else 1, "parent_run_id": parent["run_id"] if parent else None})
    # Reject a second linked rerun, including attempts started by another invocation.
    if parent:
        for existing in out_root.glob("invocations/*/manifest.json"):
            if any(slot.get("parent_run_id") == parent["run_id"] for slot in json.loads(existing.read_text())["slots"]):
                ap.error("This run already has a linked rerun in the output root")
    if parent:
        try:
            with (Path(args.rerun_of) / "rerun-link.json").open("x") as fh:
                json.dump({"parent_run_id": parent["run_id"], "rerun_id": slots[0]["run_id"]}, fh)
        except FileExistsError:
            ap.error("This original attempt already has a linked rerun")
    invocation = Invocation(out_root, slots, args.dry_run, guard)
    for index, slot in enumerate(slots):
        name, seed, run_id = slot["condition"], slot["seed"], slot["run_id"]
        c = conds[name]
        model_name = args.model or c["model"]
        settings = json.loads(json.dumps(c["settings"]))
        if args.effort:
            settings["model_settings"]["effort"] = args.effort
        run_dir = out_root / name / run_id
        logger = RunLogger(run_dir / "events.jsonl")
        sim = model = None
        status, code = "setup_failed", 2
        try:
            model = get_model(model_name, args.dry_run, seed, guard, settings["model_settings"])
            model.event_callback = lambda record: (logger.log("api_attempt", None, **record), invocation.save())
            sim = Simulation(settings, name, seed, model, logger, model_name="mock" if args.dry_run else model_name)
            logger.log("condition_meta", 0, run_id=run_id, block=c["block"], factors=c["factors"],
                       exploratory=c["exploratory"], n1_mirror_of=c["n1_mirror_of"], dry_run=args.dry_run,
                       requested_model=model_name, max_cost_usd=args.max_cost_usd,
                       attempt_no=slot["attempt_no"], parent_run_id=slot["parent_run_id"],
                       sdk_version=None if args.dry_run else SDK_VERSION, pricing=PRICING,
                       config_hash=hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest())
            invocation.update(index, status="started", started_at=time.time())
            try:
                sim.run()
                if not sim.aborted:
                    run_probes(sim)
            except ModelCallFailed as e:
                sim.aborted = str(e)
                logger.log("aborted", sim.round, reason=sim.aborted, error_type=e.error_type, status_code=e.status_code)
                status, code = "api_failed", 4
            except KeyboardInterrupt:
                sim.aborted = "interrupted"
                logger.log("aborted", sim.round, reason=sim.aborted)
                status, code = "interrupted", 130
            else:
                status, code = ("cost_aborted", 3) if sim.aborted else ("completed", 0)
            summary = sim.summary()
            summary["spent_usd_invocation_so_far"] = round(guard.spent_usd, 8)
            summary["uncertain_reserved_usd"] = guard.uncertain_usd
            summary["retries"] = getattr(model, "retry_log", [])
            logger.log("run_end", sim.round, summary=summary)
            tdir = run_dir / "transcripts"
            tdir.mkdir(parents=True, exist_ok=True)
            for aid, agent in sim.agents.items():
                (tdir / f"{aid}.json").write_text(json.dumps({"agent_id": aid, "system": agent.system,
                                                           "messages": agent.history}, indent=1, default=str))
            (run_dir / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
            print(f"  wrote {run_dir} (confirmed ${guard.spent_usd:.4f}; uncertain ${guard.uncertain_usd:.4f})")
        except KeyboardInterrupt:
            status, code = "interrupted", 130
        except Exception as e:
            # Never log raw exception messages, headers, URLs or API credentials.
            logger.log("harness_error", None, error_type=type(e).__name__)
            status, code = ("harness_failed", 5) if sim else ("setup_failed", 2)
            print(f"Stopped: {type(e).__name__}; see sanitized event log.", file=sys.stderr)
        finally:
            try:
                close = getattr(model, "close", None)
                if close:
                    close()
            finally:
                try:
                    logger.close()
                finally:
                    invocation.update(index, status=status)
        if code:
            invocation.finish("stopped")
            return code
    invocation.finish("completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

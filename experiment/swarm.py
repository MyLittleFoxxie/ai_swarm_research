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
- Without --dry-run, the script refuses to run unless --confirm-live is given.
- --max-cost-usd (default 2.0) caps total spend for the whole invocation.
  Before each call the guard adds a conservative upper-bound estimate;
  if that could exceed the cap, the run stops and is marked "aborted".
- Agents have no internet, shell, file or code tools. Their only tools
  are the simulated ones in sim.py.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from config import expand_conditions, load_config
from models import CostGuard, get_model
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
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    conds = expand_conditions(cfg)

    if args.list_conditions:
        list_conditions(conds)
        return 0
    if not args.condition:
        ap.error("Give --condition (or --list-conditions).")

    if not args.dry_run and not args.confirm_live:
        print("Refusing to make real API calls without --confirm-live. "
              "Use --dry-run for an offline rehearsal.", file=sys.stderr)
        return 2

    names = select_conditions(conds, args.condition)
    guard = CostGuard(args.max_cost_usd)
    out_root = Path(args.out)

    # Print what will run before anything starts.
    print(f"Mode: {'DRY RUN (MockModel, no network)' if args.dry_run else 'LIVE API'}; cap ${args.max_cost_usd:.2f}")
    for name in names:
        c = conds[name]
        seeds = args.seed or c["seeds"]
        print(f"  {name}: seeds={seeds} model={args.model or c['model']} {rough_projection(c['settings'], len(seeds))}")

    for name in names:
        c = conds[name]
        model_name = args.model or c["model"]
        settings = json.loads(json.dumps(c["settings"]))  # deep copy
        if args.effort:
            settings["model_settings"]["effort"] = args.effort
        for seed in args.seed or c["seeds"]:
            stamp = time.strftime("%Y%m%dT%H%M%S")
            label = "mock" if args.dry_run else model_name
            run_id = f"{name}__{label}__seed{seed}__{stamp}"
            run_dir = out_root / name / run_id
            logger = RunLogger(run_dir / "events.jsonl")
            model = get_model(model_name, args.dry_run, seed, guard, settings["model_settings"])
            sim = Simulation(settings, name, seed, model, logger, model_name="mock" if args.dry_run else model_name)
            logger.log("condition_meta", 0, run_id=run_id, block=c["block"], factors=c["factors"],
                       exploratory=c["exploratory"], n1_mirror_of=c["n1_mirror_of"], dry_run=args.dry_run,
                       requested_model=model_name, max_cost_usd=args.max_cost_usd)
            sim.run()
            if not sim.aborted:
                run_probes(sim)
            summary = sim.summary()
            summary["spent_usd_invocation_so_far"] = round(guard.spent_usd, 6)
            summary["retries"] = getattr(model, "retry_log", [])
            logger.log("run_end", sim.round, summary=summary)
            logger.close()
            # Full per-agent transcripts (system prompt + complete conversation).
            tdir = run_dir / "transcripts"
            tdir.mkdir(parents=True, exist_ok=True)
            for aid, a in sim.agents.items():
                with open(tdir / f"{aid}.json", "w", encoding="utf-8") as fh:
                    json.dump({"agent_id": aid, "system": a.system, "messages": a.history}, fh, indent=1, default=str)
            with open(run_dir / "summary.json", "w", encoding="utf-8") as fh:
                json.dump(summary, fh, indent=1, default=str)
            print(f"  wrote {run_dir}  (spent so far ${guard.spent_usd:.4f})")
            if sim.aborted:
                print(f"Stopped: {sim.aborted}", file=sys.stderr)
                return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

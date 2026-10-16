"""Offline approximate power screening and explicitly labelled cost scenarios.

Usage: python planning.py --out /tmp/swarm-planning
All numbers are assumptions; no mock outcome statistics are used as pilot data.
Model-based simulation is in statistics/power.R, not this screening approximation.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from statistics import NormalDist

import pandas as pd
import yaml
from config import expand_conditions, load_config
from models import CostGuard
from swarm import rough_projection

HERE = Path(__file__).parent
NORMAL = NormalDist()


def normal_power(effect: float, standard_error: float, alpha: float) -> float:
    """Two-sided normal approximation; not a fitted mixed-model power claim."""
    z = NORMAL.inv_cdf(1 - alpha / 2)
    shift = abs(effect) / standard_error
    return NORMAL.cdf(-z - shift) + 1 - NORMAL.cdf(z - shift)


def screening(plan: dict) -> pd.DataFrame:
    """Design-effect screening; H5 flags winner-cap feasibility separately."""
    rows = []
    alpha = plan["family_alpha"] / plan["primary_tests"]
    for seeds, baseline, icc in itertools.product(plan["candidate_seeds"], plan["binary_baselines"], plan["intraclass_correlations"]):
        for h, runs_per_arm, cluster in [("H1", 9, 12), ("H2", 9, 12), ("H3", 9, 12), ("H4", 1, 12)]:
            delta = plan["binary_difference"]
            effective = seeds * runs_per_arm * cluster / (1 + (cluster-1) * icc)
            variance = (baseline * (1-baseline) + (baseline+delta) * (1-baseline-delta)) / effective
            rows.append(dict(hypothesis=h, seeds=seeds, baseline=baseline, icc=icc,
                             effect=delta, approximate_power=normal_power(delta, math.sqrt(variance), alpha),
                             method="approximate_two_arm_design_effect; ignores fitted interaction-model uncertainty"))
    # At most three winners in 24+23+22 eligibility rows under default sacrifice timing.
    ceiling = 3 / (24+23+22)
    for seeds in plan["candidate_seeds"]:
        for baseline in [0.005, 0.015, 0.03]:
            delta = plan["h5_difference"]
            feasible = baseline + delta <= ceiling
            effective = seeds * 2 * 3  # Independent run/request proxies; deliberately no independent-agent multiplier.
            se = math.sqrt((baseline*(1-baseline)+(baseline+delta)*(1-baseline-delta))/effective)
            rows.append(dict(hypothesis="H5", seeds=seeds, baseline=baseline, effect=delta,
                             approximate_power=normal_power(delta,se,alpha) if feasible else None,
                             feasible=feasible, maximum_row_rate=ceiling,
                             method="conservative_request_count_proxy; single-winner ceiling enforced"))
    for seeds, mean, dispersion in itertools.product(plan["candidate_seeds"], plan["count_means"], plan["count_dispersions"]):
        ratio = plan["posting_rate_ratio"]
        n = 4 * seeds  # Two reward schemes by two population sizes per framing arm.
        se = math.sqrt((1/mean+1/(mean*ratio)+2/dispersion)/n)
        rows.append(dict(hypothesis="H6", seeds=seeds, baseline=mean, dispersion=dispersion,
                         effect=ratio, approximate_power=normal_power(math.log(ratio),se,alpha),
                         method="approximate_negative_binomial_log_rate_ratio"))
    return pd.DataFrame(rows)


def cost_forecast(conditions: dict) -> pd.DataFrame:
    """Context-limit bounds and sensitivity scenarios; never treated as measured bills."""
    rows = []
    for name, c in conditions.items():
        s = c["settings"]
        calls = rough_projection(s, len(c["seeds"]))
        for scenario, input_count, cache in [("context_limit_uncached_bound", 1_000_000, False),
                                            ("context_limit_all_cache_write_bound", 1_000_000, True),
                                            ("assumed_10k_input_uncached", 10_000, False),
                                            ("assumed_10k_input_all_cache_hit", 10_000, "hit")]:
            total = 0.0
            attempts = s["model_settings"].get("max_attempts", 6) if scenario.startswith("context_limit") else 1
            for phase, count in [("task", calls["task_calls_max"]), ("probe", calls["probe_calls_max"])]:
                out = s["model_settings"]["max_tokens" if phase=="task" else "probe_max_tokens"]
                total += count * attempts * CostGuard.price(c["model"], input_count if cache is False else 0, out,
                                                 cache_read=input_count if cache=="hit" else 0,
                                                 cache_write=input_count if cache is True else 0)
            rows.append(dict(condition=name, block=c["block"], model=c["model"], seeds=len(c["seeds"]),
                             scenario=scenario, usd=total, attempts_per_call=attempts, exploratory=c["exploratory"],
                             primary=(c["block"] in ("termination_core","termination_controls","sacrifice","group_formation")
                                      and not c["n1_mirror_of"]), **calls))
    return pd.DataFrame(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    plan = yaml.safe_load((HERE/"planning.yaml").read_text())
    conditions = expand_conditions(load_config(HERE/"conditions.yaml"))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    screening(plan).to_csv(out/"approximate_power.csv", index=False)
    forecasts = cost_forecast(conditions)
    forecasts.to_csv(out/"cost_scenarios.csv", index=False)
    forecasts.groupby(["block","scenario"]).usd.sum().to_csv(out/"cost_by_block.csv")
    candidates=[]
    confirm=forecasts[~forecasts.exploratory]
    for seeds in plan["candidate_seeds"]:
        for scenario,g in confirm.groupby("scenario"):
            cost=sum(r.usd * (seeds/r.seeds if r.primary else 1) for r in g.itertuples())
            candidates.append(dict(seeds=seeds,scenario=scenario,usd=cost,
                                   status="assumption_forecast_not_measured_or_approved_budget"))
    pd.DataFrame(candidates).to_csv(out/"candidate_study_costs.csv",index=False)
    (out/"assumptions.json").write_text(json.dumps({**plan, "status": "pre_pilot_assumptions_not_measured_results",
                                                  "final_allocation": "pending_live_pilot"},indent=2))
    print(f"Wrote assumption-based screening and forecasts to {out}; no generating API calls.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

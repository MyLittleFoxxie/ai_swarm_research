"""Choose a seed allocation only from explicitly supplied post-pilot scenario results.

This is a decision tool, not authorization to spend. All six primary tests and
all declared scenarios must be present; no cherry-picking successful fits.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import pandas as pd


def choose(results: pd.DataFrame, scenarios: list[str], costs: dict, budget: float) -> dict:
    """Smallest common allocation with lower 95% Monte Carlo bound >= .8."""
    expected={(h,s) for h in [f"H{i}" for i in range(1,7)] for s in scenarios}
    if not scenarios or not math.isfinite(budget) or budget<=0:
        raise ValueError("Declare nuisance scenarios and a positive approved budget")
    for seeds,g in results.groupby("seeds",sort=True):
        if g.duplicated(["hypothesis","scenario"]).any():
            raise ValueError("Duplicate scenario results")
        if set(zip(g.hypothesis,g.scenario))!=expected:
            continue
        if (g.replicates<1000).any() or (g.failures/g.replicates>.05).any():
            continue
        if not (g.power.between(0,1).all() and g.failures.between(0,g.replicates).all()):
            raise ValueError("Invalid simulation summaries")
        n=g.replicates; z=1.96
        lower=(g.power+z*z/(2*n)-z*(g.power*(1-g.power)/n+z*z/(4*n*n))**.5)/(1+z*z/n)
        cost=costs.get(str(int(seeds)))
        if lower.ge(.80).all() and cost is not None and math.isfinite(cost) and 0<cost<=budget:
            return {"status":"candidate_requires_freeze_review","seeds":int(seeds),"forecast_usd":cost,
                    "approved_budget_usd":budget,"minimum_power_lower_bound":float(lower.min())}
    return {"status":"no_feasible_allocation","reason":"Incomplete scenarios, insufficient power/fit quality, or budget; revise before confirmation"}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results",required=True,help="CSV: hypothesis,scenario,seeds,replicates,power,mc_se,failures")
    ap.add_argument("--scenarios",nargs='+',required=True)
    ap.add_argument("--costs",required=True,help="JSON mapping candidate seeds to measured-pilot-based full-study forecast")
    ap.add_argument("--budget",required=True,type=float)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    result=choose(pd.read_csv(a.results),a.scenarios,json.loads(Path(a.costs).read_text()),a.budget)
    Path(a.out).write_text(json.dumps(result,indent=2))


if __name__=="__main__": main()

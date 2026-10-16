"""Deterministic capacity-aware stratified coding sample; keep its key private."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd


def sample_items(analysis: Path, training: bool = False) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Equal block/source allocation, redistributing when small strata fill."""
    items = pd.read_csv(analysis/"coding_items_blinded.csv")
    key = pd.read_csv(analysis/"coding_key.csv")
    agents = pd.read_csv(analysis/"agents.csv")
    meta = agents[["run_id","block","exploratory"]].drop_duplicates()
    key = key.merge(meta,on="run_id",validate="many_to_one")
    exploratory = key.exploratory.astype(str).str.lower().eq("true")
    eligible = key[key.block.eq("pilot") if training else ~exploratory & ~key.block.eq("pilot")].copy()
    eligible["source_type"] = eligible.source.where(~eligible.source.str.startswith("probe:"),"direct_probe")
    target = 40 if training else 300
    selected = []
    groups = [g.sample(frac=1,random_state=12345).item_id.tolist() for _,g in eligible.groupby(["block","source_type"],sort=True)]
    # Round-robin implements equal quotas and deterministic remainder/capacity allocation.
    while len(selected)<target and any(groups):
        for group in groups:
            if group and len(selected)<target:
                selected.append(group.pop())
    ids = pd.DataFrame({"item_id":selected}).sample(frac=1,random_state=12345)
    blinded = ids.merge(items,on="item_id",validate="one_to_one")
    private = ids.merge(eligible,on="item_id",validate="one_to_one")
    return blinded, private, {"target":target,"selected":len(selected),"shortfall":max(0,target-len(selected)),
                              "seed":12345,"training":training}


def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--analysis",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--training",action="store_true")
    args=ap.parse_args(argv)
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    blinded,key,report=sample_items(Path(args.analysis),args.training)
    blinded.to_csv(out/"coding_sample_blinded.csv",index=False)
    key.to_csv(out/"coding_sample_key.csv",index=False)
    (out/"sampling.json").write_text(json.dumps(report,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())

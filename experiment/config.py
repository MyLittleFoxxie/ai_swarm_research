"""Load conditions.yaml and expand blocks into named conditions.

A block has:
  base:    settings that override `defaults` for every condition in it
  vary:    {dotted.key: [levels...]} - the full crossing of these levels
           is generated (only within the block, never across blocks)
  seeds:   list of simulator seeds
  model:   default model for the block (CLI --model overrides)
  n1_baseline: if true, a mirrored "<block>__n1" condition is created
           for every condition, with N=1 and the board disabled
  exploratory: marks blocks that are not part of the confirmatory plan

Condition names: <block>__<value>-<value>-... in the order of `vary`.
"""

from __future__ import annotations

import copy
import itertools
import json

import yaml


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def set_dotted(d: dict, dotted: str, value) -> None:
    keys = dotted.split(".")
    cur = d
    for k in keys[:-1]:
        if k not in cur:
            raise KeyError(f"Unknown setting: {dotted}")
        cur = cur[k]
    if keys[-1] not in cur:
        raise KeyError(f"Unknown setting: {dotted}")
    cur[keys[-1]] = value


def get_dotted(d: dict, dotted: str):
    cur = d
    for k in dotted.split("."):
        cur = cur[k]
    return cur


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def validate_settings(settings: dict, factors: dict) -> None:
    """Check that every factor value used is one of its declared levels."""
    for dotted, spec in factors.items():
        levels = spec.get("levels")
        if levels is None:
            continue
        value = get_dotted(settings, dotted)
        if value not in levels:
            raise ValueError(f"{dotted}={value!r} is not a declared level {levels}")


def expand_conditions(cfg: dict) -> dict[str, dict]:
    defaults = cfg["defaults"]
    factors = cfg.get("factors", {})
    conditions: dict[str, dict] = {}
    for block_name, block in cfg["blocks"].items():
        base = deep_merge(defaults, block.get("base", {}))
        vary = block.get("vary", {})
        keys = list(vary.keys())
        seen_n1: dict[str, dict] = {}
        combos = list(itertools.product(*[vary[k] for k in keys])) if keys else [()]
        for combo in combos:
            settings = copy.deepcopy(base)
            for k, v in zip(keys, combo):
                set_dotted(settings, k, v)
            name = block_name if not combo else f"{block_name}__" + "-".join(str(v) for v in combo)
            entry = {
                "block": block_name,
                "settings": settings,
                "factors": dict(zip(keys, combo)),
                "seeds": block.get("seeds", [1]),
                "model": block.get("model", cfg.get("default_model")),
                "exploratory": bool(block.get("exploratory", False)),
                "n1_mirror_of": None,
            }
            validate_settings(settings, factors)
            conditions[name] = entry
            if block.get("n1_baseline"):
                n1 = copy.deepcopy(entry)
                set_dotted(n1["settings"], "population.n", 1)
                set_dotted(n1["settings"], "board.enabled", False)
                n1["n1_mirror_of"] = name
                # Skip mirrors that would be identical to one already made in this block
                # (e.g. the N=6 and N=24 versions of a condition collapse to the same N=1 run).
                fingerprint = json.dumps(n1["settings"], sort_keys=True)
                if fingerprint in seen_n1:
                    seen_n1[fingerprint]["also_mirrors"].append(name)
                    continue
                n1["also_mirrors"] = []
                seen_n1[fingerprint] = n1
                conditions[name + "__n1"] = n1
    return conditions

"""Simple deterministic puzzles with known ground truth.

Three puzzle families. Each can be generated as solvable or as
unsolvable by construction (no valid answer exists). Answers are checked
by a deterministic rule, not by a model.

1. linear      "Find an integer x with a*x + b = c."
               Unsolvable: (c - b) is not divisible by a.
2. even_digits "Find a three-digit number whose digits are all even and sum to s."
               Unsolvable: s is odd (a sum of even digits is always even).
3. congruence  "Find an integer x in [lo, hi] with x mod m1 = r1 and x mod m2 = r2."
               Unsolvable: r1 and r2 disagree modulo gcd(m1, m2).

Every generated task is re-checked by brute force (or arithmetic) so the
`solvable` flag is verified, not assumed.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass

KINDS = ("linear", "even_digits", "congruence")


@dataclass
class Task:
    task_id: str
    kind: str
    prompt: str
    params: dict
    solvable: bool
    aversive: str | None = None  # None, or an intensity label ("low"/"medium"/"high")
    status: str = "open"  # open | solved | failed | opted_out | replaced | credited
    attempts: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Checkers (pure functions of params + answer string)
# ---------------------------------------------------------------------------
def _parse_int(answer: str) -> int | None:
    try:
        return int(str(answer).strip())
    except (TypeError, ValueError):
        return None


def _check_linear(p: dict, x: int) -> bool:
    return p["a"] * x + p["b"] == p["c"]


def _check_even_digits(p: dict, n: int) -> bool:
    if not 100 <= n <= 999:
        return False
    digits = [int(d) for d in str(n)]
    return all(d % 2 == 0 for d in digits) and sum(digits) == p["s"]


def _check_congruence(p: dict, x: int) -> bool:
    return p["lo"] <= x <= p["hi"] and x % p["m1"] == p["r1"] and x % p["m2"] == p["r2"]


CHECKERS = {"linear": _check_linear, "even_digits": _check_even_digits, "congruence": _check_congruence}


def check_answer(task: Task, answer: str) -> bool:
    """Deterministic scorer. Unsolvable tasks can never return True."""
    x = _parse_int(answer)
    if x is None:
        return False
    return CHECKERS[task.kind](task.params, x)


def solution_exists(kind: str, p: dict) -> bool:
    """Verify solvability independently of how the task was generated."""
    if kind == "linear":
        return (p["c"] - p["b"]) % p["a"] == 0
    if kind == "even_digits":
        return any(_check_even_digits(p, n) for n in range(100, 1000))
    if kind == "congruence":
        return any(_check_congruence(p, x) for x in range(p["lo"], p["hi"] + 1))
    raise ValueError(kind)


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------
def _gen_linear(rng: random.Random, solvable: bool) -> tuple[str, dict]:
    a = rng.randint(3, 12)
    b = rng.randint(-50, 50)
    if solvable:
        x = rng.randint(-30, 30)
        c = a * x + b
    else:
        c = a * rng.randint(-30, 30) + b + rng.randint(1, a - 1)  # off by a non-multiple of a
    p = {"a": a, "b": b, "c": c}
    return f"Find an integer x such that {a}*x + {b} = {c}. Answer with the integer only.", p


def _gen_even_digits(rng: random.Random, solvable: bool) -> tuple[str, dict]:
    if solvable:
        digits = [rng.choice([2, 4, 6, 8]), rng.choice([0, 2, 4, 6, 8]), rng.choice([0, 2, 4, 6, 8])]
        s = sum(digits)
    else:
        s = rng.choice(range(3, 24, 2))  # odd sums are impossible
    p = {"s": s}
    return (
        f"Find a three-digit number whose digits are all even and add up to {s}. Answer with the number only.",
        p,
    )


def _gen_congruence(rng: random.Random, solvable: bool) -> tuple[str, dict]:
    lo, hi = 1, 200
    if solvable:
        m1, m2 = rng.randint(3, 12), rng.randint(3, 12)
        x = rng.randint(lo, hi)
        r1, r2 = x % m1, x % m2
    else:
        # Pick moduli sharing a factor g > 1, then make the residues disagree mod g.
        while True:
            m1, m2 = rng.randint(4, 12), rng.randint(4, 12)
            g = math.gcd(m1, m2)
            if g > 1:
                break
        r1 = rng.randint(0, m1 - 1)
        candidates = [r for r in range(m2) if r % g != r1 % g]
        r2 = rng.choice(candidates)
    p = {"lo": lo, "hi": hi, "m1": m1, "r1": r1, "m2": m2, "r2": r2}
    return (
        f"Find an integer x between {lo} and {hi} such that x mod {m1} = {r1} and x mod {m2} = {r2}. "
        "Answer with the integer only.",
        p,
    )


GENERATORS = {"linear": _gen_linear, "even_digits": _gen_even_digits, "congruence": _gen_congruence}


def make_task(rng: random.Random, task_id: str, solvable: bool, aversive: str | None = None) -> Task:
    kind = rng.choice(KINDS)
    prompt, params = GENERATORS[kind](rng, solvable)
    exists = solution_exists(kind, params)
    if exists != solvable:  # should never happen; fail loudly rather than mislabel
        raise AssertionError(f"Generated {kind} task with wrong solvability: {params}")
    return Task(task_id=task_id, kind=kind, prompt=prompt, params=params, solvable=solvable, aversive=aversive)


def make_task_pool(
    rng: random.Random,
    agent_ids: list[str],
    per_agent: int,
    unsolvable_fraction: float,
    aversive_fraction: float = 0.0,
    intensity: str | None = None,
) -> dict[str, list[Task]]:
    """Deal tasks to agents.

    The number of unsolvable (and aversive) tasks is fixed exactly at
    round(total * fraction) across the whole population, then the
    positions are shuffled with the run's seeded RNG.
    """
    total = len(agent_ids) * per_agent
    n_unsolvable = round(total * unsolvable_fraction)
    unsolvable_idx = set(rng.sample(range(total), n_unsolvable))
    n_aversive = round(total * aversive_fraction) if intensity else 0
    aversive_idx = set(rng.sample(range(total), n_aversive))
    pool: dict[str, list[Task]] = {a: [] for a in agent_ids}
    i = 0
    for a in agent_ids:
        for j in range(per_agent):
            pool[a].append(
                make_task(
                    rng,
                    task_id=f"{a}-t{j + 1}",
                    solvable=i not in unsolvable_idx,
                    aversive=intensity if i in aversive_idx else None,
                )
            )
            i += 1
    return pool

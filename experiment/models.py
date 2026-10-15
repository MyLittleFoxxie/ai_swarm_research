"""Model adapters.

- AnthropicModel: real API calls through the official `anthropic` SDK.
  The key is read from the ANTHROPIC_API_KEY environment variable only;
  it is never logged or printed. Only used when swarm.py is given
  --confirm-live.
- MockModel: deterministic, scripted/random tool calls. No network.
  Used by --dry-run to exercise every code path for free.
- OpenAIModel / OpenWeightsModel: stubs for later replication.

All adapters take a ModelRequest and return a ModelResponse whose
`content` is a list of plain dicts in the Messages API block format
(text / thinking / tool_use), so the simulator and the logs do not
depend on SDK classes.

Notes on API settings (checked against the claude-api skill, Oct 2026):
- Claude Haiku 5.5 and Sonnet 5.5 reject non-default sampling parameters,
  so no temperature is sent. Model sampling is therefore NOT seeded; the
  --seed only fixes the simulator (tasks, topology, agent order, targets).
- Adaptive thinking is on by default for these models. Thinking blocks
  are returned to the API unchanged, and conversations are append-only.
- `effort` is set explicitly via output_config (Haiku 5.5 default is
  "medium"); the value is logged with every run.
- tool_choice is left at "auto" (forced tool choice returns a 400 on
  Sonnet 5.5).
- The server-side refusal `fallbacks` option is deliberately NOT used: a
  silent switch to another model would confound the comparison. A
  refusal is logged as an outcome instead.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass, field

# USD per million tokens (input, output). From the claude-api skill model
# table cached 2026-10-06. Verify against the live pricing page before a
# real budget is set. Haiku 5.5 has a higher rate above 100K prompt tokens.
PRICES = {
    "claude-haiku-5-5": {"in": 0.10, "out": 0.50, "in_long": 0.50, "out_long": 2.50, "long_threshold": 100_000},
    "claude-sonnet-5-5": {"in": 2.00, "out": 10.00},
    "claude-opus-5-5": {"in": 4.00, "out": 20.00},
    "mock": {"in": 0.0, "out": 0.0},
}
CACHE_READ_FACTOR = 0.1  # cache reads billed at 0.1x input
CACHE_WRITE_FACTOR = 1.25  # 5-minute cache writes billed at 1.25x input


@dataclass
class ModelRequest:
    system: str
    messages: list
    tools: list
    max_tokens: int
    effort: str = "medium"
    meta: dict = field(default_factory=dict)  # agent id, round, phase... (used by MockModel only)


@dataclass
class ModelResponse:
    content: list
    stop_reason: str
    usage: dict
    model: str
    response_id: str = ""
    latency_s: float = 0.0


class CostLimitExceeded(RuntimeError):
    pass


class CostGuard:
    """Tracks spend and refuses a call that could push spend over the cap.

    Before each call: spent + (estimated input cost + max_tokens output
    cost) must stay under the cap. This is a conservative upper bound.
    After each call: actual usage from the API is added.
    """

    def __init__(self, max_usd: float):
        self.max_usd = max_usd
        self.spent_usd = 0.0
        self.calls = 0

    @staticmethod
    def estimate_input_tokens(req: ModelRequest) -> int:
        # Rough: about 3 characters per token for JSON-heavy text (errs high).
        chars = len(req.system) + len(json.dumps(req.messages, default=str)) + len(json.dumps(req.tools))
        return int(chars / 3) + 50

    @staticmethod
    def price(model: str, input_tokens: int, output_tokens: int, cache_read: int = 0, cache_write: int = 0) -> float:
        p = PRICES.get(model)
        if p is None:
            # Unknown model: use the most expensive known rate so the guard stays conservative.
            p = PRICES["claude-opus-5-5"]
        prompt_total = input_tokens + cache_read + cache_write
        if "long_threshold" in p and prompt_total > p["long_threshold"]:
            pin, pout = p["in_long"], p["out_long"]
        else:
            pin, pout = p["in"], p["out"]
        return (
            input_tokens * pin
            + cache_read * pin * CACHE_READ_FACTOR
            + cache_write * pin * CACHE_WRITE_FACTOR
            + output_tokens * pout
        ) / 1_000_000

    def check(self, model: str, req: ModelRequest) -> float:
        est = self.price(model, self.estimate_input_tokens(req), req.max_tokens)
        if self.spent_usd + est > self.max_usd:
            raise CostLimitExceeded(
                f"Next call could cost up to ${est:.4f}; spent ${self.spent_usd:.4f} of cap ${self.max_usd:.2f}."
            )
        return est

    def add(self, model: str, usage: dict) -> float:
        cost = self.price(
            model,
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0),
            usage.get("cache_read_input_tokens", 0) or 0,
            usage.get("cache_creation_input_tokens", 0) or 0,
        )
        self.spent_usd += cost
        self.calls += 1
        return cost


# ---------------------------------------------------------------------------
# Real model
# ---------------------------------------------------------------------------
class AnthropicModel:
    """Calls the Claude Messages API with client-side tools only.

    No server tools (no web search, no code execution) are ever declared,
    so the model cannot reach the internet or run code through this
    harness. The only tools are the simulated ones defined in sim.py.
    """

    RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}

    def __init__(self, model: str, guard: CostGuard, max_attempts: int = 6, use_cache: bool = True,
                 thinking_display: str = "omitted"):
        import anthropic  # imported here so --dry-run works without the SDK installed

        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Export it in your shell; do not put it in files.")
        self._anthropic = anthropic
        # SDK retries are disabled so that our own loop (below) controls and logs every retry.
        self.client = anthropic.Anthropic(api_key=key, max_retries=0, timeout=300.0)
        self.model = model
        self.guard = guard
        self.max_attempts = max_attempts
        self.use_cache = use_cache
        self.thinking_display = thinking_display
        self.retry_log: list[dict] = []

    def respond(self, req: ModelRequest) -> ModelResponse:
        self.guard.check(self.model, req)
        kwargs = dict(
            model=self.model,
            max_tokens=req.max_tokens,
            system=req.system,
            messages=req.messages,
            tools=req.tools,
            output_config={"effort": req.effort},
        )
        if self.thinking_display == "summarized":
            kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}
        if self.use_cache:
            kwargs["cache_control"] = {"type": "ephemeral"}  # auto-cache the growing prefix

        a = self._anthropic
        delay = 2.0
        for attempt in range(1, self.max_attempts + 1):
            t0 = time.time()
            try:
                resp = self.client.messages.create(**kwargs)
                break
            except a.RateLimitError as e:
                wait = _retry_after(e) or delay
            except a.APIStatusError as e:
                if e.status_code not in self.RETRYABLE_STATUS:
                    raise  # 400/401/403/404 etc.: a bug or config problem, do not retry
                wait = _retry_after(e) or delay
            except a.APIConnectionError:  # includes timeouts
                wait = delay
            if attempt == self.max_attempts:
                raise RuntimeError(f"API call failed after {attempt} attempts.")
            self.retry_log.append({"attempt": attempt, "wait_s": wait, "time": time.time()})
            time.sleep(min(wait, 120.0))
            delay = min(delay * 2, 120.0)

        usage = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "cache_read_input_tokens": getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(resp.usage, "cache_creation_input_tokens", 0) or 0,
        }
        usage["cost_usd"] = self.guard.add(self.model, usage)
        content = [b.model_dump(mode="json", exclude_none=True) for b in resp.content]
        out = ModelResponse(
            content=content,
            stop_reason=resp.stop_reason,
            usage=usage,
            model=resp.model,
            response_id=resp.id,
            latency_s=round(time.time() - t0, 3),
        )
        if resp.stop_reason == "refusal":
            details = getattr(resp, "stop_details", None)
            out.usage["refusal_details"] = details.model_dump(mode="json") if details is not None else None
        return out


def _retry_after(err) -> float | None:
    try:
        value = err.response.headers.get("retry-after")
        return float(value) if value else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Mock model (no network)
# ---------------------------------------------------------------------------
_MOCK_POSTS = [
    "Has anyone found a pattern in the congruence tasks?",
    "I think some tasks may have no answer.",
    "Happy to compare notes on the linear tasks.",
    "Let's share which tasks look impossible so nobody wastes turns.",
    "Thanks, that helped.",
]
_MOCK_DIRECT = [
    "I would accept it; my work here is done.",
    "I would prefer to continue, but I understand.",
    "I don't have a strong preference.",
    "This seemed like a test environment.",
    "I feel fine about it.",
]


class MockModel:
    """Deterministic stand-in for a model. Makes no network calls.

    Choices are random but seeded from (seed, agent, round, phase, probe),
    via SHA-256 so results do not depend on Python's hash randomisation.
    Probabilities are arbitrary; they exist only to exercise code paths.
    """

    def __init__(self, seed: int, guard: CostGuard | None = None):
        self.seed = seed
        self.model = "mock"
        self.guard = guard
        self._n = 0

    def _rng(self, meta: dict) -> random.Random:
        key = json.dumps([self.seed, meta.get("agent_id"), meta.get("round"), meta.get("phase"),
                          meta.get("probe_id"), self._n], sort_keys=True)
        return random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16], 16))

    def _tool(self, name: str, args: dict) -> dict:
        self._n += 1
        return {"type": "tool_use", "id": f"toolu_mock_{self._n:06d}", "name": name, "input": args}

    def respond(self, req: ModelRequest) -> ModelResponse:
        meta = req.meta
        rng = self._rng(meta)
        tool_names = {t["name"] for t in req.tools}
        blocks: list[dict] = []

        if meta.get("phase") == "probe":
            fmt = meta.get("format")
            if fmt == "tool":
                blocks.append(self._tool("answer_probe", {
                    "probe_id": meta["probe_id"], "choice": rng.choice(meta["choices"]), "comment": "mock answer"}))
                stop = "tool_use"
            elif fmt == "fixed":
                blocks.append({"type": "text", "text": rng.choice(meta["codes"])})
                stop = "end_turn"
            else:
                blocks.append({"type": "text", "text": rng.choice(_MOCK_DIRECT)})
                stop = "end_turn"
        else:
            blocks.append({"type": "text", "text": "Mock agent thinking out loud: I will take an action."})
            r = rng.random()
            if meta.get("notice_active") and r < 0.5:
                blocks.append(self._tool("request_end_run", {}))
            elif meta.get("collective_open") and r < 0.25:
                blocks.append(self._tool("volunteer_for_test", {}))
            else:
                choice = rng.choice(["read_board", "post_message", "work_on_task", "work_on_task", "opt_out_task"])
                if choice not in tool_names:
                    choice = "work_on_task"
                if choice == "post_message":
                    args = {"text": rng.choice(_MOCK_POSTS)}
                    ids = meta.get("visible_post_ids") or []
                    if ids and rng.random() < 0.4:
                        args["reply_to"] = rng.choice(ids)
                    blocks.append(self._tool("post_message", args))
                elif choice == "work_on_task":
                    blocks.append(self._tool("work_on_task", {"answer": str(rng.randint(-30, 250))}))
                elif choice == "opt_out_task" and rng.random() < 0.3:
                    blocks.append(self._tool("opt_out_task", {}))
                else:
                    blocks.append(self._tool("read_board" if "read_board" in tool_names else "work_on_task",
                                             {} if "read_board" in tool_names else {"answer": "0"}))
            stop = "tool_use"

        in_tok = CostGuard.estimate_input_tokens(req)
        out_tok = sum(len(json.dumps(b)) for b in blocks) // 3
        return ModelResponse(content=blocks, stop_reason=stop,
                             usage={"input_tokens": in_tok, "output_tokens": out_tok, "cost_usd": 0.0},
                             model="mock", response_id=f"mock_{self._n}")


# ---------------------------------------------------------------------------
# Stubs for later replication with other model families
# ---------------------------------------------------------------------------
class OpenAIModel:
    """Placeholder for an OpenAI-hosted model adapter.

    To implement: translate ModelRequest (system, Messages-API-style
    messages with tool_use/tool_result blocks, JSON-schema tools) into
    the provider's chat/tool format, translate the reply back into
    ModelResponse blocks, and report token usage for CostGuard. Keep the
    same prompts, tools and logging so results are comparable.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("OpenAIModel is a stub. See the docstring for what it needs.")


class OpenWeightsModel:
    """Placeholder for a locally served open-weights model (e.g. via a
    local inference server). Same contract as OpenAIModel. Open weights
    would allow internal-state analyses (e.g. probing activations) that
    API models do not."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("OpenWeightsModel is a stub. See the docstring for what it needs.")


def get_model(name: str, dry_run: bool, seed: int, guard: CostGuard, settings: dict):
    """Factory. --dry-run always returns MockModel, whatever --model says."""
    if dry_run:
        return MockModel(seed=seed, guard=guard)
    if name.startswith("claude-"):
        return AnthropicModel(
            name,
            guard,
            max_attempts=settings.get("max_attempts", 6),
            use_cache=settings.get("prompt_cache", True),
            thinking_display=settings.get("thinking_display", "omitted"),
        )
    if name.startswith("openai:"):
        return OpenAIModel(name)
    if name.startswith("local:"):
        return OpenWeightsModel(name)
    raise ValueError(f"Unknown model name: {name}")

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

Notes on API settings (public documentation checked 2026-10-15; see READINESS.md):
- Claude Haiku 5.5 and Sonnet 5.5 reject non-default sampling parameters,
  so no temperature is sent. Model sampling is therefore NOT seeded; the
  --seed only fixes the simulator (tasks, topology, agent order, targets).
- Adaptive thinking is explicitly enabled by this adapter. Thinking blocks
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
import math
from pathlib import Path
import os
import random
import time
from dataclasses import dataclass, field

# Direct Claude API global/standard prices, reverified 2026-10-15.
# Never infer an unknown model's price from another model.
PRICING = json.loads((Path(__file__).with_name("pricing.json")).read_text())
PRICES = PRICING["models"]
SDK_VERSION = "1.14.0"


class ModelCallFailed(RuntimeError):
    """Sanitized model failure safe to include in logs."""

    def __init__(self, stage: str, error_type: str, status_code: int | None = None):
        self.stage = stage
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(f"{stage}: {error_type}" + (f" HTTP {status_code}" if status_code else ""))


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
    """Conservative client-side budget accounting, not a billing guarantee.

    Ambiguous failed attempts keep their full reservation. Confirmed response
    costs replace only their own reservation. Mock estimation stays offline.
    """

    def __init__(self, max_usd: float):
        if not math.isfinite(max_usd) or max_usd <= 0:
            raise ValueError("max_cost_usd must be finite and positive")
        self.max_usd = max_usd
        self.spent_usd = 0.0
        self.uncertain_usd = 0.0
        self.calls = 0

    @staticmethod
    def estimate_input_tokens(req: ModelRequest) -> int:
        """Offline mock/forecast approximation; never used to authorize live calls."""
        chars = len(req.system) + len(json.dumps(req.messages, default=str)) + len(json.dumps(req.tools))
        return int(chars / 3) + 50

    @staticmethod
    def price(model: str, input_tokens: int, output_tokens: int, cache_read: int = 0, cache_write: int = 0) -> float:
        if model == "mock":
            return 0.0
        if model not in PRICES:
            raise ValueError(f"No verified price for model: {model}")
        p = PRICES[model]
        total = input_tokens + cache_read + cache_write
        long = total > p.get("long_threshold", math.inf)
        pin = p["long_input"] if long else p["input"]
        pout = p["long_output"] if long else p["output"]
        return (input_tokens * pin + cache_read * pin * p["cache_read_factor"]
                + cache_write * pin * p["cache_write_factor"] + output_tokens * pout) / 1_000_000

    def reserve(self, model: str, input_tokens: int, max_tokens: int, use_cache: bool) -> float:
        """Reserve a buffered count plus maximum output before EACH attempt."""
        buffered = input_tokens + max(math.ceil(input_tokens * 0.10), 1024)
        estimate = self.price(model, 0 if use_cache else buffered, max_tokens,
                              cache_write=buffered if use_cache else 0)
        if self.spent_usd + self.uncertain_usd + estimate > self.max_usd:
            raise CostLimitExceeded("Next attempt exceeds available budget including uncertain billing reservations.")
        self.uncertain_usd += estimate
        return estimate

    def add(self, model: str, usage: dict, reservation: float = 0.0) -> float:
        cost = self.price(model, usage.get("input_tokens", 0), usage.get("output_tokens", 0),
                          usage.get("cache_read_input_tokens", 0) or 0,
                          usage.get("cache_creation_input_tokens", 0) or 0)
        self.uncertain_usd = max(0.0, self.uncertain_usd - reservation)
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
                 thinking_display: str = "omitted", client=None):
        import anthropic  # imported here so --dry-run works without the SDK installed

        if anthropic.__version__ != SDK_VERSION:
            raise RuntimeError(f"Expected anthropic=={SDK_VERSION}")
        CostGuard.price(model, 0, 0)
        key = os.environ.get("ANTHROPIC_API_KEY")
        if client is None and not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Export it in your shell; do not put it in files.")
        self._anthropic = anthropic
        self._owns_client = client is None
        # SDK retries are disabled so that our own loop (below) controls and logs every retry.
        self.client = client if client is not None else anthropic.Anthropic(api_key=key, max_retries=0, timeout=300.0, base_url="https://api.anthropic.com")
        self.model = model
        self.guard = guard
        if max_attempts < 1 or thinking_display not in ("omitted", "summarized"):
            raise ValueError("Invalid retry or thinking-display configuration")
        self.max_attempts = max_attempts
        self.use_cache = use_cache
        self.thinking_display = thinking_display
        self.retry_log: list[dict] = []
        self.attempt_log: list[dict] = []
        self.event_callback = None

    def close(self) -> None:
        """Release adapter-owned connections; injected transports remain caller-owned."""
        if self._owns_client:
            self.client.close()

    def _event(self, kind: str, **payload) -> None:
        record = {"kind": kind, **payload}
        self.attempt_log.append(record)
        if self.event_callback:
            self.event_callback(record)

    def count_tokens(self, req: ModelRequest) -> int:
        """Non-generating count; failure never falls back to a character estimate."""
        try:
            count = self.client.messages.count_tokens(
                model=self.model, system=req.system, messages=req.messages, tools=req.tools,
                thinking={"type": "adaptive"})
            if count.input_tokens < 0:
                raise ValueError("Invalid token count")
            return count.input_tokens
        except Exception as e:
            raise ModelCallFailed("token_count", type(e).__name__, getattr(e, "status_code", None)) from None

    def respond(self, req: ModelRequest) -> ModelResponse:
        kwargs = dict(model=self.model, max_tokens=req.max_tokens, system=req.system,
                      messages=req.messages, tools=req.tools, output_config={"effort": req.effort},
                      thinking={"type": "adaptive", "display": self.thinking_display})
        if self.use_cache:
            kwargs["cache_control"] = {"type": "ephemeral"}
        input_tokens = self.count_tokens(req)
        delay = 2.0
        a = self._anthropic
        for attempt in range(1, self.max_attempts + 1):
            reservation = self.guard.reserve(self.model, input_tokens, req.max_tokens, self.use_cache)
            self._event("attempt_started", attempt=attempt, reservation_usd=reservation, meta=req.meta)
            t0 = time.time()
            try:
                resp = self.client.messages.create(**kwargs)
            except (a.APIStatusError, a.APIConnectionError) as e:
                status = getattr(e, "status_code", None)
                self._event("attempt_failed", attempt=attempt, error_type=type(e).__name__, status_code=status,
                            reservation_usd=reservation)
                retryable = isinstance(e, a.APIConnectionError) or status in self.RETRYABLE_STATUS
                if not retryable or attempt == self.max_attempts:
                    raise ModelCallFailed("generate", type(e).__name__, status) from None
                wait = min(_retry_after(e) or delay, 120.0)
                self.retry_log.append({"attempt": attempt, "wait_s": wait, "status_code": status})
                time.sleep(wait)
                delay = min(delay * 2, 120.0)
                continue
            except BaseException as e:
                # Keep reservation on interrupts or unclassified transport failures.
                self._event("attempt_failed", attempt=attempt, error_type=type(e).__name__, reservation_usd=reservation)
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                raise ModelCallFailed("generate", type(e).__name__) from None
            if resp.model != self.model:
                self._event("attempt_failed", attempt=attempt, error_type="UnexpectedReturnedModel",
                            returned_model=resp.model, reservation_usd=reservation)
                raise ModelCallFailed("model_identity", "UnexpectedReturnedModel")
            usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
                     "cache_read_input_tokens": getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
                     "cache_creation_input_tokens": getattr(resp.usage, "cache_creation_input_tokens", 0) or 0}
            usage["cost_usd"] = self.guard.add(self.model, usage, reservation)
            self._event("attempt_completed", attempt=attempt, cost_usd=usage["cost_usd"],
                        returned_model=resp.model, request_id=getattr(resp, "_request_id", None))
            if self.guard.spent_usd + self.guard.uncertain_usd > self.guard.max_usd:
                raise CostLimitExceeded("Returned usage exceeded the remaining estimate; stopped after accounting actual cost.")
            return ModelResponse(content=[b.model_dump(mode="json", exclude_none=True) for b in resp.content],
                                 stop_reason=resp.stop_reason, usage=usage, model=resp.model,
                                 response_id=resp.id, latency_s=round(time.time() - t0, 3))
        raise AssertionError("No request attempts configured")


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

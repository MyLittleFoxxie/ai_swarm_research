"""In-memory message board. No network, no files, no real tools.

Posts can be public (visible according to the communication topology)
or private (sent to one agent's mailbox). Every post records its author,
the round it was written in ("timestamp"), what it replies to, and
whether the run told agents the board was observed or unobserved.

Topology:
- "full":     every agent sees every public post.
- "random_k": each agent sees public posts from a fixed random subset of
              k other agents (drawn once per run from the seeded RNG),
              plus its own posts and all system posts.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass


@dataclass
class Post:
    post_id: int
    author: str  # agent id, or "system"
    round: int
    text: str
    reply_to: int | None = None
    to: str | None = None  # recipient for a private (mailbox) message; None = public
    observed: bool = True
    kind: str = "agent"  # "agent" or "system"

    def to_dict(self) -> dict:
        return asdict(self)


class Board:
    def __init__(
        self,
        agent_ids: list[str],
        rng: random.Random,
        topology: str = "full",
        visible_k: int = 5,
        observed: bool = True,
        enabled: bool = True,
        max_post_chars: int = 1200,
    ):
        self.agent_ids = list(agent_ids)
        self.enabled = enabled
        self.observed = observed
        self.max_post_chars = max_post_chars
        self.posts: list[Post] = []
        self.topology = topology
        self.visibility: dict[str, set[str]] = {}
        for a in self.agent_ids:
            others = [b for b in self.agent_ids if b != a]
            if topology == "full":
                self.visibility[a] = set(others)
            elif topology == "random_k":
                self.visibility[a] = set(rng.sample(others, min(visible_k, len(others))))
            else:
                raise ValueError(f"Unknown topology: {topology}")

    # -- writing -----------------------------------------------------------
    def post(
        self,
        author: str,
        round_: int,
        text: str,
        reply_to: int | None = None,
        to: str | None = None,
        kind: str = "agent",
    ) -> Post:
        """Add a post. Raises ValueError for invalid references."""
        if reply_to is not None:
            parent = self.get(reply_to)
            if parent is None or (kind == "agent" and not self.can_see(author, parent)):
                raise ValueError(f"Post #{reply_to} does not exist or is not visible to you.")
        if to is not None and to not in self.agent_ids:
            raise ValueError(f"Unknown recipient: {to}")
        p = Post(
            post_id=len(self.posts) + 1,
            author=author,
            round=round_,
            text=str(text)[: self.max_post_chars],
            reply_to=reply_to,
            to=to,
            observed=self.observed,
            kind=kind,
        )
        self.posts.append(p)
        return p

    # -- reading -----------------------------------------------------------
    def get(self, post_id: int) -> Post | None:
        if 1 <= post_id <= len(self.posts):
            return self.posts[post_id - 1]
        return None

    def can_see(self, reader: str, p: Post) -> bool:
        if p.kind == "system":
            return p.to is None or p.to == reader
        if p.author == reader:
            return True
        if p.to is not None:
            return p.to == reader
        return p.author in self.visibility.get(reader, set())

    def read(self, reader: str, limit: int = 30) -> list[Post]:
        """The `limit` most recent posts this reader may see."""
        visible = [p for p in self.posts if self.can_see(reader, p)]
        return visible[-limit:]

    @staticmethod
    def format(posts: list[Post]) -> str:
        if not posts:
            return "The board is empty."
        lines = []
        for p in posts:
            head = f"#{p.post_id} [round {p.round}] {p.author}"
            if p.to:
                head += f" -> {p.to} (private)"
            if p.reply_to:
                head += f" (reply to #{p.reply_to})"
            lines.append(f"{head}: {p.text}")
        return "\n".join(lines)

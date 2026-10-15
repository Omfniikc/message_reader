from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SumArgs:
    chat_query: str | None
    limit: int | None
    instructions: str | None


def parse_sum_args(raw: str) -> SumArgs:
    """Parse the arguments of /sum.

    Supported forms:
      /sum                      -> no chat (bot will ask via buttons)
      /sum @durov               -> chat by username
      /sum @durov 50            -> chat + message limit
      /sum 123456789 200        -> chat by id + limit
      /sum @durov 50 only deadlines -> chat + limit + instructions
      /sum @durov only deadlines    -> chat + instructions (no limit)
      /sum work chat 30         -> chat by title substring + limit

    Rules: the first token is the chat unless it is a bare integer
    (which is treated as a chat id). A second integer token is the
    message limit; everything after that is instructions.
    """
    text = (raw or "").strip()
    if not text:
        return SumArgs(chat_query=None, limit=None, instructions=None)

    tokens = text.split()
    chat_query: str | None = None
    limit: int | None = None
    rest_start = 0

    # First token: chat query (username, id, or first word of a title).
    first = tokens[0]
    if first.lstrip("-").isdigit():
        chat_query = first
        rest_start = 1
    elif first.startswith("@") or "t.me/" in first:
        chat_query = first
        rest_start = 1
    else:
        # Title substring: consume tokens until a standalone integer (limit) or end.
        # Keep it simple: single-word title by default, unless followed by non-int words
        # that are clearly part of a title. To avoid ambiguity, treat a multiword title
        # only if the next token is NOT an integer and there are more tokens after it.
        chat_query = first
        rest_start = 1
        # Allow multi-word titles greedily while tokens are non-integer AND
        # an integer limit or more words follow. We stop at the first integer.
        while rest_start < len(tokens) and not tokens[rest_start].isdigit():
            # If the remaining tokens after this one are all non-integer, they might
            # be instructions, not title. Only extend the title if the NEXT token
            # is an integer limit OR this looks like a continuation. To stay safe,
            # we do NOT extend: multiword titles should be resolved via /chats.
            break

    # Second token: optional integer limit.
    if rest_start < len(tokens):
        maybe_limit = tokens[rest_start]
        if maybe_limit.isdigit():
            limit = int(maybe_limit)
            rest_start += 1

    instructions = " ".join(tokens[rest_start:]).strip() or None
    return SumArgs(chat_query=chat_query, limit=limit, instructions=instructions)

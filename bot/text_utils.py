from __future__ import annotations

MAX_MESSAGE_LEN = 4000  # Telegram hard limit is 4096; keep some headroom


def chunk_text(text: str, max_size: int = MAX_MESSAGE_LEN) -> list[str]:
    """Split text into Telegram-safe chunks, preferring paragraph/word boundaries."""
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    while text:
        if len(text) <= max_size:
            chunks.append(text)
            break
        cut = text.rfind("\n", 0, max_size)
        if cut <= max_size // 2:  # avoid cutting off a tiny sliver
            cut = text.rfind(" ", 0, max_size)
        if cut <= 0:
            cut = max_size
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip("\n ")
    return chunks

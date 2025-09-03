import re
from typing import List


def _hard_wrap(text: str, max_len: int) -> List[str]:
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i : i + max_len]
        chunks.append(chunk)
        i += max_len
    return chunks


def split_text(text: str, max_tokens: int = 512, overlap: int = 64) -> List[str]:
    # token-approximate by characters; simple MVP
    t = text.strip()
    if not t:
        return []
    step = max(1, max_tokens - overlap)
    chunks = []
    i = 0
    while i < len(t):
        chunk = t[i : i + max_tokens]
        chunks.append(chunk)
        i += step
    return chunks


def split_markdown(md: str, max_tokens: int = 512, overlap: int = 64) -> List[str]:
    # naive: split by headings, then wrap
    parts = re.split(r"\n(?=#+\s)", md)
    chunks: List[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= max_tokens:
            chunks.append(part)
        else:
            chunks.extend(split_text(part, max_tokens=max_tokens, overlap=overlap))
    return chunks


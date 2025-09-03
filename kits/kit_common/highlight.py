from typing import List, Tuple


def make_snippet(text: str, query: str, window: int = 180) -> tuple[str, List[Tuple[int, int]]]:
    """
    Build a lightweight snippet around first query match and return
    highlight ranges relative to the snippet.
    """
    if not text:
        return "", []
    q = (query or "").strip()
    if not q:
        snippet = text[: window * 2]
        return snippet, []
    lowered = text.lower()
    q_lower = q.lower()
    idx = lowered.find(q_lower)
    if idx == -1:
        # fallback: just head of text
        snippet = text[: window * 2]
        return snippet, []
    start = max(0, idx - window)
    end = min(len(text), idx + len(q) + window)
    snippet = text[start:end]
    rel = idx - start
    highlights = [(rel, rel + len(q))]
    return snippet, highlights


import os
from typing import List, Tuple

from .deps import state
from kits.kit_common.highlight import make_snippet


def retrieve(query: str, top_k: int | None = None):
    k = top_k or int(os.getenv("RAG_TOP_K", "5"))
    docs = state.faiss.similarity_search_with_score(query, k=k)
    sources = []
    for i, (doc, score) in enumerate(docs):
        snippet, hl = make_snippet(doc.page_content, query)
        sources.append({
            "id": f"d{i}",
            "score": score_to_similarity(score),
            "filename": doc.metadata.get("filename", ""),
            "page": doc.metadata.get("page", 1) or 1,
            "snippet": snippet,
            "highlights": hl,
        })
    return sources


def score_to_similarity(distance: float) -> float:
    try:
        return 1.0 / (1.0 + float(distance))
    except Exception:
        return 0.0


def compute_confidence(sources: List[dict]) -> float:
    if not sources:
        return 0.0
    vals = [float(s.get("score", 0.0)) for s in sources]
    return sum(vals) / max(1, len(vals))


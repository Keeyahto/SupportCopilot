import types
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings


class DummyEmbed(Embeddings):
    def embed_documents(self, texts):
        return [[float(len(t))] for t in texts]

    def embed_query(self, text):
        return [float(len(text))]


def test_retrieve_and_confidence(monkeypatch):
    from apps.api import deps, rag

    # Build tiny FAISS with dummy embedder
    embed = DummyEmbed()
    vs = FAISS.from_texts(["возвраты товар в 14 дней", "доставка 2-5 дней"], embed)

    deps.state.embedder = embed
    deps.state.faiss = vs
    deps.state.faiss_ready = True

    sources = rag.retrieve("возвраты")
    assert sources and all("snippet" in s for s in sources)
    conf = rag.compute_confidence(sources)
    assert 0 <= conf <= 1


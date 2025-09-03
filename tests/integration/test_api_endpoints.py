from fastapi.testclient import TestClient


class FakeStream:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        class C:  # minimal chunk with delta
            class Choice:
                class Delta:
                    content = "hi"

                delta = Delta()

            choices = [Choice()]

        yield C()


class FakeOpenAI:
    class Chat:
        class Completions:
            def create(self, **kwargs):
                class Resp:
                    class Choice:
                        class Message:
                            content = "stub answer"

                        message = Message()

                    choices = [Choice()]

                return Resp()

            def stream(self, **kwargs):
                return FakeStream()

        completions = Completions()

    chat = Chat()


def setup_app(monkeypatch):
    from apps.api import deps, main
    # Patch state with fake client and tiny FAISS
    from langchain_community.vectorstores import FAISS
    from langchain_core.embeddings import Embeddings

    class DummyEmbed(Embeddings):
        def embed_documents(self, texts):
            return [[float(len(t))] for t in texts]

        def embed_query(self, text):
            return [float(len(text))]

    embed = DummyEmbed()
    vs = FAISS.from_texts(["правила возврата 14 дней", "доставка 2-5 дней"], embed)

    # prevent real startup init
    monkeypatch.setattr(main, "init_clients", lambda: None)
    
    # Mock call_tools_api directly in main module
    async def fake_call_tools_api(intent: str, clean_text: str) -> dict:
        return {"name": "shipping.eta", "data": {"eta_days": 3}, "ok": True}
    
    monkeypatch.setattr(main, "call_tools_api", fake_call_tools_api)

    deps.state.client = FakeOpenAI()
    deps.state.embedder = embed
    deps.state.faiss = vs
    deps.state.faiss_ready = True

    return main.app


def test_health(monkeypatch):
    app = setup_app(monkeypatch)
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert "faiss_ready" in r.json()


def test_chat_rag(monkeypatch):
    app = setup_app(monkeypatch)
    client = TestClient(app)
    r = client.post("/chat", json={"text": "как вернуть товар?", "mode": "faq", "strict": False, "lang": "ru"})
    assert r.status_code == 200
    j = r.json()
    assert "answer" in j and j["labels"]


def test_chat_stream_basic(monkeypatch):
    app = setup_app(monkeypatch)
    client = TestClient(app)
    with client.stream("POST", "/chat/stream", json={"text": "доставка в 101000", "mode": "faq", "strict": False, "lang": "ru"}) as r:
        assert r.status_code == 200
        # event-stream content-type
        assert "text/event-stream" in r.headers.get("content-type", "")

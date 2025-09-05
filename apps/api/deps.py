import os
import time
import logging
from pathlib import Path
from typing import Optional, List

from openai import OpenAI
from redis import Redis
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS

from kits.kit_common import normalize_text
from kits.kit_chunker import split_markdown, split_text


logger = logging.getLogger(__name__)


class STEmbedding:
    def __init__(self, model: str):
        self.m = SentenceTransformer(model)

    def embed_documents(self, texts: List[str]):
        return self.m.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str):
        return self.m.encode([text], normalize_embeddings=True)[0].tolist()

    # Some vectorstore constructors (older/newer variants) expect a callable
    # instead of an Embeddings interface. Make the instance callable and
    # delegate to embed_query to be compatible with both forms.
    def __call__(self, text: str):
        return self.embed_query(text)


class AppState:
    client: Optional[OpenAI] = None
    redis: Optional[Redis] = None
    faiss: Optional[FAISS] = None
    embedder: Optional[STEmbedding] = None
    faiss_ready: bool = False
    metrics: dict = {
        "tool_calls": 0,
        "db_queries": 0,
        "rag_queries": 0,
        "deflection_rate": 0.0,
        "avg_confidence": 0.0,
    }


state = AppState()


def init_clients():
    # Load .env from repo root if present (best-effort)
    try:
        from dotenv import load_dotenv  # type: ignore
        repo_root = Path(__file__).resolve().parents[2]
        env_path = repo_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded .env from %s", env_path)
    except Exception as e:
        logger.debug("dotenv not loaded: %s", e)
    # LLM client
    state.client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )
    # Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    state.redis = Redis.from_url(redis_url, decode_responses=True)

    # Embeddings + FAISS
    embed_model = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    state.embedder = STEmbedding(embed_model)

    _ensure_faiss_index()


def _ensure_faiss_index():
    # Для локальной разработки используем относительные пути
    repo_root = Path(__file__).resolve().parents[2]
    rel_faiss = repo_root / "data/copilot/faiss"
    rel_faq = repo_root / "data/copilot/faq"
    abs_faiss = Path("/app/data/copilot/faiss")
    abs_faq = Path("/app/data/copilot/faq")
    faiss_dir_env = os.getenv("FAISS_DIR")
    if faiss_dir_env:
        # If env points to container path but we're local, fall back to repo-relative
        if faiss_dir_env.startswith("/app/") and not abs_faq.exists():
            faiss_dir = rel_faiss
        else:
            faiss_dir = Path(faiss_dir_env)
        faq_dir = rel_faq if rel_faq.exists() else abs_faq
    else:
        if abs_faq.exists() or abs_faiss.exists():
            faiss_dir = abs_faiss
            faq_dir = abs_faq
        else:
            faiss_dir = rel_faiss
            faq_dir = rel_faq
    Path(faiss_dir).mkdir(parents=True, exist_ok=True)
    logger.info("FAISS using faiss_dir=%s, faq_dir=%s", faiss_dir, faq_dir)
    logger.info("FAISS using faiss_dir=%s, faq_dir=%s", faiss_dir, faq_dir)

    try:
        force_rebuild = os.getenv("FAISS_FORCE_REBUILD", "false").lower() == "true"
        if (not force_rebuild) and any(Path(faiss_dir).iterdir()):
            state.faiss = FAISS.load_local(faiss_dir, state.embedder, allow_dangerous_deserialization=True)
            state.faiss_ready = True
            logger.info("FAISS index loaded from %s (force_rebuild=%s)", faiss_dir, force_rebuild)
            return
    except Exception as e:
        logger.warning("FAISS load failed, will rebuild: %s", e)

    # Build index from scratch
    texts = []
    metadatas = []
    max_tokens = int(os.getenv("CHUNK_MAX_TOKENS", "512"))
    overlap = int(os.getenv("CHUNK_OVERLAP", "64"))

    if faq_dir.exists():
        for p in faq_dir.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in {".md", ".txt"}:
                raw = p.read_text(encoding="utf-8", errors="ignore")
                clean = normalize_text(raw)
                chunks = split_markdown(clean, max_tokens, overlap) if p.suffix.lower() == ".md" else split_text(clean, max_tokens, overlap)
                for ch in chunks:
                    texts.append(ch)
                    metadatas.append({"filename": p.name, "path": str(p)})
            # PDF support omitted for MVP; can be added with pypdf

    if not texts:
        # ensure non-empty index
        texts = ["Добро пожаловать в базу знаний Support Copilot."]
        metadatas = [{"filename": "welcome.txt", "path": str(faq_dir / "welcome.txt")}]

    logger.info("Building FAISS index with %d chunks", len(texts))
    t0 = time.time()
    vs = FAISS.from_texts(texts=texts, embedding=state.embedder, metadatas=metadatas)
    vs.save_local(faiss_dir)
    state.faiss = vs
    state.faiss_ready = True
    logger.info("FAISS built in %.2fs", time.time() - t0)

import os
import sys
from types import SimpleNamespace


# Ensure repo root on path
ROOT = os.path.abspath(os.getcwd())
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def pytest_configure():
    # Minimal env for tests
    os.environ.setdefault("TESTING", "true")
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("OPENAI_API_KEY", "sk-test")
    os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:9999/v1")
    os.environ.setdefault("CHAT_MODEL", "gpt-4o-mini")
    os.environ.setdefault("EMBED_MODEL", "dummy-model")
    os.environ.setdefault("FAISS_DIR", "/tmp/faiss-test")
    os.environ.setdefault("RAG_TOP_K", "3")
    os.environ.setdefault("ADMIN_PIN", "123456")
    os.environ.setdefault("DB_URL", "postgresql+psycopg2://support_ro:readonly@localhost:5432/support")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


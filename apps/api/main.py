import os
import json
import logging
from typing import Optional

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .deps import init_clients, state
from .models import ChatRequest, ChatResponse, Source, Metrics, ToolInfo
from .router import pii_filter
from .rag import retrieve, compute_confidence
from .generators import llm_answer, llm_stream_answer, sse_from_generator
from .db_tool import db_tool_query
from .agentic import run_agentic
from .admin_api import (
    get_orders,
    get_order,
    update_order,
    get_customers,
    get_products,
    get_admin_stats,
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(title="Support Copilot API")

# CORS: allow frontend dev server (3000) and configurable origins
_origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
origins = [o.strip() for o in _origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*", "X-Admin-Key", "X-Session-ID"],
)


@app.on_event("startup")
def on_startup():
    init_clients()


def _public_tool_info(tool_info: Optional[dict]) -> Optional[dict]:
    if not tool_info:
        return None
    name = tool_info.get("name")
    sql = tool_info.get("sql")
    return {"name": name, "sql": sql}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": os.getenv("APP_ENV", "local"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL"),
        "chat_model": os.getenv("CHAT_MODEL"),
        "embed_model": os.getenv("EMBED_MODEL"),
        "faiss_ready": bool(state.faiss_ready),
    }


@app.post("/chat")
async def chat(request: ChatRequest, x_session_id: Optional[str] = Header(None), x_admin_key: Optional[str] = Header(None)):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    clean = pii_filter(request.text)

    _ans, sources, labels, tool_info = run_agentic(clean, bool(is_admin))
    answer = llm_answer(clean, sources, tool_info)

    metrics = Metrics(confidence=compute_confidence(sources))
    resp = ChatResponse(
        answer=answer,
        sources=[Source(**s) for s in sources],
        labels=labels,
        metrics=metrics,
        tool_info=ToolInfo(**_public_tool_info(tool_info)) if tool_info else None,
    )
    return JSONResponse(json.loads(resp.json()))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, x_session_id: Optional[str] = Header(None), x_admin_key: Optional[str] = Header(None)):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    clean = pii_filter(request.text)

    _ans, sources, labels, tool_info = run_agentic(clean, bool(is_admin))
    gen = llm_stream_answer(clean, sources, tool_info, labels)
    return sse_from_generator(gen)


@app.get("/metrics")
def metrics():
    return state.metrics


# Admin API endpoints
@app.get("/admin/orders")
async def admin_orders(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    x_admin_key: Optional[str] = Header(None)
):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    if not is_admin:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return get_orders(status, limit, offset)


@app.get("/admin/orders/{order_id}")
async def admin_order_detail(order_id: int, x_admin_key: Optional[str] = Header(None)):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    if not is_admin:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return get_order(order_id)


@app.put("/admin/orders/{order_id}")
async def admin_update_order(
    order_id: int,
    request: dict,
    x_admin_key: Optional[str] = Header(None)
):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    if not is_admin:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return update_order(order_id, request)


@app.get("/admin/customers")
async def admin_customers(
    limit: int = 50,
    offset: int = 0,
    x_admin_key: Optional[str] = Header(None)
):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    if not is_admin:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return get_customers(limit, offset)


@app.get("/admin/products")
async def admin_products(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    x_admin_key: Optional[str] = Header(None)
):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    if not is_admin:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return get_products(category, limit, offset)


@app.get("/admin/stats")
async def admin_stats(x_admin_key: Optional[str] = Header(None)):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    if not is_admin:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return get_admin_stats()

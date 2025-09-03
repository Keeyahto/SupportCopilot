import os
import json
import logging
from typing import Optional

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .deps import init_clients, state
from .models import ChatRequest, ChatResponse, Source, Metrics, ToolInfo
from .router import pii_filter, route_intent
from .rag import retrieve, compute_confidence
from .generators import llm_answer, llm_stream_answer, sse_from_generator
from .tools_client import call_tools_api
from .db_tool import db_tool_query


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

# Do not enable GZip to avoid interfering with SSE


@app.on_event("startup")
def on_startup():
    init_clients()


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
    intent = route_intent(clean, request.mode, bool(is_admin))

    sources = []
    labels = []
    tool_info = None

    if intent == "db_analytics" and is_admin:
        try:
            tool_info = db_tool_query(clean)
            labels.extend(["DB Tool"])
        except Exception as e:
            logger.warning("DB tool unavailable: %s", e)
            tool_info = None
        sources = retrieve(clean, top_k=int(os.getenv("RAG_TOP_K", "5")))
        labels.append("RAG")
        answer = llm_answer(clean, sources, tool_info)
    elif intent in ["order_status", "plan_price", "delivery_eta"]:
        tool_result = None
        try:
            tool_result = await call_tools_api(intent, clean)
        except Exception as e:
            logger.warning("Tools API call failed: %s", e)
            tool_result = {"name": intent, "data": {}, "ok": False}
        if tool_result.get("ok"):
            labels.extend(["Tool-call"]) 
        sources = retrieve(clean, top_k=int(os.getenv("RAG_TOP_K", "5")))
        labels.append("RAG")
        tool_info = {"name": tool_result.get("name"), "rows": None, "summary": None}
        answer = llm_answer(clean, sources, tool_result)
    else:
        sources = retrieve(clean, top_k=int(os.getenv("RAG_TOP_K", "5")))
        conf = compute_confidence(sources)
        if request.mode == "policies" and conf < 0.4:
            answer = "Недостаточно данных. Могу завести тикет?"
            labels.append("Escalation")
        else:
            answer = llm_answer(clean, sources)
            labels.append("RAG")

    metrics = Metrics(confidence=compute_confidence(sources))
    resp = ChatResponse(
        answer=answer,
        sources=[Source(**s) for s in sources],
        labels=labels,
        metrics=metrics,
        tool_info=ToolInfo(**tool_info) if tool_info else None,
    )
    return JSONResponse(json.loads(resp.json()))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, x_session_id: Optional[str] = Header(None), x_admin_key: Optional[str] = Header(None)):
    is_admin = x_admin_key and (x_admin_key == os.getenv("ADMIN_PIN"))
    clean = pii_filter(request.text)
    intent = route_intent(clean, request.mode, bool(is_admin))

    if intent == "db_analytics" and is_admin:
        try:
            tool_info = db_tool_query(clean)
        except Exception as e:
            async def err_gen():
                yield {"event": "error", "data": json.dumps({"message": f"DB Tool unavailable: {str(e)}"})}
            return sse_from_generator(err_gen())
        sources = retrieve(clean, top_k=int(os.getenv("RAG_TOP_K", "5")))
        gen = llm_stream_answer(clean, sources, tool_info)
        return sse_from_generator(gen)
    elif intent in ["order_status", "plan_price", "delivery_eta"]:
        try:
            tool_result = await call_tools_api(intent, clean)
        except Exception as e:
            async def err_gen():
                yield {"event": "error", "data": json.dumps({"message": f"Tool-call failed: {str(e)}"})}
            return sse_from_generator(err_gen())
        sources = retrieve(clean, top_k=int(os.getenv("RAG_TOP_K", "5")))
        gen = llm_stream_answer(clean, sources, tool_result)
        return sse_from_generator(gen)
    else:
        sources = retrieve(clean, top_k=int(os.getenv("RAG_TOP_K", "5")))
        gen = llm_stream_answer(clean, sources, None)
        return sse_from_generator(gen)


@app.get("/metrics")
def metrics():
    return state.metrics

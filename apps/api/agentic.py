import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .deps import state
from .rag import retrieve
from .customer_tools import order_status_tool
from .db_tool import db_tool_query


# DB execution is delegated to db_tool_query (schema-aware, with retry)


def _tools_schema(is_admin: bool) -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "rag_read",
                "description": "По вопросу пользователя найти релевантные фрагменты документации (RAG) и вернуть их в виде источников.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Вопрос пользователя"},
                        "top_k": {"type": "integer", "description": "Сколько источников вернуть", "default": 5},
                    },
                    "required": ["question"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "orders_status",
                "description": "Получить статус заказа по его номеру, например A1001.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_no": {"type": "string", "description": "Номер заказа, напр. A1001"},
                    },
                    "required": ["order_no"],
                },
            },
        },
    ]
    if is_admin:
        tools.append({
            "type": "function",
            "function": {
                "name": "db_analytics_query",
                "description": "Сформулировать аналитический запрос к БД (естественным языком). Агент сам построит безопасный SELECT по схеме и выполнит его.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Аналитический вопрос на естественном языке"},
                    },
                    "required": ["question"],
                },
            },
        })
    return tools


def run_agentic(question: str, is_admin: bool) -> Tuple[str, List[dict], List[str], Optional[dict]]:
    """Runs an agentic tool-calling loop using OpenAI tools.
    Returns: (final_answer, sources, labels, tool_info)
    """
    client = state.client
    model = os.getenv("CHAT_MODEL")
    tools = _tools_schema(is_admin)

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Ты ассистент поддержки. Доступные инструменты:\n"
                "- rag_read(question, top_k): найти релевантные фрагменты документации (RAG).\n"
                "- orders_status(order_no): статус конкретного заказа.\n"
                "- db_analytics_query(sql): аналитический SQL (ТОЛЬКО SELECT, ТОЛЬКО для админа).\n\n"
                "Правила выбора инструментов:\n"
                "1) Информационные/политики/FAQ — сперва вызови rag_read, затем отвечай на основе источников.\n"
                "2) Про конкретный заказ — вызови orders_status.\n"
                "3) Агрегации/метрики по БД (и если есть права) — db_analytics_query (SELECT).\n"
                "Отвечай после того, как получишь данные инструментов. Если инструмент не нужен, отвечай сразу."
            ),
        },
        {"role": "user", "content": question},
    ]

    labels: List[str] = []
    sources: List[dict] = []
    tool_info: Optional[dict] = None

    executed: set[str] = set()
    for _ in range(3):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = resp.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls:
            # No more tools; accept this as final reasoning but we will craft final answer with our template
            break

        # Execute tools in order
        # 1) Append assistant message that requested tool calls
        try:
            tc_payload = []
            for tc in tool_calls:
                tc_payload.append({
                    "id": getattr(tc, "id", None),
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments or "{}",
                    },
                })
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": tc_payload,
            })
        except Exception:
            # non-fatal; proceed with tool messages only
            pass

        # 2) Run tools and append tool outputs
        for tc in tool_calls:
            name = tc.function.name
            if name in executed:
                continue
            args = {}
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}

            if name == "rag_read":
                q = args.get("question") or question
                top_k = int(args.get("top_k") or int(os.getenv("RAG_TOP_K", "5")))
                sources = retrieve(q, top_k=top_k)
                labels.append("RAG")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps({"sources": sources}, ensure_ascii=False, default=str),
                })
            elif name == "orders_status":
                order_no = (args.get("order_no") or "").strip()
                ti = order_status_tool(f"#{order_no}" if order_no else question)
                # prefer the most impactful tool_info (orders/status or db)
                tool_info = ti
                labels.append("Tool-call")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps(ti, ensure_ascii=False, default=str),
                })
            elif name == "db_analytics_query" and is_admin:
                q = (args.get("question") or question).strip()
                ti = db_tool_query(q)
                tool_info = ti
                labels.append("DB Tool")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps(ti, ensure_ascii=False, default=str),
                })
                executed.add(name)
                # let the model finalize using tool results (don't immediately break outer loop)
            else:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps({"error": "tool_not_available"}, ensure_ascii=False, default=str),
                })
            executed.add(name)

        # loop continues for potential follow-up tool calls

    # Safety fallback: if модель не вызвала rag_read и других tools нет, подгрузи контекст для ответа
    if not sources and not tool_info:
        try:
            sources = retrieve(question, top_k=int(os.getenv("RAG_TOP_K", "5")))
            if sources:
                labels.append("RAG")
        except Exception:
            pass

    # Final answer text will be produced by our answer generator using sources + tool_info
    # dedupe labels preserve order
    seen = set()
    labels_unique = []
    for l in labels:
        if l not in seen:
            labels_unique.append(l)
            seen.add(l)
    final_answer = ""
    return final_answer, sources, labels_unique, tool_info

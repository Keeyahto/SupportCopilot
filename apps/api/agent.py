import os
import re
from typing import Literal, List

from .deps import state


ToolDecision = Literal["none", "orders_status", "db_analytics", "rag_read"]


def plan_tools(question: str, is_admin: bool) -> List[ToolDecision]:
    """Decide which tools to call: orders status (public), DB analytics (admin), RAG read, or none.
    Returns a list of tool decisions (0..n). Typical cases:
      - ["orders_status"]
      - ["db_analytics", "rag_read"]
      - ["rag_read"]
      - [] (means none)
    """
    decisions: List[ToolDecision] = []

    # Heuristic: explicit order number marker like #A123 → orders status
    if re.search(r"#\w+", question):
        decisions.append("orders_status")

    # Decide on DB analytics for admins only
    if is_admin:
        prompt = (
            "Ты ассистент поддержки с доступом к инструменту аналитики БД (только SELECT).\n"
            "Реши, нужен ли вызов БД, чтобы ответить на вопрос.\n"
            "Ответ строго одним словом: DB_ANALYTICS или NONE."
        )
        resp = state.client.chat.completions.create(
            model=os.getenv("CHAT_MODEL"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question},
            ],
            temperature=0,
        )
        decision = (resp.choices[0].message.content or "").strip().upper()
        if decision.startswith("DB_ANALYTICS"):
            decisions.append("db_analytics")

    # RAG read: default tool for most informational questions unless we already have orders_status only
    # If the question clearly requested order status and nothing else, RAG is optional; otherwise include it
    if not decisions or any(d in ("db_analytics",) for d in decisions):
        decisions.append("rag_read")

    return decisions

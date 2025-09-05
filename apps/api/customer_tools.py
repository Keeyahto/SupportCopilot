import os
import re
from typing import Dict, Any, Optional

from sqlalchemy import create_engine, text


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("DB_URL")
        if not db_url:
            raise RuntimeError("DB_URL is not set")
        _engine = create_engine(db_url)
    return _engine


def extract_order_no(text: str) -> Optional[str]:
    m = re.search(r"#(\w+)", text)
    return m.group(1) if m else None


def order_status_tool(question: str) -> Dict[str, Any]:
    """Public tool: looks up order by number and returns limited info.
    Returns a ToolInfo-like dict compatible with frontend and llm prompt.
    """
    order_no = extract_order_no(question)
    if not order_no:
        return {"name": "orders.status", "rows": [], "summary": "Не найден номер заказа в вопросе"}

    eng = _get_engine()
    with eng.connect() as conn:
        row = conn.execute(text(
            """
            SELECT o.order_no, o.status, o.total, c.email, c.city
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.order_no = :order_no
            """
        ), {"order_no": order_no}).mappings().first()

    if not row:
        return {"name": "orders.status", "rows": [], "summary": "Заказ не найден"}

    return {
        "name": "orders.status",
        "rows": [{
            "order_no": row["order_no"],
            "status": row["status"],
            "total": float(row["total"]) if row["total"] is not None else 0.0,
            "customer_email": row["email"],
            "customer_city": row["city"],
        }],
        "summary": "Информация о заказе получена",
    }


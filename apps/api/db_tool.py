import os
import re
from time import time
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime, time as dtime
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .deps import state


_engine = None
_schema_cache: Optional[str] = None


def _jsonify_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (int, float, bool)):
        return v
    if isinstance(v, Decimal):
        try:
            return float(v)
        except Exception:
            return str(v)
    if isinstance(v, (datetime, date, dtime)):
        return v.isoformat()
    if isinstance(v, UUID):
        return str(v)
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8", errors="replace")
        except Exception:
            return str(v)
    return v if isinstance(v, (list, dict)) else str(v)


def safe_sql(sql: str) -> str:
    s = (sql or "").strip().strip(";")
    # allow SELECT or CTE (WITH ... SELECT)
    if not re.match(r"^\s*(select|with)\s", s, flags=re.IGNORECASE):
        # try to coerce by cutting everything before first SELECT/WITH
        m = re.search(r"\b(select|with)\b", s, flags=re.IGNORECASE)
        if m:
            s = s[m.start():]
        else:
            raise ValueError("Only SELECT queries are allowed")
    # forbid dangerous keywords (word-boundary to avoid 'updated_at')
    # strip any semicolons defensively (keep single-statement)
    s = re.sub(r";+", "", s)
    sl = s.lower()
    banned_patterns = [r"\bdrop\b", r"\bdelete\b", r"\bupdate\b", r"\binsert\b", r"\balter\b", r"\bcreate\b"]
    if any(re.search(p, sl) for p in banned_patterns):
        raise ValueError("Dangerous SQL detected")
    # add LIMIT if absent
    if not re.search(r"\blimit\b", sl):
        s += " LIMIT 500"
    return s


def extract_sql(question: str) -> str:
    # Ask LLM to produce a single-line SQL SELECT statement for PostgreSQL
    prompt = (
        "Ты помощник по аналитике БД. Твоя задача — составить один корректный SQL SELECT для PostgreSQL. "
        "Ограничения: только SELECT (никаких INSERT/UPDATE/DELETE/DDL), никаких точек с запятой, без бэктиков. "
        "Опирайся на схему БД ниже и используй только существующие таблицы/поля."
    )
    schema = get_db_schema()
    resp = state.client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "system", "content": f"Схема БД (public):\n{schema}"},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return _coerce_to_sql(raw)


def extract_sql_strict(question: str) -> str:
    prompt = (
        "Выведи только один корректный SQL SELECT (PostgreSQL) без пояснений и без бэктиков. "
        "Никакого текста вокруг. Только запрос."
    )
    schema = get_db_schema()
    resp = state.client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "system", "content": f"Схема БД (public):\n{schema}"},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return _coerce_to_sql(raw)


def _coerce_to_sql(text: str) -> str:
    t = (text or "").strip()
    # strip code fences and leading language markers
    t = re.sub(r"^```+\s*sql\s*|^```+|```+$", "", t, flags=re.IGNORECASE).strip()
    # cut everything before first SELECT/WITH
    m = re.search(r"\b(select|with)\b", t, flags=re.IGNORECASE)
    if m:
        t = t[m.start():]
    # drop anything after first non-ASCII char (e.g., accidental commentary in RU/CN, etc.)
    m2 = re.search(r"[^\x00-\x7F]", t)
    if m2:
        t = t[:m2.start()].strip()
    # also drop trailing common commentary markers if any leaked in
    t = re.split(r"\b(Ошибка|Error|Note|Примечание)\b", t, maxsplit=1)[0].strip()
    # final cleanup of stray backticks or trailing dots
    t = t.strip("` ")
    t = re.sub(r"\.+\s*$", "", t)
    return t


def summarize_rows(rows: List[Dict[str, Any]]) -> str:
    body = str(rows[:5]) if rows else "Пустой результат"
    resp = state.client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": "Сделай краткое русскоязычное резюме набора строк БД."},
            {"role": "user", "content": f"Строки: {body}"},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


def db_tool_query(question: str) -> dict:
    # rely on caller for admin checks
    t0 = time()
    rows: List[Dict[str, Any]] = []
    sql_used = ""
    global _engine
    if _engine is None:
        db_url = os.getenv("DB_URL")
        if not db_url:
            raise RuntimeError("DB_URL is not set")
        _engine = create_engine(db_url)

    try:
        sql = extract_sql(question)
        sql = safe_sql(sql)
        with _engine.connect() as conn:
            result = conn.execute(text(sql))
            cols = result.keys()
            for r in result.fetchall():
                row_obj = {c: (getattr(r, c) if hasattr(r, c) else r[i]) for i, c in enumerate(cols)}
                rows.append({k: _jsonify_value(v) for k, v in row_obj.items()})
        sql_used = sql
    except Exception as e1:
        try:
            # Try strict extraction
            sql = extract_sql_strict(question)
            sql = safe_sql(sql)
            with _engine.connect() as conn:
                result = conn.execute(text(sql))
                cols = result.keys()
                for r in result.fetchall():
                    row_obj = {c: (getattr(r, c) if hasattr(r, c) else r[i]) for i, c in enumerate(cols)}
                    rows.append({k: _jsonify_value(v) for k, v in row_obj.items()})
            sql_used = sql
        except Exception as e2:
            try:
                # Last try: repair based on error
                sql = extract_sql_with_error(question, f"{e1}")
                sql = safe_sql(sql)
                with _engine.connect() as conn:
                    result = conn.execute(text(sql))
                    cols = result.keys()
                    for r in result.fetchall():
                        row_obj = {c: (getattr(r, c) if hasattr(r, c) else r[i]) for i, c in enumerate(cols)}
                        rows.append({k: _jsonify_value(v) for k, v in row_obj.items()})
                sql_used = sql
            except Exception as e3:
                # Return graceful error info
                latency = int((time() - t0) * 1000)
                state.metrics["db_queries"] = state.metrics.get("db_queries", 0) + 1
                return {
                    "name": "db_analytics.query",
                    "sql": sql_used or "",
                    "rows": [],
                    "summary": f"Ошибка SQL: {str(e3)}",
                    "latency_ms": latency,
                }

    latency = int((time() - t0) * 1000)
    state.metrics["db_queries"] = state.metrics.get("db_queries", 0) + 1
    return {
        "name": "db_analytics.query",
        "sql": sql_used,
        "rows": rows[:20],
        "summary": None,
        "latency_ms": latency,
    }


def get_db_schema() -> str:
    """Return cached public schema description (tables and columns)."""
    global _schema_cache, _engine
    if _schema_cache:
        return _schema_cache
    if _engine is None:
        db_url = os.getenv("DB_URL")
        if not db_url:
            return default_schema_hint()
        _engine = create_engine(db_url)
    try:
        q = text(
            """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
        )
        rows = []
        with _engine.connect() as conn:
            res = conn.execute(q)
            for r in res:
                rows.append((r[0], r[1], r[2]))
        tables: Dict[str, List[str]] = {}
        for t, c, dt in rows:
            tables.setdefault(t, []).append(f"- {c}: {dt}")
        parts = []
        for t, cols in tables.items():
            parts.append(f"{t}:\n" + "\n".join(cols))
        _schema_cache = "\n\n".join(parts) if parts else default_schema_hint()
        return _schema_cache
    except Exception:
        _schema_cache = default_schema_hint()
        return _schema_cache


def default_schema_hint() -> str:
    # Fallback minimal schema (kept in sync with admin_api models)
    return (
        "orders: id (int), order_no (text), created_at (timestamp), status (text), total (numeric), customer_id (int)\n"
        "order_items: id (int), order_id (int), product_id (int), qty (int), price (numeric)\n"
        "customers: id (int), email (text), city (text), zip (text)\n"
        "products: id (int), sku (text), name (text), category (text), price (numeric), active (boolean)"
    )


def extract_sql_with_error(question: str, err: str) -> str:
    prompt = (
        "Твой предыдущий SQL SELECT вызвал ошибку исполнения. Исправь запрос с учётом ошибки и схемы. "
        "Ограничения: только SELECT, без точки с запятой, без бэктиков."
    )
    schema = get_db_schema()
    resp = state.client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "system", "content": f"Схема БД (public):\n{schema}"},
            {"role": "user", "content": f"Вопрос: {question}"},
            {"role": "user", "content": f"Ошибка: {err}"},
        ],
        temperature=0,
    )
    sql = (resp.choices[0].message.content or "").strip().strip("`")
    sql = re.sub(r"^sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"^```|```$", "", sql).strip()
    return sql

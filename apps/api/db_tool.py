import os
import re
from time import time
from typing import Optional

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI

from .deps import state


db: Optional[SQLDatabase] = None
agent = None


def init_db_agent():
    global db, agent
    if db is not None:
        return
    db = SQLDatabase.from_uri(os.getenv("DB_URL"))
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL"),
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_local = create_sql_agent(llm=llm, toolkit=toolkit, agent_type="tool-calling")
    agent = agent_local


def safe_sql(sql: str) -> str:
    s = sql.strip().strip(";")
    if not re.match(r"^\s*select\s", s, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")
    # forbid dangerous keywords
    banned = [";", "drop ", "delete ", "update ", "insert ", "alter ", "create "]
    sl = s.lower()
    if any(b in sl for b in banned):
        raise ValueError("Dangerous SQL detected")
    # add LIMIT if absent
    if not re.search(r"\blimit\b", sl):
        s += " LIMIT 500"
    return s


def extract_sql(question: str) -> str:
    # Ask LLM to produce SQL only
    prompt = (
        "Верни только один SQL SELECT для PostgreSQL по следующей задаче. "
        "Только SQL без пояснений и без кавычек."
    )
    resp = state.client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    sql = (resp.choices[0].message.content or "").strip().strip("`")
    # Handle code fences
    sql = re.sub(r"^sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"^```|```$", "", sql).strip()
    return sql


def summarize_rows(rows: list[dict]) -> str:
    text = "Сводка по результатам: "
    body = str(rows[:5]) if rows else "данных нет"
    resp = state.client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": "Суммируй данные кратко на русском."},
            {"role": "user", "content": f"{text} {body}"},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


def db_tool_query(question: str) -> dict:
    init_db_agent()
    # naive guard — rely on caller for admin checks
    t0 = time()
    sql = extract_sql(question)
    sql = safe_sql(sql)
    rows = db.run(sql)
    summary = summarize_rows(rows)
    latency = int((time() - t0) * 1000)
    state.metrics["db_queries"] = state.metrics.get("db_queries", 0) + 1
    return {"name": "db_analytics.query", "sql": sql, "rows": rows[:20], "summary": summary, "latency_ms": latency}


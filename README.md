English version • Русская версия: README.ru.md

Support Copilot — AI Assistant for Customer Support (RAG + Tools + DB Analytics)

Note: this repository is a demonstration/reference project, not a finished product. It is published under the MIT License — see LICENSE.

Support Copilot showcases how a support copilot can answer with cited sources from your knowledge base, call business tools (like order status), and provide admin analytics via natural‑language‑to‑SQL — all in a clean web UI and simple API.

Watch the demo video attached to this repository to see the full flow.

Key Outcomes
- Faster responses: instant, confident answers for FAQs with transparent citations.
- Fewer escalations: integrated tools resolve common L2 cases (orders, shipping, pricing).
- Actionable analytics: managers ask questions in plain language and get live tables.

What It Does
- Web chat with live streaming: answers appear token‑by‑token for a smooth experience.
- RAG with citations: the assistant quotes relevant document fragments; each fact can include reference marks like [d0], [d1] with expandable source cards.
- Tool calling for operations:
  - Order status lookup by number (e.g., #A1009) from a read‑only database.
  - Shipping, plans, and pricing sourced from policy/FAQ documents.
- Admin mode (PIN‑protected):
  - Dashboard: totals, orders by status, top products, recent orders.
  - Orders list: filters, quick status update, and details modal.
  - NL→SQL analytics: safe SELECT‑only queries, returned rows, plus the SQL used.
- Metrics strip: live stats for tool calls, DB queries, RAG hits, and answer confidence.
- Health page: quick environment and readiness check for the backend and index.
- Telegram bot hook: can be connected for messenger support.

Where It Fits (examples)
- Support teams that need trustworthy, cited answers.
- E‑commerce or services with order tracking and clear policies.
- Operations and managers looking for quick insights without writing SQL.

How It Works (High Level)
- Knowledge Base: Markdown/text documents are indexed for semantic retrieval.
- AI Orchestration: The assistant decides when to use RAG, look up an order, or run an analytics query.
- Streaming UI: Shows context (sources, labels, tool info) first, then the answer stream.
- Safe Analytics: Read‑only queries with strong guards to prevent DML/DDL and automatic LIMIT.

Suggested Demo Scenarios
- Ask a policy question like “What is the refund window?” and review the cited sources.
- Ask “Where is my order #A1009?” to trigger the order status tool.
- Enable Admin mode (PIN: 123456) and ask “Sales last 7 days?” to see NL→SQL and a results table.
- Explore the Dashboard and Orders tabs — the database is pre‑seeded for rich results.

Running the Demo (Brief)
- Copy .env.example to .env and adjust keys/URLs if needed.
- Start with Docker Compose: docker-compose up -d
- Open Web UI (http://localhost:3000) and API (http://localhost:8000). Use Admin PIN 123456.

Security & Privacy
- Sensitive data (emails, cards, phones) is masked before processing.
- Admin analytics is gated by a PIN; SQL is SELECT‑only and validated.

What’s Included
- Web chat with citations and a sources panel.
- Admin dashboard (stats, orders, top products, recent activity).
- NL→SQL analytics with visible SQL.
- Health endpoint and live metrics.

Using This Demo
- The project is open‑source under MIT. You can fork, adapt, and integrate it with your documents and systems. The demo video illustrates the end‑to‑end UX; use it as a starting point for your own setup.

License
- MIT License. See LICENSE for details. No warranty; use at your own risk.

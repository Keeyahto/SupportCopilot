import os
import httpx


TOOLS_BASE_URL = os.getenv("TOOLS_BASE_URL", "http://tools-api:8010")


async def call_tools_api(intent: str, clean_text: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        if intent == "order_status":
            m = __import__("re").search(r"#(\w+)", clean_text)
            order = m.group(1) if m else ""
            r = await client.get(f"{TOOLS_BASE_URL}/get_order_status", params={"id": order})
            data = r.json()
            return {"name": "orders.status", "data": data, "ok": r.status_code == 200}
        if intent == "plan_price":
            # naive plan extraction
            plan = "Pro" if "pro" in clean_text.lower() else "Free"
            r = await client.get(f"{TOOLS_BASE_URL}/get_plan_price", params={"plan": plan, "currency": "RUB"})
            data = r.json()
            return {"name": "plans.price", "data": data, "ok": r.status_code == 200}
        if intent == "delivery_eta":
            m = __import__("re").search(r"(\b\d{6}\b)", clean_text)
            zipc = m.group(1) if m else "101000"
            r = await client.get(f"{TOOLS_BASE_URL}/get_delivery_eta", params={"zip": zipc})
            data = r.json()
            return {"name": "shipping.eta", "data": data, "ok": r.status_code == 200}
    return {"name": intent, "data": {}, "ok": False}


from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import json
from .loaders import load_json


app = FastAPI(title="Tools API (mock)")


@app.get("/get_order_status")
def get_order_status(id: str = Query(..., alias="id")):
    items = load_json("orders.json")
    for it in items:
        if it.get("order_no") == id:
            return it
    return JSONResponse({"error": "not_found", "message": "Order not found"}, status_code=404)


@app.get("/get_plan_price")
def get_plan_price(plan: str, currency: str = "RUB"):
    items = load_json("plans.json")
    for it in items:
        if it.get("plan") == plan and it.get("currency") == currency:
            return it
    return JSONResponse({"error": "not_found", "message": "Plan not found"}, status_code=404)


@app.get("/get_delivery_eta")
def get_delivery_eta(zip: str):
    items = load_json("shipping.json")
    for it in items:
        if it.get("zip") == zip:
            return it
    return JSONResponse({"error": "not_found", "message": "Zip not found"}, status_code=404)


@app.post("/create_ticket")
def create_ticket(payload: dict = Body(...)):
    topic = payload.get("topic", "general")
    summary = payload.get("summary", "")
    user = payload.get("user", "")
    tid = str(uuid.uuid4())
    line = {"id": tid, "topic": topic, "summary": summary, "user": user}
    log_file = Path("/app/data/tickets.log")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return {"ticket_id": tid}

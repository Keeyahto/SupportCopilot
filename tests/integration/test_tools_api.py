from fastapi.testclient import TestClient
from apps.tools_api.main import app


client = TestClient(app)


def test_get_order_status_success():
    r = client.get("/get_order_status", params={"id": "A1001"})
    assert r.status_code == 200
    assert r.json()["order_no"] == "A1001"


def test_get_plan_price_success():
    r = client.get("/get_plan_price", params={"plan": "Pro", "currency": "RUB"})
    assert r.status_code == 200
    assert r.json()["plan"] == "Pro"


def test_get_delivery_eta_success():
    r = client.get("/get_delivery_eta", params={"zip": "101000"})
    assert r.status_code == 200
    assert r.json()["eta_days"] >= 1


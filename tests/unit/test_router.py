from apps.api.router import pii_filter, route_intent


def test_pii_filter_masks_email_phone_card():
    s = "Почта a@b.com, тел +7 999 123 45 67, карта 1234-5678-1234-5678"
    out = pii_filter(s)
    assert "[email]" in out and "[phone]" in out and "[card]" in out


def test_route_intent_admin_db():
    t = "Сколько заказов за день 2025-08-01?"
    assert route_intent(t, "admin", True) == "db_analytics"


def test_route_intent_orders():
    assert route_intent("Где мой заказ #A123?", "orders", False) == "order_status"


def test_route_intent_plan_price():
    assert route_intent("Какая цена плана Pro?", "faq", False) == "plan_price"


def test_route_intent_delivery():
    assert route_intent("Когда доставка в 101000?", "faq", False) == "delivery_eta"


def test_route_intent_default_rag():
    assert route_intent("Привет", "faq", False) == "rag"


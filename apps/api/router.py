import re
from typing import Literal


def pii_filter(text: str) -> str:
    s = text
    # email
    s = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email]", s)
    # credit card (needs to be before phone to avoid conflicts)
    s = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[card]", s)
    # phone (very rough)
    s = re.sub(r"\+?\d[\d\s\-()]{7,}\d", "[phone]", s)
    # profanity mask example
    s = re.sub(r"\b(хер|хуй|fuck)\b", "***", s, flags=re.IGNORECASE)
    return s


def route_intent(text: str, mode: Literal["faq","orders","policies","admin"], is_admin: bool) -> str:
    t = text.lower()
    if is_admin and re.search(r"\b(сколько|выручка|продали|за день|за период|топ)\b", t):
        return "db_analytics"
    if re.search(r"#\w+", text):
        return "order_status"
    if re.search(r"\b(цена|тариф|стоимость)\b", t):
        return "plan_price"
    if re.search(r"\b(доставка|когда|eta|за сколько дней)\b", t):
        return "delivery_eta"
    return "rag"


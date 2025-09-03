import os
import asyncio
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from redis import Redis


API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Инициализируем бота только если не в тестовом окружении
if os.getenv("TESTING") != "true":
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN", ""))
    dp = Dispatcher()
    rdb = Redis.from_url(REDIS_URL, decode_responses=True)
else:
    # Заглушки для тестов
    bot = None
    dp = None
    rdb = None

# Заглушки для декораторов в тестовом режиме
if os.getenv("TESTING") == "true":
    class DummyDispatcher:
        def message(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    dp = DummyDispatcher()


def get_mode(chat_id: int) -> str:
    if rdb is None:
        return "faq"
    return rdb.get(f"mode:{chat_id}") or "faq"


def set_mode(chat_id: int, mode: str):
    if rdb is None:
        return
    rdb.set(f"mode:{chat_id}", mode)


def is_admin(chat_id: int) -> bool:
    if rdb is None:
        return False
    return rdb.get(f"admin:{chat_id}") == "1"


def set_admin(chat_id: int, val: bool):
    if rdb is None:
        return
    rdb.set(f"admin:{chat_id}", "1" if val else "0")


def rate_limited(chat_id: int) -> bool:
    if rdb is None:
        return False
    key = f"rl:{chat_id}"
    if rdb.exists(key):
        return True
    rdb.setex(key, 2, "1")  # 1 request / 2 sec
    return False


@dp.message(Command("start"))
async def cmd_start(m: Message):
    await m.answer("Support Copilot: /mode faq|orders|policies|admin, /admin <PIN>. Напишите вопрос.")


@dp.message(Command("mode"))
async def cmd_mode(m: Message):
    parts = (m.text or "").split()
    if len(parts) < 2 or parts[1] not in ("faq", "orders", "policies", "admin"):
        return await m.answer("Использование: /mode faq|orders|policies|admin")
    set_mode(m.chat.id, parts[1])
    await m.answer(f"Режим: {parts[1]}")


@dp.message(Command("admin"))
async def cmd_admin(m: Message):
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Использование: /admin <PIN>")
    pin = parts[1].strip()
    if pin and pin == os.getenv("ADMIN_PIN", "123456"):
        set_admin(m.chat.id, True)
        await m.answer("Admin режим активирован.")
    else:
        set_admin(m.chat.id, False)
        await m.answer("Неверный PIN.")


@dp.message(F.text)
async def any_text(m: Message):
    if rate_limited(m.chat.id):
        return await m.answer("Подождите пару секунд...")

    mode = get_mode(m.chat.id)
    admin = is_admin(m.chat.id)
    payload = {"text": m.text or "", "mode": mode, "strict": False, "lang": "ru"}
    headers = {}
    if admin:
        headers["X-Admin-Key"] = os.getenv("ADMIN_PIN", "123456")

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE_URL}/chat", json=payload, headers=headers)
        if r.status_code >= 400:
            return await m.answer("Ошибка. Попробуйте уточнить запрос.")
        data = r.json()
        answer = data.get("answer", "")
        if admin and data.get("tool_info"):
            ti = data["tool_info"]
            rows = ti.get("rows") or []
            table = "\n".join([str(rows[i]) for i in range(0, min(5, len(rows)))])
            answer += f"\n\nSQL: {ti.get('sql')}\n{table}"
        await m.answer(answer)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


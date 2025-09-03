import types
from apps.bot import main as bot


class DummyRedis:
    def __init__(self):
        self.d = {}

    def get(self, k):
        return self.d.get(k)

    def set(self, k, v):
        self.d[k] = v

    def setex(self, k, ttl, v):
        self.d[k] = v

    def exists(self, k):
        return 1 if k in self.d else 0


def test_mode_and_admin_flags(monkeypatch):
    r = DummyRedis()
    monkeypatch.setattr(bot, "rdb", r)

    chat = 1
    bot.set_mode(chat, "admin")
    assert bot.get_mode(chat) == "admin"

    assert not bot.is_admin(chat)
    bot.set_admin(chat, True)
    assert bot.is_admin(chat)


def test_rate_limit(monkeypatch):
    r = DummyRedis()
    monkeypatch.setattr(bot, "rdb", r)
    chat = 2
    first = bot.rate_limited(chat)
    again = bot.rate_limited(chat)
    assert first is False and again is True


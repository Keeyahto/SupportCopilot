# 🚀 Быстрый старт SupportCopilot

## ✅ Что уже готово

- ✅ Виртуальное окружение создано и активировано
- ✅ Все зависимости установлены
- ✅ Структура проекта настроена
- ✅ Скрипты запуска созданы

## 🎯 Следующие шаги

### 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```bash
# OpenAI API ключ (обязательно)
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot токен (обязательно для бота)
BOT_TOKEN=your_telegram_bot_token_here

# База данных (опционально, для полной функциональности)
DATABASE_URL=postgresql://user:password@localhost:5432/supportcopilot

# Redis (опционально, для кэширования)
REDIS_URL=redis://localhost:6379
```

### 2. Запуск сервисов

#### Вариант 1: PowerShell скрипт (рекомендуется для Windows)
```powershell
.\run.ps1
```

#### Вариант 2: Ручной запуск по отдельности



**API Server:**
```bash
cd apps/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Tools API:**
```bash
Tools API удалён: инструменты теперь работают через БД в API
```

**Telegram Bot:**
```bash
cd apps/bot
python main.py
```

### 3. Проверка работы

После запуска проверьте:

- 🌐 **API Server**: http://localhost:8000
- 🔧 **Tools API**: http://localhost:8001
- 🤖 **Telegram Bot**: отправьте сообщение боту

## 🔧 Полезные команды

### Проверка установки
```bash
# Проверьте, что виртуальное окружение активировано
# и все зависимости установлены
pip list | findstr fastapi
pip list | findstr aiogram
```

### Активация виртуального окружения
```bash
.\venv\Scripts\Activate.ps1
```

### Установка новых зависимостей
```bash
pip install package_name
pip freeze > requirements.txt
```

## 📚 Документация

- 📖 **README.md** - полная документация проекта
- ⚡ **run.ps1** - PowerShell скрипт запуска всех сервисов

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте, что виртуальное окружение активировано
2. Запустите `python check_install.py` для диагностики
3. Проверьте логи сервисов
4. Убедитесь, что все переменные окружения настроены

---

**🎉 Готово! Ваш SupportCopilot готов к работе!**

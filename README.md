# SupportCopilot

Система поддержки клиентов с использованием AI для автоматизации ответов на часто задаваемые вопросы.

## Структура проекта

```
SupportCopilot/
├── apps/
│   ├── api/           # Основное API приложение
│   ├── bot/           # Telegram бот
│   └── web/           # Веб UI (Next.js)
├── data/              # Данные и конфигурация
├── db/                # Скрипты базы данных
├── kits/              # Общие компоненты
└── docker-compose.yml # Docker конфигурация
```

## Установка

### 1. Создание виртуального окружения

```bash
python -m venv venv
```

### 2. Активация виртуального окружения

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` на основе `config.py` или установите переменные окружения:

```bash
# База данных
export DATABASE_URL="postgresql://user:password@localhost:5432/supportcopilot"

# Redis
export REDIS_URL="redis://localhost:6379"

# OpenAI
export OPENAI_API_KEY="your_api_key_here"

# Telegram Bot
export BOT_TOKEN="your_bot_token_here"
```

## Запуск

### Запуск API сервера

```bash
cd apps/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Запуск Telegram бота

```bash
cd apps/bot
python main.py
```

### Запуск Tools API

```bash
Tools API удалён: логика инструментов теперь работает через реальную БД внутри основного API
```

### Запуск через Docker

```bash
docker-compose up -d
```

## Разработка

### Установка зависимостей для разработки

```bash
pip install -r requirements.txt
```

### Структура кода

- **API**: FastAPI приложение с эндпоинтами для обработки запросов
- **Bot**: Telegram бот на aiogram для взаимодействия с пользователями
- **Tools API**: API для загрузки и обработки документов
- **Kits**: Общие компоненты для переиспользования

## Лицензия

MIT License

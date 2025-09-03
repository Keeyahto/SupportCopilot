import os
import json
from typing import AsyncGenerator, Optional

from openai import OpenAI
from sse_starlette.sse import EventSourceResponse

from .deps import state


def system_prompt(mode: str, strict: bool) -> str:
    base = (
        "Ты — ассистент поддержки. Отвечай кратко, дружелюбно, с цитатами источников. "
        "Если даются правила, не обещай возвраты вне правил."
    )
    if mode == "policies" or strict:
        base += " Отвечай только из контекста. Если данных недостаточно — предложи эскалацию."
    return base


def build_user_prompt(question: str, context_sources: list[dict], tool_block: Optional[dict] = None) -> str:
    ctx = []
    for s in context_sources[:5]:
        ctx.append(f"[{s['filename']}] {s['snippet']}")
    ctx_block = "\n".join(ctx)
    tb = ""
    if tool_block:
        tb = f"\n\nИнструмент: {json.dumps(tool_block, ensure_ascii=False)}"
    return f"Вопрос: {question}\n\nКонтекст:\n---\n{ctx_block}\n---{tb}"


def _llm_enabled() -> bool:
    return bool(state.client) and bool(os.getenv("OPENAI_API_KEY")) and bool(os.getenv("CHAT_MODEL"))


def llm_answer(question: str, context_sources: list[dict], tool_info: Optional[dict] = None) -> str:
    if not _llm_enabled():
        return "Демо-ответ (LLM отключён). Это локальный режим без доступа к OpenAI."
    client: OpenAI = state.client
    resp = client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt("faq", False)},
            {"role": "user", "content": build_user_prompt(question, context_sources, tool_info)},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


async def llm_stream_answer(question: str, context_sources: list[dict], tool_info: Optional[dict] = None) -> AsyncGenerator[dict, None]:
    print(f"🚀 [LLM] Начинаем стрим для вопроса: {question[:50]}...")
    print(f"🚀 [LLM] Источники: {len(context_sources)}")
    print(f"🚀 [LLM] Tool info: {tool_info}")
    
    client: OpenAI = state.client
    # send context first
    context_event = {"event": "context", "data": json.dumps({
        "sources": context_sources,
        "labels": [],
        "tool_info": tool_info or {},
    }, ensure_ascii=False)}
    print(f"📋 [LLM] Отправляем context event")
    yield context_event

    if not _llm_enabled():
        print("⚠️ [LLM] LLM отключен, отправляем fallback")
        # Fallback: emit a short stub answer token-by-token
        stub = "Демо-ответ (LLM отключён)."
        for ch in stub:
            token_event = {"event": "token", "data": json.dumps({"t": ch}, ensure_ascii=False)}
            print(f"🔤 [LLM] Отправляем fallback токен: '{ch}'")
            yield token_event
        done_event = {"event": "done", "data": json.dumps({"finish_reason": "stop"}, ensure_ascii=False)}
        print(f"✅ [LLM] Отправляем done event")
        yield done_event
        return

    print(f"🤖 [LLM] LLM включен, вызываем OpenAI API")
    try:
        with client.chat.completions.stream(
            model=os.getenv("CHAT_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt("faq", False)},
                {"role": "user", "content": build_user_prompt(question, context_sources, tool_info)},
            ],
            temperature=0.2,
        ) as stream:
            print(f"📡 [LLM] Начинаем стрим от OpenAI")
            token_count = 0
            last_delta = ""  # Для дедупликации
            
            for chunk in stream:
                delta = None
                try:
                    # LM Studio использует другую структуру чанков
                    if hasattr(chunk, 'choices') and chunk.choices:
                        # OpenAI формат
                        delta = chunk.choices[0].delta.content
                    elif hasattr(chunk, 'content'):
                        # LM Studio формат
                        delta = chunk.content
                    elif hasattr(chunk, 'delta') and hasattr(chunk.delta, 'content'):
                        # Альтернативный формат
                        delta = chunk.delta.content
                    elif hasattr(chunk, 'type') and chunk.type == 'content.delta':
                        # ContentDeltaEvent формат
                        delta = getattr(chunk, 'delta', None)
                    elif hasattr(chunk, 'type') and chunk.type == 'chunk':
                        # ChunkEvent формат
                        if hasattr(chunk, 'chunk') and hasattr(chunk.chunk, 'choices'):
                            delta = chunk.chunk.choices[0].delta.content
                    else:
                        print(f"🔤 [LLM] Неизвестная структура чанка: {type(chunk)} - {chunk}")
                        delta = None
                except Exception as e:
                    print(f"⚠️ [LLM] Ошибка получения delta: {e}")
                    delta = None
                
                if delta and delta != last_delta:  # Дедупликация
                    token_event = {"event": "token", "data": json.dumps({"t": delta}, ensure_ascii=False)}
                    print(f"🔤 [LLM] Отправляем токен {token_count}: '{delta}'")
                    yield token_event
                    token_count += 1
                    last_delta = delta
                elif delta:
                    print(f"🔤 [LLM] Пропускаем дублированный токен: '{delta}'")
                else:
                    print(f"🔤 [LLM] Пустой delta в чанке типа: {type(chunk)}")
            
            print(f"✅ [LLM] Стрим завершен, отправлено токенов: {token_count}")
            done_event = {"event": "done", "data": json.dumps({"finish_reason": "stop"}, ensure_ascii=False)}
            print(f"✅ [LLM] Отправляем done event")
            yield done_event
    except Exception as e:
        print(f"💥 [LLM] Ошибка в стриме: {e}")
        error_event = {"event": "error", "data": json.dumps({"message": str(e)})}
        print(f"❌ [LLM] Отправляем error event")
        yield error_event


def sse_from_generator(gen: AsyncGenerator[dict, None]) -> EventSourceResponse:
    async def event_gen():
        try:
            async for ev in gen:
                yield ev
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)})}
    return EventSourceResponse(event_gen())

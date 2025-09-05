"use client";
import React, { useRef, useState } from "react";
import { useUiStore } from "../lib/store";
import { postChat, postChatStream } from "../lib/api";
import { splitThinking } from "../lib/think";
import type { SSEContextData, SSEDoneData, SSEErrorData } from "../lib/types";

export default function ChatBox({ sessionId }: { sessionId?: string }) {
  const { mode, strict, lang, isAdmin, adminKey, pushMessage, updateLastAssistant, resetDialog } = useUiStore();
  const [text, setText] = useState("");
  const [isStreaming, setStreaming] = useState(false);
  const [phase, setPhase] = useState<"idle" | "waiting" | "streaming">("idle");
  const [tokens, setTokens] = useState(0)
  const lastTokenRef = useRef<string | null>(null);

  const disabled = !text.trim() || (mode === "admin" && !isAdmin);

  const doStream = async () => {
    setStreaming(true);
    setPhase("waiting");
    setTokens(0);
    const userId = crypto.randomUUID();
    pushMessage({ id: userId, role: "user", text, ts: Date.now() });
    const asstId = crypto.randomUUID();
    pushMessage({ id: asstId, role: "assistant", text: "", ts: Date.now(), labels: [], sources: [] });
    setText("");
    let acc = "";

    try {
      await postChatStream(
        { text, mode, strict, lang },
        {
          onContext: (ctx: SSEContextData) => {
            setPhase("streaming");
            updateLastAssistant({ sources: ctx.sources, labels: ctx.labels, tool_info: ctx.tool_info });
          },
          onToken: (t: string) => {
            if (lastTokenRef.current === t) { return; }
                        lastTokenRef.current = t;
                                    acc += t;
            setTokens((n) => n + 1);
            const { thinking, answer } = splitThinking(acc);
            // Проверяем, не содержит ли токен thinking блок с полным ответом
            if (t.includes('<think>') && t.includes('</think>')) {
              // Если токен содержит полный thinking блок, используем только его
              const { thinking: newThinking, answer: newAnswer } = splitThinking(t);
              updateLastAssistant({ text: newAnswer, thinking: newThinking });
            } else {
              updateLastAssistant({ text: answer, thinking });
            }
          },
          onDone: (_d: SSEDoneData) => {
            setStreaming(false);
            setPhase("idle");
          },
          onError: (e: SSEErrorData) => {
            setStreaming(false);
            alert(e.message || "Ошибка соединения");
          },
        },
        isAdmin ? adminKey : undefined,
        sessionId
      );
    } catch (e: any) {
      setStreaming(false);
      alert(e?.message || "Ошибка соединения");
    }
  };

  const doOnce = async () => {
    const userId = crypto.randomUUID();
    pushMessage({ id: userId, role: "user", text, ts: Date.now() });
    setText("");
    try {
      const res = await postChat({ text, mode, strict, lang }, isAdmin ? adminKey : undefined, sessionId);
      const { thinking, answer } = splitThinking(res.answer || "");
      pushMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        text: answer,
        thinking,
        labels: res.labels,
        sources: res.sources,
        tool_info: res.tool_info,
        ts: Date.now(),
      });
    } catch (e: any) {
      alert(e?.message || "Ошибка соединения");
    }
  };

  return (
    <div className="mt-3">
      {phase !== "idle" && (
        <div className="mb-2">
          <div className={`h-2 rounded-full overflow-hidden ${phase === "waiting" ? "bg-indigo-100" : "bg-emerald-100"}`}>
            <div className={`h-2 w-1/3 animate-pulse ${phase === "waiting" ? "bg-indigo-400" : "bg-emerald-400"}`}></div>
          </div>
          <div className="mt-1 text-xs text-neutral-500 flex items-center justify-between">
            <span>{phase === "waiting" ? "Подготовка контекста..." : "Генерация ответа..."}</span>
            {phase === "streaming" && <span>токенов: {tokens}</span>}
          </div>
        </div>
      )}
      <textarea
        className="w-full border rounded-xl p-3 resize-y min-h-[80px]"
        placeholder="Спросите… (например: Где мой заказ #A1001?)"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!disabled && !isStreaming) doStream();
          }
        }}
      />
      <div className="mt-2 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <button
            className="px-3 py-2 rounded-lg bg-indigo-600 text-white disabled:opacity-50"
            onClick={doStream}
            disabled={disabled || isStreaming}
          >
            Отправить (SSE)
          </button>
          <button
            className="px-3 py-2 rounded-lg bg-neutral-200 text-neutral-900 disabled:opacity-50"
            onClick={doOnce}
            disabled={disabled || isStreaming}
          >
            Отправить (без стрима)
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="text-sm text-rose-600 hover:underline"
            onClick={() => resetDialog()}
            disabled={isStreaming}
          >
            Сбросить диалог
          </button>
        </div>
      </div>
      {mode === "admin" && !isAdmin && (
        <div className="mt-1 text-xs text-rose-600">Требуется PIN для режима Admin</div>
      )}
    </div>
  );
}

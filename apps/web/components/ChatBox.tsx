"use client";
import React, { useState } from "react";
import { useUiStore } from "../lib/store";
import { postChat, postChatStream } from "../lib/api";
import { splitThinking } from "../lib/think";
import type { SSEContextData, SSEDoneData, SSEErrorData } from "../lib/types";

export default function ChatBox({ sessionId }: { sessionId?: string }) {
  const { mode, strict, lang, isAdmin, adminKey, pushMessage, updateLastAssistant, resetDialog } = useUiStore();
  const [text, setText] = useState("");
  const [isStreaming, setStreaming] = useState(false);

  const disabled = !text.trim() || (mode === "admin" && !isAdmin);

  const doStream = async () => {
    setStreaming(true);
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
            updateLastAssistant({ sources: ctx.sources, labels: ctx.labels, tool_info: ctx.tool_info });
          },
          onToken: (t: string) => {
            acc += t;
            const { thinking, answer } = splitThinking(acc);
            updateLastAssistant({ text: answer, thinking });
          },
          onDone: (_d: SSEDoneData) => {
            setStreaming(false);
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
      <textarea
        className="w-full border rounded-xl p-3 resize-y min-h-[80px]"
        placeholder="Спросите… (например: Где мой заказ #A1001?)"
        value={text}
        onChange={(e) => setText(e.target.value)}
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


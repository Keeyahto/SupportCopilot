"use client";
import React, { useEffect, useRef } from "react";
import { useUiStore } from "../lib/store";
import MessageItem from "./MessageItem";

export default function MessageList() {
  const messages = useUiStore((s) => s.messages);
  const endRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-auto flex flex-col gap-3 pr-1" style={{ minHeight: 200 }}>
      {messages.map((m) => (
        <MessageItem
          key={m.id}
          role={m.role}
          text={m.text}
          labels={m.labels}
          sources={m.sources}
          tool_info={m.tool_info}
          thinking={m.thinking}
        />
      ))}
      <div ref={endRef} />
    </div>
  );
}

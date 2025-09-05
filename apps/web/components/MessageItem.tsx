"use client";
import React, { useState } from "react";
import type { Label, ToolInfo, Source } from "../lib/types";
import ToolBadge from "./ToolBadge";
import DbSummary from "./DbSummary";
import SourceCard from "./SourceCard";

export default function MessageItem({
  role,
  text,
  labels,
  sources,
  tool_info,
  thinking,
}: {
  role: "user" | "assistant";
  text: string;
  labels?: Label[];
  sources?: Source[];
  tool_info?: ToolInfo;
  thinking?: string;
}) {
  const [showThink, setShowThink] = useState(false);
  const [showSources, setShowSources] = useState(false);
  
  // Проверяем, есть ли размышления для отображения
  const hasThinking = thinking && thinking.trim().length > 0;
  const referencedIds = new Set(
    (text || "").match(/\[d\d+\]/g)?.map((m) => m.replace(/\[|\]/g, "")) || []
  );
  const filteredSources = (sources || []).filter((s) =>
    referencedIds.size === 0 ? false : referencedIds.has(s.id)
  );
  
  return (
    <div className={`card ${role === "assistant" ? "bg-white" : "bg-neutral-50"}`}>
      {role === "assistant" && (labels?.length || tool_info) && (
        <div className="mb-2 flex items-center gap-2 flex-wrap">
          {labels?.map((l) => (
            <ToolBadge key={l} label={l} />
          ))}
          {tool_info && !(labels || []).includes("DB Tool") && !(labels || []).includes("Tool-call") && (
            <ToolBadge label={
              tool_info.name === "db_analytics.query"
                ? "DB Tool"
                : tool_info.name === "orders.status"
                ? "Order Status"
                : "Tool-call"
            } />
          )}
        </div>
      )}
      
      {/* Панель размышлений - только одна копия */}
      {role === "assistant" && hasThinking && (
        <div className="mt-2">
          <button
            className="w-full text-left text-xs px-3 py-2 bg-neutral-100 rounded-lg text-neutral-700 hover:bg-neutral-200 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"
            onClick={() => setShowThink((v) => !v)}
            aria-expanded={showThink}
            aria-label={showThink ? "Скрыть размышления модели" : "Показать размышления модели"}
          >
            <span className="flex items-center gap-2">
              <span className="text-indigo-600">💭</span>
              {showThink ? "Скрыть размышления" : "Показать размышления"}
            </span>
          </button>
          {showThink && (
            <div className="mt-2 p-3 bg-neutral-50 rounded-lg border border-neutral-200">
              <div className="text-xs font-medium text-neutral-600 mb-2">Размышления модели:</div>
              <pre className="text-xs font-mono whitespace-pre-wrap text-neutral-700 max-h-48 overflow-y-auto">
                {thinking}
              </pre>
            </div>
          )}
        </div>
      )}
      
      <div className="whitespace-pre-wrap leading-relaxed text-neutral-900">
        {text ? text.replace(/<\/?think>/gi, "") : ""}
      </div>
      
      {tool_info && <DbSummary tool={tool_info} />}
      
      {role === "assistant" && filteredSources && filteredSources.length > 0 && (
        <div className="mt-3">
          <button
            className="text-sm text-neutral-600 underline"
            onClick={() => setShowSources((v) => !v)}
            aria-expanded={showSources}
          >
            {showSources ? "Скрыть источники" : `Показать источники (${filteredSources.length})`}
          </button>
          {showSources && (
            <div className="mt-2 grid md:grid-cols-2 gap-2">
              {filteredSources.map((s) => (
                <SourceCard key={s.id} source={s} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

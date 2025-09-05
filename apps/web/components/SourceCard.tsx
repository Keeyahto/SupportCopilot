"use client";
import React from "react";
import type { HighlightRange, Source } from "../lib/types";
import { renderHighlighted } from "../lib/highlight";

export default function SourceCard({ source }: { source: Source }) {
  const scorePct = Math.round(source.score * 1000) / 10;
  const ranges: HighlightRange[] = source.highlights || [];

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(source.content || source.snippet || "");
    } catch {}
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <div className="font-medium text-sm">
          <span className="text-neutral-700">{source.filename}</span>
          {Number.isFinite(source.page) && (
            <span className="text-neutral-400"> · стр. {source.page}</span>
          )}
        </div>
        <div className="text-xs text-neutral-500">{scorePct}%</div>
      </div>
      <pre className="font-mono text-sm whitespace-pre-wrap leading-relaxed text-neutral-800 max-h-72 overflow-y-auto">
        {source.content ? source.content : renderHighlighted(source.snippet, ranges)}
      </pre>
      <div className="mt-2 text-right">
        <button onClick={copy} className="text-xs text-indigo-600 hover:underline">Скопировать фрагмент</button>
      </div>
    </div>
  );
}

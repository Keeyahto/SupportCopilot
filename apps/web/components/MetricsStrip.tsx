"use client";
import React, { useEffect } from "react";
import { getMetrics } from "../lib/api";
import { useUiStore } from "../lib/store";

const REFRESH_MS = Number(process.env.NEXT_PUBLIC_METRICS_REFRESH_MS || 5000);

export default function MetricsStrip() {
  const metrics = useUiStore((s) => s.metrics);
  const setMetrics = useUiStore((s) => s.setMetrics);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const m = await getMetrics();
        if (alive) setMetrics(m);
      } catch {
        // ignore
      }
    };
    tick();
    const id = setInterval(tick, REFRESH_MS);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [setMetrics]);

  if (!metrics) return null;

  const pct = Math.round(metrics.avg_confidence * 1000) / 10;

  return (
    <div className="flex items-center gap-3 text-xs text-neutral-700">
      <div>🛠️ {metrics.tool_calls}</div>
      <div>🗄️ {metrics.db_queries}</div>
      <div>📚 {metrics.rag_queries}</div>
      <div>🤝 {pct}%</div>
    </div>
  );
}


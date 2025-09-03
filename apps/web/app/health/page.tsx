"use client";
import React, { useEffect, useState } from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import { getHealth } from "../../lib/api";
import type { HealthResponse } from "../../lib/types";

export default function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    getHealth().then(setHealth).catch((e) => setError(e?.message || "Ошибка"));
  }, []);

  return (
    <div className="flex-1 flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="card">
          <div className="text-lg font-semibold mb-2">Health</div>
          {error && <div className="text-rose-600">{error}</div>}
          {health && (
            <ul className="text-sm text-neutral-800 space-y-1">
              <li><b>env:</b> {health.env}</li>
              <li><b>faiss_ready:</b> {String(health.faiss_ready)}</li>
              <li><b>chat_model:</b> {health.chat_model}</li>
              <li><b>embed_model:</b> {health.embed_model}</li>
              <li><b>openai_base_url:</b> {health.openai_base_url}</li>
            </ul>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}


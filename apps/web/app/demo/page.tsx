"use client";
import React, { useEffect, useMemo, useState } from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import MessageList from "../../components/MessageList";
import ChatBox from "../../components/ChatBox";
import MetricsStrip from "../../components/MetricsStrip";
import AdminPanel from "../../components/AdminPanel";
import { useUiStore } from "../../lib/store";

export default function DemoPage() {
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const isAdmin = useUiStore((s) => s.isAdmin);

  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, []);

  return (
    <div className="flex-1 flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col gap-3">
        <div className="flex items-center justify-end">
          <MetricsStrip />
        </div>

        <MessageList />
        <ChatBox sessionId={sessionId} />

        {isAdmin && (
          <div className="mt-4">
            <AdminPanel />
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

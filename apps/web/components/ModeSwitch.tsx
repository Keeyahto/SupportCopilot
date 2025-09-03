"use client";
import React from "react";
import { useUiStore } from "../lib/store";
import type { Mode } from "../lib/types";

export default function ModeSwitch({ onRequireAdmin }: { onRequireAdmin?: () => void }) {
  const mode = useUiStore((s) => s.mode);
  const setMode = useUiStore((s) => s.setMode);
  const isAdmin = useUiStore((s) => s.isAdmin);

  const pick = (m: Mode) => {
    if (m === "admin" && !isAdmin) {
      onRequireAdmin?.();
      return;
    }
    setMode(m);
  };

  const item = (m: Mode, label: string) => (
    <button
      key={m}
      onClick={() => pick(m)}
      className={`px-3 py-1 rounded-full text-sm ${mode === m ? "bg-neutral-900 text-white" : "bg-neutral-200 text-neutral-900"}`}
    >
      {label}
    </button>
  );

  return (
    <div className="inline-flex items-center gap-2">
      {item("faq", "FAQ")}
      {item("orders", "Orders")}
      {item("policies", "Policies")}
      {item("admin", "Admin")}
    </div>
  );
}


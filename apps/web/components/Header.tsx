"use client";
import React, { useState } from "react";
import { useUiStore } from "../lib/store";
import ModeSwitch from "./ModeSwitch";
import PinGate from "./PinGate";

export default function Header() {
  const strict = useUiStore((s) => s.strict);
  const setStrict = useUiStore((s) => s.setStrict);
  const clearAdmin = useUiStore((s) => s.clearAdmin);
  const isAdmin = useUiStore((s) => s.isAdmin);
  const [pinOpen, setPinOpen] = useState(false);

  return (
    <header className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-6">
        <a href="/" className="font-semibold">Support Copilot</a>
        <nav className="hidden sm:flex items-center gap-3 text-sm">
          <a href="/demo" className="text-neutral-700 hover:underline">Демо</a>
          <a href="/health" className="text-neutral-700 hover:underline">Health</a>
        </nav>
      </div>
      <div className="flex items-center gap-3">
        <ModeSwitch onRequireAdmin={() => setPinOpen(true)} />
        <label className="flex items-center gap-1 text-sm">
          <input type="checkbox" checked={!!strict} onChange={(e) => setStrict(e.target.checked)} />
          Strict
        </label>
        <button className="text-sm px-3 py-1 rounded-full bg-neutral-200" onClick={() => setPinOpen(true)}>Admin</button>
        {isAdmin && (
          <button className="text-sm text-rose-600" onClick={() => clearAdmin()}>Выйти</button>
        )}
      </div>
      <PinGate open={pinOpen} onClose={() => setPinOpen(false)} />
    </header>
  );
}


"use client";
import React, { useState } from "react";
import { useUiStore } from "../lib/store";

export default function PinGate({ open, onClose }: { open: boolean; onClose: () => void }) {
  const setAdmin = useUiStore((s) => s.setAdmin);
  const setMode = useUiStore((s) => s.setMode);
  const [pin, setPin] = useState("");
  const [loading, setLoading] = useState(false);
  if (!open) return null;

  const tryLogin = async () => {
    setLoading(true);
    try {
      // Простая проверка PIN - в реальном приложении здесь должна быть проверка на сервере
      // Пока используем хардкод для демо
      if (pin === "1234") {
        setAdmin(pin);
        setMode("admin");
        onClose();
      } else {
        alert("Неверный PIN");
      }
    } catch (e: any) {
      alert(e?.message || "Ошибка аутентификации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
      <div className="card w-full max-w-sm">
        <div className="text-lg font-semibold mb-2">Admin PIN</div>
        <input
          type="password"
          className="w-full border rounded-lg p-2"
          placeholder="Введите PIN"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && tryLogin()}
        />
        <div className="mt-3 flex items-center justify-end gap-2">
          <button className="px-3 py-2 rounded-lg" onClick={onClose} disabled={loading}>Отмена</button>
          <button className="px-3 py-2 rounded-lg bg-neutral-900 text-white disabled:opacity-50" onClick={tryLogin} disabled={!pin || loading}>Войти</button>
        </div>
      </div>
    </div>
  );
}


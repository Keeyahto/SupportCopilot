"use client";
import React, { useEffect, useState } from "react";

export type ToastKind = "success" | "error" | "info";

export default function Toast({ message, kind = "info", onClose }: { message: string; kind?: ToastKind; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000);
    return () => clearTimeout(t);
  }, [onClose]);

  const bg = kind === "error" ? "bg-rose-600" : kind === "success" ? "bg-emerald-600" : "bg-neutral-800";

  return (
    <div className={`fixed bottom-4 right-4 text-white px-3 py-2 rounded-lg shadow ${bg}`}>{message}</div>
  );
}


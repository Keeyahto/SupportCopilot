"use client";
import React from "react";

export function ToolBadge({ label }: { label: "RAG" | "Tool-call" | "DB Tool" | "Escalation" }) {
  const color =
    label === "RAG" ? "badge-slate" :
    label === "Tool-call" ? "badge-indigo" :
    label === "DB Tool" ? "badge-emerald" :
    "badge-rose";
  return <span className={`badge ${color}`}>{label}</span>;
}

export default ToolBadge;


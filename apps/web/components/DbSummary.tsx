"use client";
import React, { useState } from "react";
import type { ToolInfo } from "../lib/types";

export default function DbSummary({ tool }: { tool: ToolInfo }) {
  const [openSql, setOpenSql] = useState(false);

  return (
    <div className="card mt-2">
      <div className="font-semibold mb-2">DB Tool</div>
      {tool.summary && (
        <div className="mb-2 text-sm text-neutral-800">{tool.summary}</div>
      )}

      {tool.sql && (
        <div className="mb-2">
          <button className="text-xs text-indigo-600 hover:underline" onClick={() => setOpenSql(!openSql)}>
            {openSql ? "Скрыть SQL" : "Показать SQL"}
          </button>
          {openSql && (
            <pre className="mt-1 text-xs bg-neutral-100 rounded p-2 overflow-x-auto"><code>{tool.sql}</code></pre>
          )}
        </div>
      )}

      {tool.rows && tool.rows.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="text-left text-neutral-600">
                {Object.keys(tool.rows[0]).map((k) => (
                  <th key={k} className="border-b p-1 pr-3 font-medium">{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tool.rows.slice(0, 20).map((row, i) => (
                <tr key={i} className="align-top">
                  {Object.keys(tool.rows![0]).map((k) => (
                    <td key={k} className="border-b p-1 pr-3 text-neutral-800">{String((row as any)[k])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {tool.rows.length > 20 && (
            <div className="text-[11px] text-neutral-500 mt-1">…и ещё {tool.rows.length - 20} строк</div>
          )}
        </div>
      )}

      <div className="text-[11px] text-neutral-500 mt-2">Данные из read-only БД (демо)</div>
    </div>
  );
}


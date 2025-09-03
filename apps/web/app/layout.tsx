import "./globals.css";
import React from "react";

export const metadata = {
  title: "Support Copilot",
  description: "RAG + Tools + DB Analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="min-h-screen flex flex-col">
        <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full px-4 py-6">
          {children}
        </div>
      </body>
    </html>
  );
}


"use client";
import React from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function HomePage() {
  return (
    <div className="flex-1 flex flex-col">
      <Header />
      <main className="flex-1">
        <section className="card">
          <h1 className="text-2xl font-bold mb-2">Support Copilot — RAG + Tools + DB-Analytics</h1>
          <p className="text-neutral-700">Демо ассистента уровня L2: RAG с цитатами, инструменты (заказы/доставка/тарифы) и NL→SQL аналитика в админ-режиме.</p>
        </section>
        <section className="grid sm:grid-cols-2 gap-4 mt-4">
          <div className="card">
            <div className="font-semibold mb-1">RAG с цитатами</div>
            <div className="text-sm text-neutral-700">Ответы с источниками и подсветкой релевантных фрагментов.</div>
          </div>
          <div className="card">
            <div className="font-semibold mb-1">Инструменты</div>
            <div className="text-sm text-neutral-700">Статус заказа, доставка, тарифы и другие tool-calls.</div>
          </div>
          <div className="card">
            <div className="font-semibold mb-1">Admin-аналитика</div>
            <div className="text-sm text-neutral-700">NL→SQL, сводки и таблицы из read-only БД.</div>
          </div>
          <div className="card">
            <div className="font-semibold mb-1">Telegram-бот</div>
            <div className="text-sm text-neutral-700">Лёгкая интеграция для поддержки в мессенджере.</div>
          </div>
        </section>
        <div className="mt-6">
          <a href="/demo" className="px-4 py-2 rounded-lg bg-neutral-900 text-white inline-block">Открыть демо-чат</a>
        </div>
      </main>
      <Footer />
    </div>
  );
}


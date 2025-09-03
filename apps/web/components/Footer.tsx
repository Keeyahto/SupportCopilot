"use client";
import React from "react";

export default function Footer() {
  return (
    <footer className="mt-8 text-xs text-neutral-500 text-center">
      © {new Date().getFullYear()} Support Copilot — Demo
    </footer>
  );
}


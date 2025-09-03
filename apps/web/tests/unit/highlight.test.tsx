import { describe, it, expect } from "vitest";
import React from "react";
import { mergeRanges, renderHighlighted } from "../../lib/highlight";

describe("highlight", () => {
  it("mergeRanges merges overlaps", () => {
    const merged = mergeRanges([
      [0, 3] as any,
      [2, 5] as any,
      [10, 12] as any,
    ]);
    expect(merged).toEqual([
      [0, 5],
      [10, 12],
    ]);
  });

  it("renderHighlighted returns spans and marks", () => {
    const snippet = "abcdef";
    const ranges = [
      [1, 3] as any, // bc
      [4, 5] as any, // e
    ];
    const nodes = renderHighlighted(snippet, ranges);
    // nodes: span('a'), mark('bc'), span('d'), mark('e'), span('f')
    expect(Array.isArray(nodes)).toBe(true);
    const tags = (nodes as any[]).map((n) => (React.isValidElement(n) ? (n.type as any) : "text"));
    expect(tags).toEqual(["span", "mark", "span", "mark", "span"]);
  });
});


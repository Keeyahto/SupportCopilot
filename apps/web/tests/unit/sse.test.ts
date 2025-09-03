import { describe, it, expect, vi } from "vitest";
import { parseEventStream } from "../../lib/sse";

function streamFromStrings(parts: string[]): ReadableStream<Uint8Array> {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      const enc = new TextEncoder();
      for (const p of parts) controller.enqueue(enc.encode(p));
      controller.close();
    },
  });
}

describe("parseEventStream", () => {
  it("parses context -> tokens* -> done", async () => {
    const events: Array<[string, string]> = [];
    const onEvent = vi.fn((e: string, d: string) => events.push([e, d]));
    const onClose = vi.fn();
    const onError = vi.fn();

    const payload =
      "event: context\r\n" +
      'data: {"sources":[],"labels":["RAG"]}\r\n' +
      "\r\n" +
      "event: token\n" +
      'data: {"t":"Hel"}\n' +
      "\n" +
      "event: token\n" +
      'data: {"t":"lo"}\n' +
      "\n" +
      "event: done\n" +
      'data: {"finish_reason":"stop"}\n' +
      "\n";

    const stream = streamFromStrings([payload.slice(0, 30), payload.slice(30)]);
    await parseEventStream(stream, { onEvent, onClose, onError });

    expect(onError).not.toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
    expect(onEvent).toHaveBeenCalledTimes(4);
    expect(events[0][0]).toBe("context");
    expect(JSON.parse(events[0][1]).labels).toEqual(["RAG"]);
    expect(events[1][0]).toBe("token");
    expect(JSON.parse(events[1][1]).t).toBe("Hel");
    expect(events[2][0]).toBe("token");
    expect(JSON.parse(events[2][1]).t).toBe("lo");
    expect(events[3][0]).toBe("done");
  });

  it("emits error event and closes", async () => {
    const onEvent = vi.fn();
    const onClose = vi.fn();
    const onError = vi.fn();
    const payload =
      "event: error\n" +
      'data: {"message":"boom"}\n' +
      "\n";
    const stream = streamFromStrings([payload]);
    await parseEventStream(stream, { onEvent, onClose, onError });
    expect(onEvent).toHaveBeenCalledWith("error", '{"message":"boom"}');
    expect(onClose).toHaveBeenCalled();
  });
});


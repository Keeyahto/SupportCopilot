import { describe, it, expect } from "vitest";
import { useUiStore } from "../../lib/store";

describe("store", () => {
  it("initial state and toggles", () => {
    const s = useUiStore.getState();
    expect(["faq", "orders", "policies", "admin"]).toContain(s.mode);
    expect(["ru", "en"]).toContain(s.lang);
    expect(s.strict).toBe(false);

    useUiStore.getState().setMode("orders");
    expect(useUiStore.getState().mode).toBe("orders");

    useUiStore.getState().setStrict(true);
    expect(useUiStore.getState().strict).toBe(true);
  });

  it("admin key flow", () => {
    const store = useUiStore.getState();
    store.setAdmin("1234");
    expect(useUiStore.getState().isAdmin).toBe(true);
    expect(useUiStore.getState().adminKey).toBe("1234");
    store.clearAdmin();
    expect(useUiStore.getState().isAdmin).toBe(false);
    expect(useUiStore.getState().adminKey).toBeUndefined();
  });

  it("messages push and update last assistant", () => {
    const store = useUiStore.getState();
    store.resetDialog();
    store.pushMessage({ id: "1", role: "user", text: "hi", ts: Date.now() });
    store.pushMessage({ id: "2", role: "assistant", text: "", ts: Date.now() });
    expect(useUiStore.getState().messages).toHaveLength(2);

    store.updateLastAssistant({ text: "hello" });
    const msgs = useUiStore.getState().messages;
    expect(msgs[msgs.length - 1].text).toBe("hello");
  });
});


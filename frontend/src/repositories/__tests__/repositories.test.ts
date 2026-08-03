import { describe, it, expect, vi } from "vitest";
import { SystemRepository } from "../SystemRepository";
import { AuthRepository } from "../AuthRepository";
import { mapIPCErrorToMessage } from "../../api/errors";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(async (_cmd: string, args: { payload: string }) => {
    const payload = JSON.parse(args.payload);
    if (payload.method === "system.ping") {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: payload.id,
        result: { success: true, data: { status: "ok", version: "1.0" } },
      });
    }
    if (payload.method === "auth.unlock") {
      if (payload.params.masterPassword === "correct") {
        return JSON.stringify({
          jsonrpc: "2.0",
          id: payload.id,
          result: { success: true, data: { success: true } },
        });
      } else {
        return JSON.stringify({
          jsonrpc: "2.0",
          id: payload.id,
          result: {
            success: false,
            error: { code: "AUTH_INVALID_PASSWORD", message: "Invalid password" },
          },
        });
      }
    }
    return JSON.stringify({ jsonrpc: "2.0", id: payload.id, result: { success: true, data: {} } });
  }),
}));

describe("Repository & API Client Unit Tests", () => {
  it("SystemRepository.ping returns ok status", async () => {
    const res = await SystemRepository.ping();
    expect(res.success).toBe(true);
    if (res.success) {
      expect(res.data.status).toBe("ok");
    }
  });

  it("AuthRepository.unlock returns success for valid password", async () => {
    const res = await AuthRepository.unlock("correct");
    expect(res.success).toBe(true);
  });

  it("AuthRepository.unlock returns mapped error message for invalid password", async () => {
    const res = await AuthRepository.unlock("wrong");
    expect(res.success).toBe(false);
    if (!res.success) {
      const userMessage = mapIPCErrorToMessage(res.error);
      expect(userMessage).toBe("Invalid master password. Please try again.");
    }
  });
});

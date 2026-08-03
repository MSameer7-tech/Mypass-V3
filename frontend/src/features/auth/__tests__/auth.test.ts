import { describe, it, expect, beforeEach, vi } from "vitest";
import { useAuthStore } from "../../../stores/auth/useAuthStore";

vi.mock("../../../repositories/AuthRepository", () => ({
  AuthRepository: {
    status: vi.fn(async () => ({ success: true, data: { sessionState: "LOCKED" } })),
    unlock: vi.fn(async (pwd: string) => {
      if (pwd === "correct") return { success: true, data: { success: true } };
      return { success: false, error: { code: "AUTH_INVALID_PASSWORD", message: "Invalid password" } };
    }),
    lock: vi.fn(async () => ({ success: true, data: { success: true } })),
  },
}));

describe("Authentication & Session Lifecycle Integration Tests", () => {
  beforeEach(() => {
    useAuthStore.setState({
      sessionState: "BOOTING",
      authError: null,
      autoLockMinutes: 15,
    });
  });

  it("checkVaultStatus transitions BOOTING -> LOCKED", async () => {
    await useAuthStore.getState().checkVaultStatus();
    expect(useAuthStore.getState().sessionState).toBe("LOCKED");
  });

  it("unlockVault with correct password transitions LOCKED -> UNLOCKED", async () => {
    const success = await useAuthStore.getState().unlockVault("correct");
    expect(success).toBe(true);
    expect(useAuthStore.getState().sessionState).toBe("UNLOCKED");
  });

  it("unlockVault with wrong password stays LOCKED and sets authError", async () => {
    const success = await useAuthStore.getState().unlockVault("wrong");
    expect(success).toBe(false);
    expect(useAuthStore.getState().sessionState).toBe("LOCKED");
    expect(useAuthStore.getState().authError).toBe("Invalid password");
  });

  it("lockVault transitions UNLOCKED -> LOCKED", () => {
    useAuthStore.setState({ sessionState: "UNLOCKED" });
    useAuthStore.getState().lockVault();
    expect(useAuthStore.getState().sessionState).toBe("LOCKED");
  });
});

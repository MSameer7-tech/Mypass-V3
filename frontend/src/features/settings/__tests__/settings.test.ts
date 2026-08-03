import { describe, it, expect, vi } from "vitest";
import { useSettingsStore } from "../../../stores/settings/useSettingsStore";
import { BackupRepository } from "../../../repositories/BackupRepository";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(async (_cmd: string, args: { payload: string }) => {
    const payload = JSON.parse(args.payload);
    if (payload.method === "backup.export") {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: payload.id,
        result: {
          success: true,
          data: { filename: "backup.json", payload: "[]", itemCount: 0 },
        },
      });
    }
    if (payload.method === "backup.import") {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: payload.id,
        result: {
          success: true,
          data: { importedCount: 2 },
        },
      });
    }
    return JSON.stringify({ jsonrpc: "2.0", id: payload.id, result: { success: true, data: {} } });
  }),
}));

describe("Preferences & Backup Integration Tests", () => {
  it("useSettingsStore updates preferences state", () => {
    useSettingsStore.getState().setTheme("light");
    useSettingsStore.getState().setAutoLockMinutes(30);
    useSettingsStore.getState().setClipboardAutoClearSeconds(60);

    expect(useSettingsStore.getState().theme).toBe("light");
    expect(useSettingsStore.getState().autoLockMinutes).toBe(30);
    expect(useSettingsStore.getState().clipboardAutoClearSeconds).toBe(60);
  });

  it("BackupRepository.exportVault returns exported JSON payload", async () => {
    const res = await BackupRepository.exportVault("json");
    expect(res.success).toBe(true);
    if (res.success) {
      expect(res.data.filename).toBe("backup.json");
    }
  });

  it("BackupRepository.importVault imports entries successfully", async () => {
    const res = await BackupRepository.importVault("[]");
    expect(res.success).toBe(true);
    if (res.success) {
      expect(res.data.importedCount).toBe(2);
    }
  });
});

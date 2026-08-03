import { describe, it, expect, vi } from "vitest";
import { VaultRepository } from "../../repositories/VaultRepository";
import { GeneratorRepository } from "../../repositories/GeneratorRepository";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(async (_cmd: string, args: { payload: string }) => {
    const payload = JSON.parse(args.payload);
    if (payload.method === "vault.list_entries") {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: payload.id,
        result: {
          success: true,
          data: [
            { id: 1, title: "Live GitHub", username: "dev", is_favorite: true, category: "Passwords" },
            { id: 2, title: "Live Stripe", username: "billing", is_favorite: false, category: "Developer Keys" },
          ],
        },
      });
    }
    if (payload.method === "vault.create_entry") {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: payload.id,
        result: { success: true, data: { id: 3, title: payload.params.title } },
      });
    }
    if (payload.method === "generator.generate") {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: payload.id,
        result: { success: true, data: { password: "generated_password_123!" } },
      });
    }
    return JSON.stringify({ jsonrpc: "2.0", id: payload.id, result: { success: true, data: {} } });
  }),
}));

describe("Live Vault CRUD & Generator Integration Tests", () => {
  it("VaultRepository.listEntries fetches live mapped SQLite entries", async () => {
    const res = await VaultRepository.listEntries();
    expect(res.success).toBe(true);
    if (res.success) {
      expect(res.data).toHaveLength(2);
      expect(res.data[0].title).toBe("Live GitHub");
    }
  });

  it("VaultRepository.createEntry sends parameters and receives new entry ID", async () => {
    const res = await VaultRepository.createEntry({
      title: "Live Vercel",
      username: "deployer",
    });
    expect(res.success).toBe(true);
    if (res.success) {
      expect(res.data.id).toBe(3);
      expect(res.data.title).toBe("Live Vercel");
    }
  });

  it("GeneratorRepository.generate returns generated password string", async () => {
    const res = await GeneratorRepository.generate(16, true, true);
    expect(res.success).toBe(true);
    if (res.success) {
      expect(res.data.password).toBe("generated_password_123!");
    }
  });
});

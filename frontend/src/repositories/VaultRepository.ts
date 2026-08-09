import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";
import { VaultEntryDTO, mapDTOToVaultEntry } from "../mappers/vaultMapper";
import { MockVaultEntry } from "../mocks/vault";
import { z } from "zod";

const EntrySchema = z.object({
  title: z.string().min(1, "Title is required").max(100),
  username: z.string().max(100).optional().default(""),
  password: z.string().max(1024).optional().default(""),
  websiteUrl: z.string().max(500).optional().default(""),
  notes: z.string().max(5000).optional().default(""),
  category: z.string().max(50).optional().default("Passwords"),
  favorite: z.boolean().optional().default(false),
});

const UpdateEntrySchema = EntrySchema.partial().extend({
  id: z.number().int().positive(),
});

export class VaultRepository {
  static async listEntries(): Promise<Result<MockVaultEntry[]>> {
    const res = await sendIPCRequest<VaultEntryDTO[]>("vault.list_entries");

    if (res.success) {
      const domainEntries = res.data.map(mapDTOToVaultEntry);
      return { success: true, data: domainEntries };
    }

    return res;
  }

  static async createEntry(entry: {
    title: string;
    username: string;
    password?: string;
    websiteUrl?: string;
    notes?: string;
    category?: string;
    favorite?: boolean;
  }): Promise<Result<{ id: number; title: string }>> {
    const parsed = EntrySchema.safeParse(entry);
    if (!parsed.success) {
      return { success: false, error: { message: "Invalid payload: " + parsed.error.errors[0].message, code: "VALIDATION_ERROR" } };
    }
    const data = parsed.data;
    
    return sendIPCRequest<{ id: number; title: string }>("vault.create_entry", {
      title: data.title,
      username: data.username,
      password: data.password,
      website_url: data.websiteUrl,
      notes: data.notes,
      category: data.category,
      favorite: data.favorite,
    });
  }

  static async updateEntry(
    id: number,
    updates: Partial<MockVaultEntry>
  ): Promise<Result<{ success: boolean }>> {
    const parsed = UpdateEntrySchema.safeParse({ id, ...updates });
    if (!parsed.success) {
      return { success: false, error: { message: "Invalid payload: " + parsed.error.errors[0].message, code: "VALIDATION_ERROR" } };
    }
    const data = parsed.data;

    return sendIPCRequest<{ success: boolean }>("vault.update_entry", {
      id: data.id,
      title: data.title,
      username: data.username,
      password: data.password,
      website_url: data.websiteUrl,
      notes: data.notes,
      category: data.category,
      favorite: data.favorite,
    });
  }

  static async deleteEntry(id: number): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("vault.delete_entry", { id });
  }

  static async toggleFavorite(id: number): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("vault.toggle_favorite", { id });
  }
}

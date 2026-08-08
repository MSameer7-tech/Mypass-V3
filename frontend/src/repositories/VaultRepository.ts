import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";
import { VaultEntryDTO, mapDTOToVaultEntry } from "../mappers/vaultMapper";
import { MockVaultEntry } from "../mocks/vault";

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
    return sendIPCRequest<{ id: number; title: string }>("vault.create_entry", {
      title: entry.title,
      username: entry.username,
      password: entry.password,
      website_url: entry.websiteUrl,
      notes: entry.notes,
      category: entry.category,
      favorite: entry.favorite,
    });
  }

  static async updateEntry(
    id: number,
    updates: Partial<MockVaultEntry>
  ): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("vault.update_entry", {
      id,
      title: updates.title,
      username: updates.username,
      password: updates.password,
      website_url: updates.websiteUrl,
      notes: updates.notes,
    });
  }

  static async deleteEntry(id: number): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("vault.delete_entry", { id });
  }

  static async toggleFavorite(id: number): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("vault.toggle_favorite", { id });
  }
}

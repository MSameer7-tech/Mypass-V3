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

  static async deleteEntry(id: number): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("vault.delete_entry", { id });
  }
}

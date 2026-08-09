import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";

export interface ExportData {
  filename: string;
  payload: string;
  itemCount: number;
}

export class BackupRepository {
  static async exportVault(format: "json" | "mypass" = "mypass"): Promise<Result<ExportData>> {
    return sendIPCRequest<ExportData>("backup.export", { format });
  }

  static async importVault(payload: string): Promise<Result<{ importedCount: number }>> {
    return sendIPCRequest<{ importedCount: number }>("backup.import", { payload });
  }
}
